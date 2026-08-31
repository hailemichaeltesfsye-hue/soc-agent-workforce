import os
import sys
import uuid
import json
import streamlit as st
from pathlib import Path

# Fix path to allow importing soc_agent_workforce
sys.path.append(str(Path(__file__).resolve().parents[3]))
from soc_agent_workforce.state import SOCState
from soc_agent_workforce.graph.workflow import build_workflow
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# Must be the very first Streamlit command
st.set_page_config(page_title="SOC Analyst Portal", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# UI / CSS (Dark theme + Professional SOC)
# ==========================================
st.markdown("""
<style>
    /* Global dark theme and font overrides */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0E1117;
        color: #C9D1D9;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Top Bar */
    .top-bar {
        background-color: #161B22;
        padding: 10px 20px;
        border-bottom: 1px solid #30363D;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: -60px;
        margin-bottom: 20px;
    }
    .top-bar h2 { margin: 0; color: #58A6FF; font-weight: 600; font-size: 22px; }
    .status-pill {
        background-color: #238636;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    
    /* Cards */
    .soc-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .soc-card h3 { margin-top: 0; border-bottom: 1px solid #30363D; padding-bottom: 10px; font-size: 16px; color: #8B949E; text-transform: uppercase;}
    
    /* Badges */
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-critical { background-color: #DA3633; color: white; }
    .badge-high { background-color: #D29922; color: #0E1117; }
    .badge-medium { background-color: #E3B341; color: #0E1117; }
    .badge-low { background-color: #238636; color: white; }
    .badge-info { background-color: #1F6FEB; color: white; }
    
    /* Stepper */
    .stepper {
        display: flex;
        justify-content: space-between;
        margin-bottom: 30px;
        padding: 20px;
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
    }
    .step {
        text-align: center;
        flex: 1;
        font-size: 14px;
        color: #8B949E;
        position: relative;
    }
    .step.active {
        color: #58A6FF;
        font-weight: 600;
    }
    .step.completed {
        color: #238636;
    }
    .step i {
        display: block;
        margin-bottom: 8px;
        font-size: 20px;
    }
    
    /* Metric / Evidence Items */
    .evidence-tag {
        background: #21262D;
        border: 1px solid #30363D;
        padding: 8px 12px;
        border-radius: 6px;
        display: inline-block;
        margin: 4px;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="top-bar">
    <h2>⚡ FalconStream SOC Portal</h2>
    <div>
        <span class="status-pill">Groq: Online</span>
        <span class="status-pill">ChromaDB: Connected</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# State Management
# ==========================================
if "app_engine" not in st.session_state:
    st.session_state.app_engine = build_workflow().compile(checkpointer=MemorySaver())
    st.session_state.thread_config = {"configurable": {"thread_id": "streamlit_session_1"}}
    st.session_state.current_case = None
    st.session_state.graph_state = None
    st.session_state.logs = []
    st.session_state.active_agent = "idle"

app = st.session_state.app_engine
config = st.session_state.thread_config

def update_ui_state():
    state_snap = app.get_state(config)
    if state_snap and state_snap.values:
        st.session_state.graph_state = state_snap.values
        if state_snap.next:
            st.session_state.active_agent = state_snap.next[0]
        else:
            st.session_state.active_agent = "completed"
    else:
        st.session_state.graph_state = None

def run_graph(payload=None, resume_action=None):
    if resume_action:
        stream_gen = app.stream(Command(resume=resume_action), config=config)
    else:
        stream_gen = app.stream(payload, config=config)
        
    for event in stream_gen:
        for node_name, state_update in event.items():
            st.session_state.active_agent = node_name
            st.session_state.logs.append(f"Node completed: {node_name}")
    update_ui_state()

# ==========================================
# Sidebar UI
# ==========================================
with st.sidebar:
    st.markdown("### 📥 Active Queue")
    
    if st.button("➕ New Alert", use_container_width=True, type="primary"):
        st.session_state.current_case = None
        st.session_state.graph_state = None
        st.session_state.logs = []
        st.session_state.active_agent = "idle"
        st.rerun()
        
    st.divider()
    
    # Mock Queue
    st.markdown("""
    <div style="background: #161B22; border: 1px solid #30363D; padding: 10px; border-radius: 6px; margin-bottom: 10px; cursor: pointer;">
        <div style="font-size: 13px; color: #8B949E;">10 mins ago</div>
        <div style="font-weight: 600; font-size: 15px; margin: 4px 0;">Suspicious SSH Login Pattern</div>
        <span class="badge badge-high">HIGH</span> <span class="badge badge-info">Awaiting Review</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Filters")
    st.multiselect("Severity", ["Critical", "High", "Medium", "Low"], default=["Critical", "High"])

# ==========================================
# Main Content
# ==========================================
gs = st.session_state.graph_state

if not gs and st.session_state.current_case is None:
    # Alert Intake Screen
    st.markdown("### 🚨 New Alert Intake")
    with st.form("alert_intake"):
        alert_title = st.text_input("Alert Title", "Suspicious SSH Login Pattern")
        alert_text = st.text_area("Raw Alert Payload", "Multiple failed SSH login attempts followed by a successful login from a suspicious IP (198.51.100.23).")
        col1, col2 = st.columns(2)
        with col1:
            severity = st.selectbox("Severity", ["high", "critical", "medium", "low"])
        with col2:
            ip_address = st.text_input("Extracted IP Address (optional)", "198.51.100.23")
            
        submitted = st.form_submit_button("Investigate", type="primary")
        
        if submitted:
            st.session_state.current_case = f"INC-{uuid.uuid4().hex[:8]}"
            initial_state = SOCState(
                incident_id=st.session_state.current_case,
                alert_summary=alert_text,
                severity=severity,
                ip_addresses=[ip_address] if ip_address else [],
                source="api",
                case_title=alert_title,
                mitre_techniques=[] # Empty to trigger compliance self-healing
            )
            with st.spinner("Initializing Pipeline..."):
                run_graph(payload=initial_state.model_dump())
            st.rerun()

elif gs:
    st.markdown(f"### Case: {gs.get('case_title', 'Unknown')} ({gs.get('incident_id')})")
    
    # Render Stepper
    agents = ["soc_manager", "alert_analyst", "threat_hunter", "compliance_auditor", "incident_reporter", "__interrupt__"]
    labels = ["Intake", "Triage", "Hunter", "Compliance", "Reporter", "Approval"]
    
    active_idx = 5 if st.session_state.active_agent == "human_approval" else 6 if st.session_state.active_agent == "completed" else -1
    if active_idx == -1:
        try:
            active_idx = agents.index(st.session_state.active_agent)
        except ValueError:
            active_idx = 5 if gs.get('status') == 'awaiting_human_approval' else 0
            
    stepper_html = '<div class="stepper">'
    for i, label in enumerate(labels):
        cls = "step completed" if i < active_idx else "step active" if i == active_idx else "step"
        stepper_html += f'<div class="{cls}">{label}</div>'
    stepper_html += '</div>'
    st.markdown(stepper_html, unsafe_allow_html=True)
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Investigation", "Evidence", "Compliance Log", "Final Report"])
    
    with tab1:
        st.markdown('<div class="soc-card"><h3>Current Status</h3>', unsafe_allow_html=True)
        st.write(f"**State Status:** `{gs.get('status', 'unknown')}`")
        st.write(f"**Assigned To:** `{gs.get('assigned_to', 'unknown')}`")
        st.write(f"**Final Decision:** `{gs.get('final_decision', 'none')}`")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # HITL Control Panel
        if gs.get('status') == "awaiting_human_approval":
            st.markdown('<div class="soc-card" style="border-color: #D29922;"><h3>✋ Action Required: Human Approval</h3>', unsafe_allow_html=True)
            st.warning("The Incident Reporter has finalized the report. Please review the 'Final Report' tab and render a decision.")
            
            c1, c2, c3, _ = st.columns([1,1,1,3])
            with c1:
                if st.button("✅ Approve", use_container_width=True, type="primary"):
                    run_graph(resume_action="Approve")
                    st.rerun()
            with c2:
                if st.button("❌ Reject", use_container_width=True):
                    run_graph(resume_action="Reject")
                    st.rerun()
            with c3:
                if st.button("⏸ Hold", use_container_width=True):
                    run_graph(resume_action="Hold")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="soc-card"><h3>Extracted Entities & IOCs</h3>', unsafe_allow_html=True)
        ips = gs.get('ip_addresses', [])
        if ips:
            for ip in ips:
                st.markdown(f'<div class="evidence-tag">🌐 IP: <strong>{ip}</strong></div>', unsafe_allow_html=True)
        else:
            st.write("No IP evidence found.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="soc-card"><h3>MITRE ATT&CK Mapping</h3>', unsafe_allow_html=True)
        mitre = gs.get('mitre_techniques', [])
        if mitre:
            for m in mitre:
                st.markdown(f'<div class="evidence-tag">🎯 {m}</div>', unsafe_allow_html=True)
        else:
            st.write("No specific MITRE techniques mapped yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="soc-card"><h3>Pipeline & Compliance Audit Log</h3>', unsafe_allow_html=True)
        notes = gs.get('notes', [])
        for note in notes:
            st.markdown(f"> {note}")
        if not notes:
            st.write("No notes recorded.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        report = gs.get('incident_report', {})
        if not report:
            st.info("The Incident Report has not been generated yet.")
        else:
            st.markdown('<div class="soc-card">', unsafe_allow_html=True)
            st.title(report.get("case_title", "Incident Report"))
            sev = report.get('severity', 'UNKNOWN').upper()
            st.markdown(f"<span class='badge badge-{sev.lower()}'>Severity: {sev} ({report.get('severity_justification', '')})</span>", unsafe_allow_html=True)
            
            st.markdown("### Executive Summary")
            st.write(report.get("executive_summary", ""))
            
            st.markdown("### Timeline & Evidence")
            timeline = report.get("timeline_and_evidence", {})
            st.write("**Triage Notes:**", timeline.get("triage_notes", ""))
            st.write("**Threat Hunt Summary:**", timeline.get("threat_hunt_summary", ""))
            
            st.markdown("### Recommended Remediation")
            st.write(report.get("recommended_remediation", ""))
            
            st.download_button("💾 Download as Markdown", data=json.dumps(report, indent=2), file_name="report.md")
            st.markdown('</div>', unsafe_allow_html=True)
