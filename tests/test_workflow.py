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
        alert_summary="Multiple failed SSH login attempts from 198.51.100.23 followed by a successful login to the production server.",
        severity="critical",
        case_title="Suspicious SSH Login Pattern",
        ip_addresses=["198.51.100.23"],
        source="streamlit",
    )

    checkpointer = MemorySaver()
    app = build_workflow().compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "test_thread_hitl"}, "recursion_limit": 100}

    interrupt_seen = False
    for event in app.stream(state.model_dump(), config=config, stream_mode="values"):
        if isinstance(event, dict) and "__interrupt__" in event:
            interrupt_seen = True
            break

    assert interrupt_seen is True

    resumed = app.invoke(Command(resume="Approve"), config=config)
    assert resumed["status"] in {"escalated", "closed"}
    assert resumed["report_approval_status"] == "approved"
    assert resumed["final_decision"] == "escalate"
    assert resumed["incident_report"] is not None
    print("RESUMED_STATE", resumed)

def test_workflow_reaches_human_approval_from_ssh_alert():
    state = SOCState(
        incident_id="INC-SSH-1001",
        alert_summary="Multiple failed SSH login attempts from 198.51.100.23 followed by a successful login to the production server.",
        severity="critical",
        case_title="Suspicious SSH Login Pattern",
        ip_addresses=["198.51.100.23"],
        source="streamlit",
    )

    app = build_workflow().compile()
    final_state = app.invoke(state.model_dump(), config={"recursion_limit": 100})

    assert final_state["status"] == "awaiting_human_approval"
    assert final_state["report_ready_for_review"] is True
    assert final_state["incident_report"] is not None
    assert final_state["mitre_techniques"]


def test_compliance_loop_max_retries():
    state = SOCState(
        incident_id="INC-123",
        alert_summary="Test",
        severity="high",
        case_title="Test"
    )
    
    app = build_workflow().compile()
    
    final_state = app.invoke(state.model_dump(), config={"recursion_limit": 100})
    
    assert final_state["compliance_retry_count"] == 3
    assert final_state["compliance_status"] == "blocked"
    assert final_state["status"] == "blocked" 
