import os
os.environ["GROQ_API_KEY"] = ""
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["ABUSEIPDB_API_KEY"] = ""

import sys
import uuid
import json

from soc_agent_workforce.state import SOCState
from soc_agent_workforce.graph.workflow import build_workflow

def run_test():
    print("Initializing test case...")
    initial_state = SOCState(
        incident_id=f"INC-{uuid.uuid4().hex[:8]}",
        alert_summary="Multiple failed SSH login attempts followed by a successful login from a suspicious IP (198.51.100.23).",
        severity="high",
        ip_addresses=["198.51.100.23"],
        source="api",
        case_title="Suspicious SSH Login Pattern",
        mitre_techniques=["T1078"] # Pre-fill
    )
    
    app = build_workflow().compile()
    
    print("Running workflow (this will invoke the LLM agents, please wait)...")
    final_state_dict = app.invoke(initial_state.model_dump())
    
    # We don't need to manually print the report here because workflow.py's print_report node does it
    print("\nWorkflow Execution Complete.")

if __name__ == "__main__":
    run_test()
