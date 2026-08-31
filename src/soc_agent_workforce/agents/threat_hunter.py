from __future__ import annotations

from soc_agent_workforce.state import SOCState

from .base_agent import BaseAgent


class ThreatHunterAgent(BaseAgent):
    """Reviews triage quality and adds threat-hunting context."""

    agent_name = "threat_hunter"
    system_prompt = "You are the Threat Hunter. Critique triage quality and add hunting findings."

    def run(self, state: SOCState) -> SOCState:
        hunter_findings = []
        is_weak = (
            not state.alert_summary
            or len(state.alert_summary.split()) < 12
            or len(state.ip_addresses) == 0
            or state.triage_confidence is None
            or state.triage_confidence < 0.7
        )

        if is_weak:
            state.self_healing_retry_count += 1
            state.self_healing_status = "rejected"
            state.reviewer_feedback = (
                "Triage is incomplete and too ambiguous for reliable action. "
                "Please add explicit malicious behavior, observed artifacts, and supporting evidence before resubmitting."
            )
            state.status = "revision_requested"
            state.threat_hunt_summary = "Triage rejected: insufficient behavioral evidence to proceed safely."
            state.threat_hunt_findings = [state.threat_hunt_summary]
            state.last_agent = self.agent_name
            state.notes.append("Threat Hunter rejected the weak triage and requested revision.")
            return state

        if state.triage_category == "malicious":
            hunter_findings.append("High-confidence malicious activity identified from environment evidence and reputation checks.")
        elif state.triage_category == "suspicious":
            hunter_findings.append("Behavior remains suspicious and should be examined for lateral movement or credential theft.")
        else:
            hunter_findings.append("Activity appears low-risk and should be treated as benign unless additional evidence appears.")

        if state.mitre_techniques:
            hunter_findings.append(f"MITRE technique correlation observed: {', '.join(state.mitre_techniques)}")

        state.threat_hunt_summary = " | ".join(hunter_findings)
        state.threat_hunt_findings = hunter_findings
        state.reviewer_feedback = "Triage accepted for workflow progression."
        state.self_healing_status = "accepted"
        state.mitre_tactics = ["Credential Access", "Execution"] if state.mitre_techniques else []
        state.final_summary = state.threat_hunt_summary
        state.status = "triaged"
        state.last_agent = self.agent_name
        state.notes.append("Threat Hunter accepted the triage and added hunting context.")
        return state
