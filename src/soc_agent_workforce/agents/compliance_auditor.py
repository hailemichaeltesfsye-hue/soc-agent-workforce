from __future__ import annotations

from soc_agent_workforce.state import SOCState

from .base_agent import BaseAgent


class ComplianceAuditorAgent(BaseAgent):
    """Validates that the case has required information before report generation."""

    agent_name = "compliance_auditor"
    system_prompt = "You are the Compliance Auditor. Ensure required fields are present before moving forward."

    def run(self, state: SOCState) -> SOCState:
        required_fields = {
            "incident_id": lambda s: bool(s.incident_id),
            "alert_summary": lambda s: bool(s.alert_summary and s.alert_summary.strip()),
            "severity": lambda s: bool(s.severity),
            "triage_category": lambda s: bool(s.triage_category),
            "risk_assessment": lambda s: bool(s.risk_assessment),
            "mitre_techniques": lambda s: bool(s.mitre_techniques),
            "threat_hunt_summary": lambda s: bool(s.threat_hunt_summary and s.threat_hunt_summary.strip()),
            "triage_evidence": lambda s: bool(s.triage_evidence or s.ip_addresses),
            "final_summary": lambda s: bool(s.final_summary and s.final_summary.strip()),
        }

        missing = []
        compliance_findings: list[str] = []

        for field_name, validator in required_fields.items():
            if not validator(state):
                missing.append(field_name)
                if field_name == "mitre_techniques":
                    compliance_findings.append("MITRE mapping is empty; add at least one technique identifier.")
                elif field_name == "triage_evidence":
                    compliance_findings.append("No evidence is attached; include triage evidence or IP reputation context.")
                elif field_name == "final_summary":
                    compliance_findings.append("Final summary is missing; add a concise incident conclusion.")
                else:
                    compliance_findings.append(f"Missing required field: {field_name}")

        state.required_fields_present = not missing
        state.required_fields_missing = missing
        state.compliance_findings = compliance_findings

        if missing:
            state.compliance_status = "failed"
            state.status = "needs_revision"
            state.report_ready_for_review = False
            if state.compliance_retry_count >= state.compliance_max_retries:
                state.compliance_status = "blocked"
                state.status = "blocked"
                state.compliance_findings.append(
                    "Compliance retry cap exceeded; escalate to manual review or fix the state before continuing."
                )
        else:
            state.compliance_status = "passed"
            state.report_ready_for_review = True
            state.status = "triaged"
            state.required_fields_missing = []
            state.compliance_findings = ["All required fields for compliance are present."]

        state.last_agent = self.agent_name
        state.notes.append("Compliance Auditor completed validation.")
        return state
