from __future__ import annotations

from langgraph.graph import StateGraph

from soc_agent_workforce.agents.alert_analyst import AlertAnalystAgent
from soc_agent_workforce.agents.compliance_auditor import ComplianceAuditorAgent
from soc_agent_workforce.agents.incident_reporter import IncidentReporterAgent
from soc_agent_workforce.agents.soc_manager import SocManagerAgent
from soc_agent_workforce.agents.threat_hunter import ThreatHunterAgent
from soc_agent_workforce.state import SOCState
from langgraph.types import interrupt
import json


class WorkflowState(SOCState):
    pass


def _route_after_hunter(state: SOCState) -> str:
    if state.self_healing_status == "rejected":
        if state.self_healing_retry_count < 3:
            state.status = "revision_requested"
            return "alert_analyst"
        state.status = "triaged"
        state.notes.append("Threat Hunter retries exhausted; forcing case through to compliance review.")
        return "compliance_auditor"
    return "compliance_auditor"


def _route_after_compliance(state: SOCState) -> str:
    if state.compliance_status == "failed":
        state.compliance_retry_count += 1
        state.notes.append(
            f"Compliance failed. Routing back to Alert Analyst for remediation (attempt {state.compliance_retry_count}/{state.compliance_max_retries})."
        )
        if state.compliance_retry_count >= state.compliance_max_retries:
            state.compliance_status = "blocked"
            state.status = "blocked"
            state.notes.append("Compliance retry cap reached; workflow blocked until the case is manually corrected.")
            return "__end__"
        state.status = "needs_revision"
        state.reviewer_feedback = "Compliance failed. Fix the missing required fields before re-running validation."
        return "alert_analyst"
    if state.compliance_status == "passed":
        return "incident_reporter"
    return "__end__"


def _print_final_report(state: SOCState) -> SOCState:
    print("\n" + "="*50)
    print("FINAL REPORT ASSEMBLED")
    print("="*50)
    print(f"Status: {state.status}")
    print("Incident Report:")
    if state.incident_report:
        print(json.dumps(state.incident_report, indent=2))
    else:
        print("None")
    print("="*50 + "\n")
    return state


def human_approval_checkpoint(state: SOCState) -> SOCState:
    action = interrupt({
        "message": "Approval required. Please review the incident report.",
        "report": state.incident_report
    })
    
    if action == "Approve":
        state.report_approval_status = "approved"
        state.final_decision = "escalate" 
        state.status = "escalated"
    elif action == "Reject":
        state.report_approval_status = "rejected"
        state.final_decision = "request_revision"
        state.status = "revision_requested"
    elif action == "Hold":
        state.status = "hold"
        
    state.notes.append(f"HITL Decision: {action}")
    return state


def _route_after_approval(state: SOCState) -> str:
    if state.status == "revision_requested":
        return "alert_analyst"
    return "__end__"


def build_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)

    workflow.add_node("soc_manager", lambda state: SocManagerAgent().run(state))
    workflow.add_node("alert_analyst", lambda state: AlertAnalystAgent().run(state))
    workflow.add_node("threat_hunter", lambda state: ThreatHunterAgent().run(state))
    workflow.add_node("compliance_auditor", lambda state: ComplianceAuditorAgent().run(state))
    workflow.add_node("incident_reporter", lambda state: IncidentReporterAgent().run(state))
    workflow.add_node("human_approval", human_approval_checkpoint)
    workflow.add_node("print_report", _print_final_report)

    workflow.set_entry_point("soc_manager")
    workflow.add_edge("soc_manager", "alert_analyst")
    workflow.add_edge("alert_analyst", "threat_hunter")
    workflow.add_conditional_edges(
        "threat_hunter",
        _route_after_hunter,
        {
            "alert_analyst": "alert_analyst",
            "compliance_auditor": "compliance_auditor",
        },
    )
    workflow.add_conditional_edges(
        "compliance_auditor",
        _route_after_compliance,
        {
            "alert_analyst": "alert_analyst",
            "incident_reporter": "incident_reporter",
            "__end__": "__end__",
        },
    )
    
    workflow.add_edge("incident_reporter", "print_report")
    workflow.add_edge("print_report", "human_approval")
    
    workflow.add_conditional_edges(
        "human_approval",
        _route_after_approval,
        {
            "alert_analyst": "alert_analyst",
            "__end__": "__end__",
        }
    )

    return workflow
