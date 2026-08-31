import sys
import uuid
import json

print("Starting import...", flush=True)
from soc_agent_workforce.state import SOCState
from soc_agent_workforce.graph.workflow import build_workflow
print("Imports complete.", flush=True)

def run_test():
    print("Initializing test case...", flush=True)
    initial_state = SOCState(
        incident_id=f"INC-{uuid.uuid4().hex[:8]}",
        alert_summary="Multiple failed SSH login attempts followed by a successful login from a suspicious IP (198.51.100.23).",
        severity="high",
        ip_addresses=["198.51.100.23"],
        source="api",
        case_title="Suspicious SSH Login Pattern",
        mitre_techniques=["T1078"] # Pre-fill to avoid compliance failure if MITRE dataset lookup fails
    )
    
    app = build_workflow().compile()
    
    print("Running workflow...", flush=True)
    for event in app.stream(initial_state.model_dump()):
        for key, val in event.items():
            print(f"Node executed: {key}", flush=True)
    
    print("\nWorkflow Execution Complete.", flush=True)

if __name__ == "__main__":
    run_test()
