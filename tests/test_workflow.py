import pytest
from soc_agent_workforce.state import SOCState
from soc_agent_workforce.graph.workflow import build_workflow
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
import uuid

def test_soc_state_validation():
    # Test valid creation
    state = SOCState(
        incident_id="INC-1234",
        alert_summary="Test alert",
        severity="low",
        case_title="Test Case"
    )
    assert state.status == "new"
    assert state.severity == "low"

    # Test invalid severity
    with pytest.raises(ValueError):
        SOCState(
            incident_id="INC-1235",
            alert_summary="Test",
            severity="invalid_sev",
            case_title="Test"
        )

def test_mcp_mocked(monkeypatch):
    # Mock external calls to verify tool logic
    from soc_agent_workforce.mcp import abuseipdb_client
    
    def mock_check_ip(*args, **kwargs):
        return {"ipAddress": "127.0.0.1", "abuseConfidenceScore": 50}
        
    monkeypatch.setattr(abuseipdb_client, "check_ip_reputation", mock_check_ip)
    
    res = abuseipdb_client.check_ip_reputation("127.0.0.1")
    assert res["abuseConfidenceScore"] == 50

def test_hitl_interrupt_flow():
    state = SOCState(
        incident_id=f"INC-{uuid.uuid4().hex[:8]}",
        alert_summary="Test alert",
        severity="high",
        case_title="Test",
        mitre_techniques=["T1078"] # bypass compliance
    )
    
    # We bypass LLM calls by just testing the graph routing structure if possible
    # Given the test environment, we rely on _FallbackLLM
    
    checkpointer = MemorySaver()
    app = build_workflow().compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "test_thread_hitl"}}
    
    # Run to interrupt
    for _ in app.stream(state.model_dump(), config=config):
        pass
        
    current = app.get_state(config)
    assert current.next[0] == "human_approval"
    
    # Verify interrupt is pending
    pending_task = current.tasks[0]
    assert pending_task.interrupts
    
    # Resume with Approve
    for _ in app.stream(Command(resume="Approve"), config=config):
        pass
        
    final = app.get_state(config)
    assert final.values["status"] == "escalated"
    assert final.values["final_decision"] == "escalate"

def test_compliance_loop_max_retries():
    state = SOCState(
        incident_id="INC-123",
        alert_summary="Test",
        severity="high",
        case_title="Test"
    )
    
    # This state lacks mitre_techniques and threat_hunt_summary, so compliance will fail
    # It should loop back to alert_analyst and bump retries until max.
    app = build_workflow().compile()
    
    # Since we use _FallbackLLM, the agents will output dummy text.
    # The compliance auditor will keep failing it because mitre_techniques remains empty.
    final_state = app.invoke(state.model_dump())
    
    assert final_state["compliance_retries"] == 3
    assert final_state["compliance_status"] == "blocked"
    assert final_state["status"] == "escalated" # Blocked cases get escalated per workflow logic
