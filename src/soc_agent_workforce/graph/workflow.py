from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

from soc_agent_workforce.agents.alert_analyst import AlertAnalystAgent
from soc_agent_workforce.agents.compliance_auditor import ComplianceAuditorAgent
from soc_agent_workforce.agents.incident_reporter import IncidentReporterAgent
from soc_agent_workforce.agents.soc_manager import SocManagerAgent
from soc_agent_workforce.agents.threat_hunter import ThreatHunterAgent
from soc_agent_workforce.state import SOCState

import json


class WorkflowState(SOCState):
    """
    Workflow-specific state.

    Keeps track of how many times the human reviewer has
    rejected/requested a revision of the incident report.
    """

    approval_retry_count: int = 0
    approval_max_retries: int = 3


def _route_after_hunter(state: SOCState) -> str:
    """
    Decide where to go after the Threat Hunter.

    If self-healing was rejected and retries remain,
    send the case back to the Alert Analyst.

    Otherwise continue to Compliance Auditor.
    """

    if state.status in {"blocked", "closed", "escalated", "hold"}:
        return END

    if state.self_healing_status == "max_retries_reached" or state.self_healing_retry_count >= state.self_healing_max_retries:
        state.self_healing_status = "max_retries_reached"
        state.status = "triaged"
        state.notes.append(
            "Threat Hunter retries exhausted; "
            "forcing case through to compliance review."
        )
        return "compliance_auditor"

    if state.self_healing_status == "rejected":
        if state.self_healing_retry_count < state.self_healing_max_retries:
            state.status = "revision_requested"
            state.notes.append(
                f"Threat Hunter rejected the triage; routing back to Alert Analyst "
                f"(attempt {state.self_healing_retry_count}/{state.self_healing_max_retries})."
            )
            return "alert_analyst"

        state.self_healing_status = "max_retries_reached"
        state.status = "triaged"
        state.notes.append(
            "Threat Hunter retries exhausted; "
            "forcing case through to compliance review."
        )
        return "compliance_auditor"

    return "compliance_auditor"


def _route_after_compliance(state: SOCState) -> str:
    """
    Decide where to go after Compliance Auditor.

    Failed compliance can retry through the Alert Analyst,
    but only up to the configured maximum.
    """

    if state.status in {"blocked", "closed", "escalated", "hold"}:
        return END

    if state.compliance_status == "blocked" or state.compliance_retry_count >= state.compliance_max_retries:
        state.compliance_status = "blocked"
        state.status = "blocked"
        state.notes.append(
            "Compliance retry cap reached; "
            "workflow blocked until the case is manually corrected."
        )
        return END

    if state.compliance_status == "failed":
        state.status = "needs_revision"
        state.reviewer_feedback = (
            "Compliance failed. Fix the missing required fields "
            "before re-running validation."
        )
        state.notes.append(
            f"Compliance failed. Routing back to Alert Analyst "
            f"for remediation "
            f"(attempt {state.compliance_retry_count + 1}/"
            f"{state.compliance_max_retries})."
        )
        return "alert_analyst"

    if state.compliance_status == "passed":
        return "incident_reporter"

    return END


def _print_final_report(state: SOCState) -> SOCState:
    """
    Print the final incident report.
    """

    print("\n" + "=" * 50)
    print("FINAL REPORT ASSEMBLED")
    print("=" * 50)

    print(f"Status: {state.status}")

    print("Incident Report:")

    if state.incident_report:
        print(json.dumps(state.incident_report, indent=2))
    else:
        print("None")

    print("=" * 50 + "\n")

    return state


def human_approval_checkpoint(state: SOCState) -> SOCState:
    """
    Pause the workflow and request human approval.

    Possible actions:
        Approve
        Reject
        Hold
    """

    action = interrupt(
        {
            "message": "Approval required. Please review the incident report.",
            "report": state.incident_report,
        }
    )

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

    else:

        state.status = "blocked"

        state.notes.append(
            f"Unknown HITL decision received: {action}. "
            "Blocking workflow for safety."
        )

    state.notes.append(f"HITL Decision: {action}")

    return state


def _route_after_approval(state: WorkflowState) -> str:
    """
    Decide what happens after human approval.

    Approved:
        END

    Rejected:
        Return to Alert Analyst, but only up to the
        configured approval retry limit.

    Hold:
        END for now.
    """

    if state.status in {"blocked", "closed", "escalated", "hold"}:
        return END

    if state.status == "revision_requested":

        state.approval_retry_count += 1

        state.notes.append(
            f"Human approval requested revision. "
            f"Attempt {state.approval_retry_count}/"
            f"{state.approval_max_retries}."
        )

        if state.approval_retry_count >= state.approval_max_retries:

            state.status = "blocked"

            state.notes.append(
                "Maximum human approval revision attempts reached; "
                "workflow blocked."
            )

            return END

        return "alert_analyst"

    return END


def build_workflow() -> StateGraph:
    """
    Build and return the SOC agent workflow.
    """

    workflow = StateGraph(WorkflowState)

    # ---------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------

    workflow.add_node(
        "soc_manager",
        lambda state: SocManagerAgent().run(state),
    )

    workflow.add_node(
        "alert_analyst",
        lambda state: AlertAnalystAgent().run(state),
    )

    workflow.add_node(
        "threat_hunter",
        lambda state: ThreatHunterAgent().run(state),
    )

    workflow.add_node(
        "compliance_auditor",
        lambda state: ComplianceAuditorAgent().run(state),
    )

    workflow.add_node(
        "incident_reporter",
        lambda state: IncidentReporterAgent().run(state),
    )

    workflow.add_node(
        "human_approval",
        human_approval_checkpoint,
    )

    workflow.add_node(
        "print_report",
        _print_final_report,
    )

    # ---------------------------------------------------------
    # Starting point
    # ---------------------------------------------------------

    workflow.set_entry_point("soc_manager")

    # ---------------------------------------------------------
    # SOC Manager → Alert Analyst
    # ---------------------------------------------------------

    workflow.add_edge(
        "soc_manager",
        "alert_analyst",
    )

    # ---------------------------------------------------------
    # Alert Analyst → Threat Hunter
    # ---------------------------------------------------------

    workflow.add_edge(
        "alert_analyst",
        "threat_hunter",
    )

    # ---------------------------------------------------------
    # Threat Hunter routing
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "threat_hunter",
        _route_after_hunter,
        {
            "alert_analyst": "alert_analyst",
            "compliance_auditor": "compliance_auditor",
        },
    )

    # ---------------------------------------------------------
    # Compliance routing
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "compliance_auditor",
        _route_after_compliance,
        {
            "alert_analyst": "alert_analyst",
            "incident_reporter": "incident_reporter",
            END: END,
        },
    )

    # ---------------------------------------------------------
    # Incident Reporter → Print Report
    # ---------------------------------------------------------

    workflow.add_edge(
        "incident_reporter",
        "print_report",
    )

    # ---------------------------------------------------------
    # Print Report → Human Approval
    # ---------------------------------------------------------

    workflow.add_edge(
        "print_report",
        "human_approval",
    )

    # ---------------------------------------------------------
    # Human Approval routing
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "human_approval",
        _route_after_approval,
        {
            "alert_analyst": "alert_analyst",
            END: END,
        },
    )

    return workflow
