from __future__ import annotations

from soc_agent_workforce.state import SOCState

from .base_agent import BaseAgent


class SocManagerAgent(BaseAgent):
    """Supervisor that routes case progress between workflow stages."""

    agent_name = "soc_manager"
    system_prompt = "You are the SOC manager; route the case to the correct next step."

    def run(self, state: SOCState) -> SOCState:
        if state.status == "new":
            state.status = "triaged"
            state.assigned_to = "alert_analyst"
            state.last_agent = self.agent_name
            state.notes.append("SOC Manager assigned the case to Alert Analyst for triage.")
        elif state.status == "triaged" and state.compliance_status == "passed":
            state.status = "awaiting_human_approval"
            state.assigned_to = "incident_reporter"
            state.last_agent = self.agent_name
            state.notes.append("SOC Manager routed the case for human review.")
        elif state.status == "closed":
            state.final_decision = "close"
            state.last_agent = self.agent_name
        else:
            state.last_agent = self.agent_name
            state.notes.append("SOC Manager confirmed workflow progression.")
        return state
