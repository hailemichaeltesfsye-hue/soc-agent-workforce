import os
import sys
import uuid
import json
import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components

# Fix path to allow importing soc_agent_workforce
sys.path.append(str(Path(__file__).resolve().parents[3]))
from soc_agent_workforce.state import SOCState
from soc_agent_workforce.graph.workflow import build_workflow
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# Must be the very first Streamlit command
st.set_page_config(page_title="FalconStream SOC Portal", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# PROFESSIONAL SOC CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    :root {
        --bg-primary: #0D1017;
        --bg-secondary: #161B22;
        --bg-tertiary: #21262D;
        --border-color: #30363D;
        --text-primary: #C9D1D9;
        --text-secondary: #8B949E;
        --accent-blue: #58A6FF;
        --accent-green: #238636;
        --accent-orange: #D29922;
        --accent-red: #DA3633;
    }
    
    html, body, [class*="css"], [class*="stApp"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Hide Streamlit UI clutter */
    #MainMenu, footer, header { visibility: hidden; }
    .stApp > header { display: none; }
    
    /* ===== HEADER BAR ===== */
    .top-bar {
        background: linear-gradient(to right, var(--bg-secondary), var(--bg-secondary));
        border-bottom: 1px solid var(--border-color);
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -75px -16px 24px -16px;
        position: relative;
        z-index: 10;
    }
    
    .top-bar-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .top-bar-left h2 {
        margin: 0;
        font-size: 20px;
        font-weight: 700;
        color: var(--accent-blue);
        letter-spacing: -0.5px;
    }
    
    .logo-icon {
        font-size: 24px;
    }
    
    .top-bar-right {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        color: var(--text-secondary);
        letter-spacing: 0.5px;
    }
    
    .status-online {
        color: var(--accent-green);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-green);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* ===== CARDS & PANELS ===== */
    .soc-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    
    .soc-card:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.1);
    }
    
    .soc-card h3 {
        margin: 0 0 16px 0;
        font-size: 13px;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 12px;
    }
    
    .soc-card h4 {
        margin: 16px 0 8px 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .soc-card p {
        margin: 0 0 12px 0;
        line-height: 1.5;
        color: var(--text-primary);
    }
    
    /* Alert/Warning Banner */
    .alert-banner {
        background: linear-gradient(135deg, #4A1515 0%, #2D0E0E 100%);
        border-left: 4px solid var(--accent-red);
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
        border: 1px solid var(--accent-red);
    }
    
    .alert-banner h4 {
        margin: 0 0 8px 0;
        color: #FF6B6B;
        font-weight: 700;
    }
    
    .alert-banner p {
        margin: 0;
        color: #E8AAAA;
        font-size: 13px;
    }
    
    /* ===== BADGES & TAGS ===== */
    .badge {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        white-space: nowrap;
        margin: 2px;
    }
    
    .badge-critical {
        background-color: rgba(218, 54, 51, 0.2);
        color: #FF6B6B;
        border: 1px solid rgba(218, 54, 51, 0.5);
    }
    
    .badge-high {
        background-color: rgba(210, 153, 34, 0.2);
        color: #FFB86C;
        border: 1px solid rgba(210, 153, 34, 0.5);
    }
    
    .badge-medium {
        background-color: rgba(227, 179, 65, 0.2);
        color: #FECA57;
        border: 1px solid rgba(227, 179, 65, 0.5);
    }
    
    .badge-low {
        background-color: rgba(35, 134, 54, 0.2);
        color: #51CF66;
        border: 1px solid rgba(35, 134, 54, 0.5);
    }
    
    .badge-info {
        background-color: rgba(31, 111, 235, 0.2);
        color: #74C0FC;
        border: 1px solid rgba(31, 111, 235, 0.5);
    }
    
    .badge-success {
        background-color: rgba(35, 134, 54, 0.2);
        color: #51CF66;
        border: 1px solid rgba(35, 134, 54, 0.5);
    }
    
    /* ===== STEPPER / PIPELINE VISUALIZATION ===== */
    .stepper-container {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stepper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
    }
    
    .step {
        flex: 1;
        text-align: center;
        position: relative;
        z-index: 2;
    }
    
    .step:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 24px;
        left: 50%;
        width: 100%;
        height: 2px;
        background: var(--border-color);
        z-index: 1;
    }
    
    .step.completed:not(:last-child)::after {
        background: var(--accent-green);
    }
    
    .step-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--bg-tertiary);
        border: 2px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px;
        font-weight: 700;
        color: var(--text-secondary);
        font-size: 18px;
        transition: all 0.3s;
    }
    
    .step.active .step-circle {
        background: var(--accent-blue);
        border-color: var(--accent-blue);
        color: white;
        box-shadow: 0 0 12px rgba(88, 166, 255, 0.4);
    }
    
    .step.completed .step-circle {
        background: var(--accent-green);
        border-color: var(--accent-green);
        color: white;
    }
    
    .step-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        margin-top: 8px;
        letter-spacing: 0.5px;
    }
    
    .step.active .step-label {
        color: var(--accent-blue);
    }
    
    .step.completed .step-label {
        color: var(--accent-green);
    }
    
    /* ===== EVIDENCE & IOC TAGS ===== */
    .evidence-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }
    
    .evidence-tag {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        color: var(--text-primary);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
    }
    
    .evidence-tag:hover {
        border-color: var(--accent-blue);
        background: var(--bg-secondary);
        box-shadow: 0 2px 6px rgba(88, 166, 255, 0.1);
    }
    
    /* ===== TABLES ===== */
    .table-container {
        overflow-x: auto;
        margin-top: 12px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }
    
    table thead {
        background: var(--bg-tertiary);
        border-bottom: 2px solid var(--border-color);
    }
    
    table th {
        padding: 12px;
        text-align: left;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    table td {
        padding: 10px 12px;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    table tbody tr:hover {
        background: var(--bg-tertiary);
    }
    
    /* ===== FORM INPUTS ===== */
    .stTextInput, .stSelectbox, .stTextArea {
        background: var(--bg-secondary) !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--accent-blue) !important;
        color: white !important;
        border: 1px solid var(--accent-blue) !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #4A8FDF !important;
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3) !important;
    }
    
    /* ===== REVISION HISTORY TIMELINE ===== */
    .timeline-item {
        display: flex;
        gap: 16px;
        margin-bottom: 16px;
        padding: 12px;
        background: var(--bg-tertiary);
        border-left: 3px solid var(--accent-blue);
        border-radius: 4px;
    }
    
    .timeline-item.rejected {
        border-left-color: var(--accent-red);
    }
    
    .timeline-item.approved {
        border-left-color: var(--accent-green);
    }
    
    .timeline-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-blue);
        margin-top: 6px;
        flex-shrink: 0;
    }
    
    .timeline-item.rejected .timeline-dot {
        background: var(--accent-red);
    }
    
    .timeline-item.approved .timeline-dot {
        background: var(--accent-green);
    }
    
    .timeline-content {
        flex: 1;
    }
    
    .timeline-content h5 {
        margin: 0 0 4px 0;
        font-size: 12px;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .timeline-content p {
        margin: 0 0 4px 0;
        font-size: 12px;
        color: var(--text-secondary);
    }
    
    .timeline-time {
        font-size: 11px;
        color: var(--text-secondary);
        opacity: 0.7;
    }
    
    /* ===== REPORT SECTION ===== */
    .report-header {
        background: linear-gradient(135deg, var(--accent-blue), #1F6FEB);
        padding: 32px;
        border-radius: 8px;
        margin-bottom: 24px;
        color: white;
        text-align: center;
    }
    
    .report-header h1 {
        margin: 0 0 8px 0;
        font-size: 28px;
        font-weight: 700;
    }
    
    .report-section {
        margin-bottom: 24px;
    }
    
    .report-section h2 {
        font-size: 16px;
        font-weight: 700;
        color: var(--accent-blue);
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 12px;
        margin-bottom: 16px;
    }
    
    /* ===== SIDEBAR ===== */
    .sidebar-queue-item {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .sidebar-queue-item:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 2px 6px rgba(88, 166, 255, 0.1);
    }
    
    .queue-timestamp {
        font-size: 11px;
        color: var(--text-secondary);
        margin-bottom: 4px;
    }
    
    .queue-title {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    
    /* ===== METRICS ROW ===== */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-box {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        padding: 16px;
        border-radius: 6px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--accent-blue);
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER BAR WITH STATUS INDICATORS
# ==========================================
col_header_left, col_header_right = st.columns([2, 1])

with col_header_left:
    st.markdown("""
    <div class="top-bar">
        <div class="top-bar-left">
            <div class="logo-icon">⚡</div>
            <h2>FalconStream</h2>
        </div>
        <div class="top-bar-right">
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span class="status-online">Groq API: Online</span>
            </div>
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span class="status-online">ChromaDB: Connected</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# STATE MANAGEMENT & INITIALIZATION
# ==========================================
if "app_engine" not in st.session_state:
    st.session_state.app_engine = build_workflow().compile(checkpointer=MemorySaver())
    st.session_state.thread_config = {"configurable": {"thread_id": f"streamlit_{uuid.uuid4().hex[:8]}"}, "recursion_limit": 100}
    st.session_state.current_case = None
    st.session_state.graph_state = None
    st.session_state.logs = []
    st.session_state.active_agent = "idle"
    st.session_state.case_queue = []

app = st.session_state.app_engine
config = st.session_state.thread_config

def update_ui_state():
    """Pull latest state from graph"""
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
    """Execute graph stream and capture events"""
    try:
        if resume_action:
            stream_gen = app.stream(Command(resume=resume_action), config=config)
        else:
            stream_gen = app.stream(payload, config=config)
        
        for event in stream_gen:
            for node_name, state_update in event.items():
                st.session_state.active_agent = node_name
                st.session_state.logs.append(f"✓ {node_name}")
        
        update_ui_state()
    except Exception as e:
        st.error(f"Graph execution error: {str(e)}")

def get_severity_badge(severity: str) -> str:
    """Return badge class for severity level"""
    return f"badge-{severity}" if severity in ["critical", "high", "medium", "low"] else "badge-info"

def format_timestamp(dt) -> str:
    """Format datetime for display"""
    if isinstance(dt, str):
        return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, 'strftime') else str(dt)


def render_live_agent_flow(active_agent_name: str):
    """Render a non-linear agent mesh with animated motion between all nodes."""
    agent_order = [
        ("soc_manager", "SOC Manager", "Intake & Triage"),
        ("alert_analyst", "Alert Analyst", "Triage"),
        ("threat_hunter", "Threat Hunter", "Hunt"),
        ("compliance_auditor", "Compliance", "Review"),
        ("incident_reporter", "Reporter", "Write"),
        ("approval", "Human Approval", "Review")
    ]

    # Reduced vertical spread so the bottom node (and its subtitle) fits
    # comfortably inside the viewBox with margin to spare.
    node_positions = {
        "soc_manager": (500, 60),
        "alert_analyst": (220, 200),
        "threat_hunter": (780, 200),
        "compliance_auditor": (290, 360),
        "incident_reporter": (710, 360),
        "approval": (500, 490),
    }

    html = """
    <div style="margin-top: 12px; margin-bottom: 20px; border-radius: 12px; overflow: visible; background: linear-gradient(180deg, rgba(10,14,24,1), rgba(12,18,30,1)); border: 1px solid #2c3a4d; box-shadow: 0 16px 32px rgba(0,0,0,0.25); padding-bottom: 32px;">
      <div style="padding: 12px 16px 0 16px; font-size: 11px; letter-spacing: 0.08em; color: #8BA1C0; text-transform: uppercase; font-weight: 700;">Live team collaboration flow</div>
      <svg width="100%" viewBox="0 0 1000 570" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SOC agent collaboration diagram" preserveAspectRatio="xMidYMid meet" style="display: block;">
        <defs>
          <linearGradient id="agentGlow" x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stop-color="#58A6FF" />
            <stop offset="100%" stop-color="#74E4FF" />
          </linearGradient>
          <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <style>
          .flow-line {
            stroke: rgba(88, 166, 255, 0.35);
            stroke-width: 2.5;
            fill: none;
            stroke-linecap: round;
            stroke-dasharray: 10 16;
            animation: dashFlow 3.2s linear infinite;
          }
          .flow-line.active {
            stroke: rgba(116, 228, 255, 0.95);
            filter: url(#softGlow);
          }
          .agent-node {
            fill: rgba(20, 26, 36, 1);
            stroke: rgba(97, 120, 151, 0.7);
            stroke-width: 2;
          }
          .agent-node.active {
            fill: rgba(20, 26, 36, 1);
            stroke: url(#agentGlow);
            filter: url(#softGlow);
          }
          .agent-label {
            font-size: 12px;
            font-weight: 700;
            fill: #DDE8FF;
            text-anchor: middle;
            font-family: Arial, sans-serif;
          }
          .agent-meta {
            font-size: 10px;
            fill: #8BA1C0;
            text-anchor: middle;
            font-family: Arial, sans-serif;
          }
          .travel-dot {
            fill: #74E4FF;
            opacity: 0.95;
          }
          @keyframes dashFlow {
            from { stroke-dashoffset: 0; }
            to { stroke-dashoffset: -260; }
          }
        </style>
    """

    connections = [
        ("soc_manager", "alert_analyst"),
        ("soc_manager", "threat_hunter"),
        ("alert_analyst", "threat_hunter"),
        ("alert_analyst", "compliance_auditor"),
        ("alert_analyst", "incident_reporter"),
        ("threat_hunter", "incident_reporter"),
        ("threat_hunter", "compliance_auditor"),
        ("compliance_auditor", "approval"),
        ("incident_reporter", "approval"),
        ("soc_manager", "approval"),
        ("compliance_auditor", "incident_reporter")
    ]

    for source, target in connections:
        x1, y1 = node_positions[source]
        x2, y2 = node_positions[target]
        cx1 = x1 + (x2 - x1) * 0.45
        cy1 = y1 + (y2 - y1) * 0.12
        cx2 = x1 + (x2 - x1) * 0.55
        cy2 = y1 + (y2 - y1) * 0.88
        path = f"M {x1} {y1} C {cx1} {cy1}, {cx2} {cy2}, {x2} {y2}"
        is_active = source in {active_agent_name, "soc_manager"} or target == active_agent_name or (active_agent_name == "approval" and (source == "approval" or target == "approval"))
        html += f'<path class="flow-line {"active" if is_active else ""}" d="{path}" />'
        html += f'<circle class="travel-dot" r="4"><animateMotion dur="{2.8 + (hash(source + target) % 3) * 0.5}s" repeatCount="indefinite" path="{path}" /></circle>'

    for name, title, subtitle in agent_order:
        cx, cy = node_positions[name]
        is_active = name == active_agent_name or (active_agent_name == "approval" and name == "approval")
        node_radius = 46 if name == "approval" else 32
        active_radius = 58 if name == "approval" else 46
        if is_active:
            html += f'<g>'
            html += f'<circle class="agent-node active" cx="{cx}" cy="{cy}" r="{node_radius}" />'
            html += f'<circle cx="{cx}" cy="{cy}" r="{active_radius}" fill="none" stroke="rgba(110,231,249,0.28)" stroke-width="2"><animate attributeName="r" values="{active_radius};{active_radius + 8};{active_radius}" dur="2.4s" repeatCount="indefinite" /></circle>'
            html += f'</g>'
        else:
            html += f'<circle class="agent-node" cx="{cx}" cy="{cy}" r="{node_radius if name == "approval" else 32}" />'
        html += f'<text x="{cx}" y="{cy + 7}" class="agent-label">{title}</text>'
        html += f'<text x="{cx}" y="{cy + 28}" class="agent-meta">{subtitle}</text>'

    html += """
      </svg>
    </div>
    """
    return html

# ==========================================
# SIDEBAR: CASE QUEUE & FILTERS
# ==========================================
with st.sidebar:
    st.markdown("#### 📥 Alert Queue Management")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ New Alert", use_container_width=True, type="primary"):
            st.session_state.current_case = None
            st.session_state.graph_state = None
            st.session_state.logs = []
            st.session_state.active_agent = "idle"
            st.rerun()
    with col_btn2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    st.markdown("**Active Cases:**")
    if st.session_state.case_queue:
        for case in st.session_state.case_queue[:5]:  # Show top 5
            st.markdown(f"""
            <div class="sidebar-queue-item">
                <div class="queue-timestamp">{case.get('timestamp', 'N/A')}</div>
                <div class="queue-title">{case.get('title', 'Untitled')}</div>
                <span class="badge {get_severity_badge(case.get('severity', 'low'))}">{case.get('severity', 'unknown').upper()}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active cases. Create a new alert to begin.")
    
    st.divider()
    st.markdown("**Filter by Severity:**")
    severity_filter = st.multiselect(
        "Show cases with severity:",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High"],
        key="severity_filter",
        label_visibility="collapsed"
    )

# ==========================================
# MAIN CONTENT: ALERT INTAKE OR ACTIVE CASE
# ==========================================
gs = st.session_state.graph_state

if not gs and st.session_state.current_case is None:
    # ========== ALERT INTAKE SCREEN ==========
    st.markdown("## 🚨 Alert Intake & Investigation")
    st.markdown("Submit a new security alert or anomaly for investigation.")
    
    with st.form("alert_intake_form", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            alert_title = st.text_input(
                "Alert Title",
                value="Suspicious SSH Login Pattern",
                help="Brief title summarizing the alert"
            )
            severity = st.selectbox(
                "Severity Level",
                ["critical", "high", "medium", "low"],
                help="Initial severity assessment"
            )
        
        with col2:
            ip_address = st.text_input(
                "Extracted IOC: IP Address",
                value="198.51.100.23",
                help="(Optional) IP address involved in the incident"
            )
            alert_source = st.selectbox(
                "Alert Source",
                ["EDR", "SIEM", "IDS/IPS", "Manual", "Other"],
                help="Source system of the alert"
            )
        
        alert_text = st.text_area(
            "Raw Alert Payload",
            value="Multiple failed SSH login attempts (15) over 5 minutes followed by successful authentication from IP 198.51.100.23 to prod-db-01. Suspicious activity detected from non-standard port.",
            height=120,
            help="Paste the complete alert details, logs, or event information"
        )
        
        col_domain, col_hash, col_user = st.columns(3)
        with col_domain:
            domains = st.text_input("Domains (comma-separated)", "")
        with col_hash:
            hashes = st.text_input("File Hashes (comma-separated)", "")
        with col_user:
            users = st.text_input("User Accounts (comma-separated)", "")
        
        st.divider()
        
        col_submit, col_cancel = st.columns([1, 4])
        with col_submit:
            submitted = st.form_submit_button("🔍 Investigate", type="primary", use_container_width=True)
        
        if submitted:
            # Create incident and initialize graph
            incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
            st.session_state.current_case = incident_id
            
            # Add to queue
            st.session_state.case_queue.insert(0, {
                "id": incident_id,
                "title": alert_title,
                "severity": severity,
                "timestamp": format_timestamp(datetime.now()),
                "status": "investigating"
            })
            
            # Prepare initial state
            initial_state = SOCState(
                incident_id=incident_id,
                case_title=alert_title,
                alert_summary=alert_text,
                severity=severity,
                alert_source_system=alert_source,
                ip_addresses=[ip_address] if ip_address else [],
                domains=[d.strip() for d in domains.split(",") if d.strip()],
                hashes=[h.strip() for h in hashes.split(",") if h.strip()],
                user_accounts=[u.strip() for u in users.split(",") if u.strip()],
                source="streamlit",
                status="new"
            )

            # Make the case view appear immediately so the dashboard transitions from
            # the intake form to the active investigation panel even while the graph runs.
            st.session_state.graph_state = initial_state.model_dump()
            st.session_state.active_agent = "soc_manager"

            with st.spinner("⏳ Initializing SOC workflow..."):
                try:
                    run_graph(payload=initial_state.model_dump())
                except Exception:
                    st.session_state.graph_state = initial_state.model_dump()
                    st.session_state.active_agent = "soc_manager"
            
            st.rerun()

elif gs:
    # ========== ACTIVE CASE: INVESTIGATION VIEW ==========
    incident_id = gs.get('incident_id', 'UNKNOWN')
    case_title = gs.get('case_title', 'Untitled Incident')
    severity = gs.get('severity', 'low')
    
    # Case Header
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h1 style="margin: 0; color: #C9D1D9;">{case_title}</h1>
                <p style="margin: 8px 0 0 0; color: #8B949E; font-size: 14px;">Case ID: <code>{incident_id}</code></p>
            </div>
            <div>
                <span class="badge {get_severity_badge(severity)}" style="font-size: 13px; padding: 8px 12px;">{severity.upper()}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== LIVE AGENT PIPELINE VISUALIZATION ==========
    st.markdown("### 🔄 Investigation Pipeline")
    
    pipeline_steps = [
        {"name": "soc_manager", "label": "SOC Manager", "icon": "👨‍💼", "desc": "Intake & Triage"},
        {"name": "alert_analyst", "label": "Alert Analyst", "icon": "🔎", "desc": "Deep Analysis"},
        {"name": "threat_hunter", "label": "Threat Hunter", "icon": "🎯", "desc": "Threat Hunt"},
        {"name": "compliance_auditor", "label": "Compliance", "icon": "✓", "desc": "Compliance Check"},
        {"name": "incident_reporter", "label": "Reporter", "icon": "📋", "desc": "Final Report"},
        {"name": "__interrupt__", "label": "Approval", "icon": "✋", "desc": "Human Review"}
    ]
    
    # Determine active step
    active_step_idx = -1
    try:
        for idx, step in enumerate(pipeline_steps):
            if step["name"] == st.session_state.active_agent or (step["name"] == "__interrupt__" and gs.get('status') == 'awaiting_human_approval'):
                active_step_idx = idx
                break
    except:
        pass
    
    active_flow_name = st.session_state.active_agent
    if active_flow_name == "completed":
        active_flow_name = "approval"
    elif active_flow_name == "__interrupt__":
        active_flow_name = "approval"

    components.html(render_live_agent_flow(active_flow_name), height=820, scrolling=False)
    
    # ========== MAIN TABBED INTERFACE ==========
    tab_investigation, tab_evidence, tab_compliance, tab_report = st.tabs([
        "🔍 Investigation",
        "📊 Evidence",
        "📋 Compliance",
        "📄 Report"
    ])
    
    # ===== TAB 1: INVESTIGATION =====
    with tab_investigation:
        st.markdown("### Investigation Status")
        
        col_status1, col_status2, col_status3, col_status4 = st.columns(4)
        
        with col_status1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label">Current Status</div>', unsafe_allow_html=True)
            status_val = gs.get('status', 'new').replace('_', ' ').title()
            st.markdown(f'<div class="metric-value" style="font-size: 16px;">{status_val}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_status2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label">Triage Category</div>', unsafe_allow_html=True)
            triage_cat = gs.get('triage_category', 'unknown').title()
            st.markdown(f'<div class="metric-value" style="font-size: 16px;">{triage_cat}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_status3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label">Triage Confidence</div>', unsafe_allow_html=True)
            conf = gs.get('triage_confidence', 0)
            conf_pct = f"{int(conf * 100)}%" if conf else "—"
            st.markdown(f'<div class="metric-value" style="font-size: 16px;">{conf_pct}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_status4:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label">Risk Score</div>', unsafe_allow_html=True)
            risk = gs.get('entity_risk_score', 0)
            risk_disp = f"{risk:.1f}/10" if risk else "—"
            st.markdown(f'<div class="metric-value" style="font-size: 16px;">{risk_disp}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Alert Summary
        st.markdown("### Alert Summary")
        alert_summary = gs.get('alert_summary', 'No summary available.')
        st.markdown(f"""
        <div class="soc-card">
            <p>{alert_summary}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Triage Notes
        if gs.get('triage_notes'):
            st.markdown("### Triage Analysis")
            st.markdown(f"""
            <div class="soc-card">
                <h4>Analyst Notes</h4>
                <p>{gs.get('triage_notes', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Threat Hunt Summary
        if gs.get('threat_hunt_summary'):
            st.markdown("### Threat Hunt Findings")
            st.markdown(f"""
            <div class="soc-card">
                <h4>Hunt Summary</h4>
                <p>{gs.get('threat_hunt_summary', '')}</p>
                <h4>Key Findings</h4>
                <ul>
            """, unsafe_allow_html=True)
            for finding in gs.get('threat_hunt_findings', []):
                st.markdown(f"<li>{finding}</li>", unsafe_allow_html=True)
            st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # ===== HITL APPROVAL PANEL =====
        if gs.get('status') == "awaiting_human_approval":
            st.markdown("""
            <div class="alert-banner">
                <h4>✋ Action Required: Human Approval</h4>
                <p>The incident analysis is complete. Review the report and provide your decision to proceed.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_approve, col_reject, col_hold, _ = st.columns([1, 1, 1, 2])
            
            with col_approve:
                if st.button("✅ Approve & Escalate", use_container_width=True, type="primary"):
                    with st.spinner("Processing approval..."):
                        run_graph(resume_action="Approve")
                    st.success("Approved! Escalating incident...")
                    st.rerun()
            
            with col_reject:
                if st.button("❌ Reject & Close", use_container_width=True):
                    with st.spinner("Processing rejection..."):
                        run_graph(resume_action="Reject")
                    st.info("Incident rejected and closed.")
                    st.rerun()
            
            with col_hold:
                if st.button("⏸ Hold for Review", use_container_width=True):
                    with st.spinner("Holding case..."):
                        run_graph(resume_action="Hold")
                    st.info("Case held for further review.")
                    st.rerun()
    
    # ===== TAB 2: EVIDENCE =====
    with tab_evidence:
        st.markdown("### Extracted Indicators of Compromise (IOCs)")
        
        # IP Addresses
        ips = gs.get('ip_addresses', [])
        st.markdown("#### 🌐 IP Addresses")
        if ips:
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for ip in ips:
                st.markdown(f'<div class="evidence-tag">📍 <strong>{ip}</strong></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No IP addresses extracted.")
        
        # Domains
        domains = gs.get('domains', [])
        st.markdown("#### 🔗 Domains")
        if domains:
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for domain in domains:
                st.markdown(f'<div class="evidence-tag">🔗 <strong>{domain}</strong></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No domains extracted.")
        
        # File Hashes
        hashes = gs.get('hashes', [])
        st.markdown("#### 📄 File Hashes")
        if hashes:
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for hash_val in hashes:
                st.markdown(f'<div class="evidence-tag">🔐 <strong>{hash_val[:16]}...</strong></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No file hashes extracted.")
        
        # User Accounts
        users = gs.get('user_accounts', [])
        st.markdown("#### 👤 User Accounts")
        if users:
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for user in users:
                st.markdown(f'<div class="evidence-tag">👤 <strong>{user}</strong></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No user accounts extracted.")
        
        # MITRE ATT&CK Mapping
        st.markdown("### 🎯 MITRE ATT&CK Mapping")
        mitre_techniques = gs.get('mitre_techniques', [])
        mitre_tactics = gs.get('mitre_tactics', [])
        
        if mitre_tactics:
            st.markdown("**Tactics:**")
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for tactic in mitre_tactics:
                st.markdown(f'<div class="evidence-tag" style="border-left: 3px solid #58A6FF;">🎯 {tactic}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if mitre_techniques:
            st.markdown("**Techniques:**")
            st.markdown('<div class="evidence-container">', unsafe_allow_html=True)
            for technique in mitre_techniques:
                st.markdown(f'<div class="evidence-tag" style="border-left: 3px solid #D29922;">⚙️ {technique}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if not mitre_tactics and not mitre_techniques:
            st.info("No MITRE ATT&CK mappings available yet.")
        
        # Risk Assessment
        if gs.get('risk_assessment'):
            st.markdown("### Risk Assessment")
            st.markdown(f"""
            <div class="soc-card">
                <p>{gs.get('risk_assessment', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== TAB 3: COMPLIANCE =====
    with tab_compliance:
        st.markdown("### Compliance & Self-Healing Status")
        
        compliance_status = gs.get('compliance_status', 'pending').upper()
        status_color = {
            'PENDING': 'badge-info',
            'PASSED': 'badge-success',
            'FAILED': 'badge-high',
            'BLOCKED': 'badge-critical'
        }.get(compliance_status, 'badge-info')
        
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Compliance Status</div>
            <div style="margin: 12px 0;">
                <span class="badge {status_color}" style="font-size: 13px; padding: 8px 12px;">{compliance_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compliance Findings
        compliance_findings = gs.get('compliance_findings', [])
        if compliance_findings:
            st.markdown("### Compliance Findings")
            for finding in compliance_findings:
                st.markdown(f"""
                <div class="soc-card">
                    <p>{finding}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Required Fields Status
        st.markdown("### Required Fields Check")
        required_present = gs.get('required_fields_present', False)
        missing_fields = gs.get('required_fields_missing', [])
        
        if required_present:
            st.markdown(f'<span class="badge badge-success">✓ All Required Fields Present</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge badge-high">Missing {len(missing_fields)} Required Fields</span>', unsafe_allow_html=True)
            if missing_fields:
                st.markdown("**Missing:**")
                for field in missing_fields:
                    st.markdown(f"- `{field}`")
        
        # Revision History / Self-Healing Timeline
        revision_hist = gs.get('triage_revision_history', [])
        if revision_hist:
            st.markdown("### Revision & Self-Healing Timeline")
            for revision in revision_hist:
                action = revision.get('action', 'revision')
                reason = revision.get('reason', 'No reason provided')
                timestamp = revision.get('timestamp', 'N/A')
                
                timeline_class = 'rejected' if 'rejected' in action.lower() else 'approved' if 'approved' in action.lower() else ''
                
                st.markdown(f"""
                <div class="timeline-item {timeline_class}">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                        <h5>{action.title()}</h5>
                        <p>{reason}</p>
                        <div class="timeline-time">{timestamp}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== TAB 4: FINAL REPORT =====
    with tab_report:
        st.markdown("### Incident Report")
        
        report = gs.get('incident_report')
        
        if not report:
            st.info("📋 Report generation in progress or not yet available. Check back soon.")
        else:
            # Report Header
            report_severity = report.get('severity', 'unknown').upper()
            severity_color = {
                'CRITICAL': 'var(--accent-red)',
                'HIGH': 'var(--accent-orange)',
                'MEDIUM': '#FECA57',
                'LOW': 'var(--accent-green)'
            }.get(report_severity, 'var(--accent-blue)')
            
            st.markdown(f"""
            <div class="report-header" style="background: linear-gradient(135deg, {severity_color}, {severity_color}99);">
                <h1>⚠️ {report.get('case_title', 'Incident Report')}</h1>
                <p style="margin: 0; font-size: 16px; opacity: 0.95;">Severity: <strong>{report_severity}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Executive Summary
            st.markdown("### Executive Summary")
            st.markdown(f"""
            <div class="soc-card">
                <p>{report.get('executive_summary', 'No summary available.')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Timeline & Evidence
            if report.get('timeline_and_evidence'):
                st.markdown("### Timeline & Evidence")
                timeline = report.get('timeline_and_evidence', {})
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"""
                    <div class="soc-card">
                        <h4>Triage Results</h4>
                        <p>{timeline.get('triage_notes', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"""
                    <div class="soc-card">
                        <h4>Threat Hunt Summary</h4>
                        <p>{timeline.get('threat_hunt_summary', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recommended Remediation
            if report.get('recommended_remediation'):
                st.markdown("### Recommended Remediation")
                st.markdown(f"""
                <div class="soc-card">
                    <p>{report.get('recommended_remediation', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # MITRE Coverage
            if report.get('mitre_coverage'):
                st.markdown("### MITRE ATT&CK Coverage")
                st.markdown(f"""
                <div class="soc-card">
                    <p>{report.get('mitre_coverage', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Download Options
            st.divider()
            
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                # Markdown download
                report_md = f"""# {report.get('case_title', 'Incident Report')}

**Severity:** {report_severity}
**Case ID:** {incident_id}
**Generated:** {format_timestamp(datetime.now())}

## Executive Summary
{report.get('executive_summary', 'N/A')}

## Timeline & Evidence
### Triage
{report.get('timeline_and_evidence', {}).get('triage_notes', 'N/A')}

### Threat Hunt
{report.get('timeline_and_evidence', {}).get('threat_hunt_summary', 'N/A')}

## Recommended Remediation
{report.get('recommended_remediation', 'N/A')}

## MITRE ATT&CK Coverage
{report.get('mitre_coverage', 'N/A')}
"""
                
                st.download_button(
                    label="📥 Download as Markdown",
                    data=report_md,
                    file_name=f"incident_report_{incident_id}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col_dl2:
                # JSON download for archival
                st.download_button(
                    label="💾 Download as JSON",
                    data=json.dumps(report, indent=2, default=str),
                    file_name=f"incident_report_{incident_id}.json",
                    mime="application/json",
                    use_container_width=True
                )