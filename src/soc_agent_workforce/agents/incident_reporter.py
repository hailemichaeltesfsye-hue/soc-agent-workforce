from __future__ import annotations

from soc_agent_workforce.state import SOCState

from .base_agent import BaseAgent


class IncidentReporterAgent(BaseAgent):
    """Builds the final structured incident report package."""

    agent_name = "incident_reporter"
    system_prompt = "You are the Incident Reporter. Build a clear final incident report for human review."

    def run(self, state: SOCState) -> SOCState:
        # Build the structured incident_report object per PLAN.md section 3
        # Pulling from triage_notes, threat_hunt_summary, mitre_techniques, severity, final_summary, evidence_links, risk_assessment.
        state.incident_report = {
            "case_title": state.case_title or f"Incident: {state.incident_id}",
            "executive_summary": state.final_summary or state.alert_summary,
            "severity": state.severity,
            "severity_justification": state.risk_assessment,
            "mitre_attack_mapping": state.mitre_techniques,
            "timeline_and_evidence": {
                "triage_notes": state.triage_notes,
                "evidence_links": state.evidence_links,
                "threat_hunt_summary": state.threat_hunt_summary
            },
            "recommended_remediation": "Review affected endpoints and isolate if necessary. Update firewall rules to block suspicious IPs." # Placeholder for remediation
        }
        
        state.report_ready_for_review = True
        state.report_approval_status = "pending"
        
        # Step 7 requirements: set status to awaiting_human_approval
        state.status = "awaiting_human_approval"
        state.last_agent = self.agent_name
        state.notes.append("Incident Reporter assembled the final report structure.")
        return state
