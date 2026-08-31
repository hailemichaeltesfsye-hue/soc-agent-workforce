import os
import sys
import uuid

os.environ["GROQ_API_KEY"] = ""
os.environ["ABUSEIPDB_API_KEY"] = ""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from soc_agent_workforce.state import SOCState
from soc_agent_workforce.graph.workflow import build_workflow

def run_test():
    print("Setting up HITL test...")
    initial_state = SOCState(
        incident_id=f"INC-{uuid.uuid4().hex[:8]}",
        alert_summary="Multiple failed SSH login attempts followed by a successful login from a suspicious IP (198.51.100.23).",
        severity="high",
        ip_addresses=["198.51.100.23"],
        source="api",
        case_title="Suspicious SSH Login Pattern",
        mitre_techniques=["T1078"] 
    )
    
    checkpointer = MemorySaver()
    app = build_workflow().compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "test_thread_1"}}
    
    print("Running graph up to interrupt...")
    for event in app.stream(initial_state.model_dump(), config=config):
        for key, val in event.items():
            print(f"Node completed: {key}")
            
    state = app.get_state(config)
    if state.next:
        pending_task = state.tasks[0]
        interrupt_val = pending_task.interrupts[0].value
        print("\n" + "!"*50)
        print("GRAPH INTERRUPTED!")
        print(f"Message: {interrupt_val['message']}")
        print("!"*50 + "\n")
        
        decision = sys.argv[1] if len(sys.argv) > 1 else "Approve"
        print(f"Simulating human decision via CLI args: {decision}")
        
        print("\nResuming graph...")
        for event in app.stream(Command(resume=decision), config=config):
            for key, val in event.items():
                print(f"Node completed: {key}")
                
        final_state = app.get_state(config)
        print(f"\nFinal State Status: {final_state.values.get('status')}")
        print(f"Final Decision: {final_state.values.get('final_decision')}")
    else:
        print("Graph did not interrupt!")

if __name__ == "__main__":
    run_test()
