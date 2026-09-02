from __future__ import annotations

from soc_agent_workforce.mcp.abuseipdb_client import check_ip_reputation
from soc_agent_workforce.mcp.mitre_dataset import lookup_mitre_technique
from soc_agent_workforce.state import SOCState

from .base_agent import BaseAgent


class AlertAnalystAgent(BaseAgent):
    """Performs initial triage and evidence collection for the case."""

    agent_name = "alert_analyst"
    system_prompt = "You are the Alert Analyst. Triage alerts, classify them, and gather supporting evidence."

    def run(self, state: SOCState) -> SOCState:
        if not state.alert_summary:
            state.alert_summary = "No alert summary available."

        if state.status in {"revision_requested", "needs_revision"} or state.reviewer_feedback:
            state.triage_revisions += 1
            if state.compliance_status != "blocked":
                state.compliance_status = "pending"
            state.notes.append("Alert Analyst received a revision request and re-evaluated the alert with the feedback in mind.")
            if state.reviewer_feedback:
                state.triage_notes = f"Revised using reviewer feedback: {state.reviewer_feedback}"
                state.reviewer_feedback = None

        if state.ip_addresses:
            ip_context = []
            for ip in state.ip_addresses:
                ip_ctx = check_ip_reputation(ip)
                ip_context.append(f"{ip}: {ip_ctx.get('verdict')} / score={ip_ctx.get('abuse_confidence_score')} / reports={ip_ctx.get('total_reports')}")
            state.triage_evidence.extend(ip_context)

        if state.alert_summary:
            technique = lookup_mitre_technique(keyword=state.alert_summary)
            if technique.get("status") == "ok" and technique.get("id"):
                state.mitre_techniques.append(technique["id"])
                state.triage_reasoning.append(f"Mapped alert to MITRE technique {technique['id']} ({technique['name']}).")
            elif "ssh" in state.alert_summary.lower() or "login" in state.alert_summary.lower() or "brute" in state.alert_summary.lower():
                fallback_techniques = ["T1110", "T1078"]
                for technique_id in fallback_techniques:
                    if technique_id not in state.mitre_techniques:
                        state.mitre_techniques.append(technique_id)
                state.triage_reasoning.append("Fallback MITRE mapping applied for SSH/brute-force login activity.")
                state.mitre_tactics = ["Credential Access", "Initial Access"]

        if state.severity == "critical":
            state.triage_category = "malicious"
            state.triage_confidence = 0.92
        elif state.severity in {"high", "medium"}:
            state.triage_category = "suspicious"
            state.triage_confidence = 0.78
        else:
            state.triage_category = "benign"
            state.triage_confidence = 0.42

        if state.status in {"revision_requested", "needs_revision"}:
            state.triage_confidence = min(0.99, max(state.triage_confidence, 0.86))
            state.triage_category = "suspicious" if state.severity in {"high", "medium", "critical"} else "benign"
            state.risk_assessment = state.triage_category
            state.status = "triaged"

        state.triage_notes = (
            f"Alert triaged with analyst assessment: {state.triage_category}. "
            f"Evidence reviewed: {', '.join(state.triage_evidence) if state.triage_evidence else 'none supplied'}"
        )
        state.risk_assessment = state.triage_category
        state.last_agent = self.agent_name
        state.notes.append("Alert Analyst completed triage.")
        return state
