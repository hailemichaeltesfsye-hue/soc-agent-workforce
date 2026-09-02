# FalconStream SOC Portal - Streamlit Setup & Running Guide

## STEP 9 - Professional SOC Dashboard Complete ✅

The Streamlit web application has been fully implemented with enterprise-grade styling and real-world SOC analyst UI patterns.

### Features Implemented

#### 🎨 **Professional Dark-Themed UI**
- Custom CSS with GitHub-inspired dark color scheme (#0E1117 primary, #161B22 secondary)
- Inter font family for modern, clean typography
- Hidden Streamlit branding (no menu, footer, header clutter)
- Smooth transitions and hover effects on interactive elements

#### 📊 **Header Bar with Status Indicators**
- FalconStream branding/logo placeholder
- Live connection status indicators for:
  - Groq API (online/offline)
  - ChromaDB (connected/disconnected)
- Pulsing green status dots for visual confirmation

#### 📥 **Sidebar: Alert Queue Management**
- "New Alert" button to submit incidents
- Active cases queue showing:
  - Timestamp (relative, e.g., "10 mins ago")
  - Case title
  - Severity badges (color-coded: red/orange/yellow/green)
  - Status indicators
- Severity filter: Critical, High, Medium, Low

#### 🚨 **Alert Intake Form**
- Alert title field
- Severity level selector (critical/high/medium/low)
- Raw alert payload textarea (supports large logs)
- IOC extraction fields:
  - IP address
  - Domains (comma-separated)
  - File hashes (comma-separated)
  - User accounts (comma-separated)
- Alert source dropdown (EDR, SIEM, IDS/IPS, Manual, Other)

#### 🔄 **Live Agent Pipeline Visualization**
- Visual stepper showing 6-step workflow:
  1. SOC Manager (Intake & Triage)
  2. Alert Analyst (Deep Analysis)
  3. Threat Hunter (Threat Hunt)
  4. Compliance Auditor (Compliance Check)
  5. Incident Reporter (Final Report)
  6. Human Approval (Human Review)
- Color-coded step states:
  - Completed: Green (✓)
  - Active: Blue (animated icon)
  - Pending: Gray (step number)
- Connecting lines between steps (green when completed)
- Connected lines show progress through pipeline

#### 📋 **Tabbed Investigation Interface**

**Tab 1: Investigation**
- Case header with title and severity badge
- Metrics dashboard showing:
  - Current Status
  - Triage Category
  - Triage Confidence (percentage)
  - Risk Score (0-10)
- Alert summary card
- Triage analysis notes
- Threat hunt findings (summary + bullet list)
- **HITL Approval Panel** (when awaiting human approval):
  - Alert banner with ✋ icon
  - Three action buttons: Approve, Reject, Hold
  - Clear call-to-action

**Tab 2: Evidence**
- **Extracted IOCs** displayed as styled tags (NOT raw JSON):
  - IP Addresses: 🌐 icon + address
  - Domains: 🔗 icon + domain
  - File Hashes: 🔐 icon + truncated hash
  - User Accounts: 👤 icon + username
- **MITRE ATT&CK Mapping**:
  - Tactics displayed as cards with 🎯 icon
  - Techniques displayed as cards with ⚙️ icon
  - Color-coded left borders for visual distinction
- Risk assessment narrative

**Tab 3: Compliance**
- Compliance status badge (Pending/Passed/Failed/Blocked)
- Compliance findings displayed as cards
- Required fields check:
  - Pass/fail indicator
  - List of missing fields if any
- **Revision & Self-Healing Timeline**:
  - Timeline items with dot indicator
  - Action type (Revised, Rejected, Approved, etc.)
  - Reason/feedback text
  - Timestamp
  - Color-coded by action type:
    - Rejected: Red border
    - Approved: Green border
    - Default: Blue border

**Tab 4: Final Report**
- Professional report header with severity-based gradient background
- Executive summary
- Timeline & Evidence section (2-column layout):
  - Triage results card
  - Threat hunt summary card
- Recommended remediation section
- MITRE ATT&CK coverage section
- Download options:
  - Markdown (.md) - formatted report
  - JSON (.json) - full structured data for archival

#### 🎯 **Key UI Components**

**Cards (soc-card)**
- Dark background (#161B22)
- Subtle border with hover effect
- Box shadow for depth
- Header with uppercase label
- Smooth transitions

**Badges**
- Inline-block display
- Severity-based colors:
  - Critical: Red (#DA3633)
  - High: Orange (#D29922)
  - Medium: Gold (#E3B341)
  - Low: Green (#238636)
  - Info: Blue (#1F6FEB)
  - Success: Green (#238636)
- Semi-transparent backgrounds with colored borders

**Evidence Tags**
- Dark background with subtle borders
- Icon prefix (🌐, 🔗, 🔐, 👤, 🎯, ⚙️)
- Hover effect with blue accent border
- Grouped in flex containers

**Timeline Items** (for revision history)
- Left-aligned with colored dot indicator
- Left border accent (3px)
- Supports rejected/approved/neutral states
- Content includes title, description, timestamp

**Metric Boxes**
- Grid layout (responsive)
- Centered text
- Large value font (28px)
- Small uppercase label
- Card styling

### How to Run

#### Prerequisites
- Python 3.13+
- UV package manager installed
- All dependencies from `pyproject.toml`

#### Option 1: Run with UV (Recommended)
```bash
cd soc-agent-workforce
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py
```

#### Option 2: Run on Specific Port
```bash
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py --server.port=8502
```

#### Option 3: Headless Mode (for automation/CI)
```bash
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py --server.headless=true
```

### Access the App
- **Local**: http://localhost:8501
- **Network**: http://<your-ip>:8501
- Browser will auto-open (or click the URL printed to console)

### Workflow
1. **Alert Intake**: Submit a new alert with title, severity, raw payload, and extracted IOCs
2. **Investigation**: Monitor the 6-step pipeline as agents analyze the incident
3. **Evidence Review**: Examine extracted IOCs and MITRE ATT&CK mappings (all formatted, no raw JSON)
4. **Compliance Check**: View compliance findings and self-healing revision history
5. **Approval**: When HITL is required, review the final report and Approve/Reject/Hold

### No Raw JSON Output
- ✅ All evidence displayed as styled cards/tags
- ✅ MITRE mappings shown with icons and color coding
- ✅ Compliance findings formatted as readable text
- ✅ Final report has proper sections (headers, narrative, structured tables)
- ✅ Download options for Markdown (human-readable) and JSON (archival)

### Customization
- **Colors**: Edit CSS variables in `<style>` block (`--bg-primary`, `--accent-blue`, etc.)
- **Port**: Change `--server.port=8501` to any available port
- **Theme**: Already dark-themed; can add light mode by duplicating CSS vars
- **Case Queue**: Currently mock data; connect to actual database/API as needed

### Troubleshooting

**Port 8501 already in use:**
```bash
# Kill existing process
lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use different port
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py --server.port=8502
```

**Dependencies not found:**
```bash
uv sync
```

**Graph execution timeout:**
- Adjust `recursion_limit` in state initialization (currently 100)
- Increase in code: `"recursion_limit": 100` → `"recursion_limit": 200`

---

## Architecture Overview

### File: `src/soc_agent_workforce/app/streamlit_app.py`

**Sections:**
1. **Imports & Config** - Dependencies and Streamlit page config
2. **Professional CSS** - 600+ lines of custom styling
3. **Header Bar** - Status indicators and branding
4. **State Management** - Session state and graph initialization
5. **Helper Functions** - `update_ui_state()`, `run_graph()`, badge formatters
6. **Sidebar** - Queue management and filters
7. **Main Content**:
   - Alert intake form (when no case active)
   - Active case view with tabs:
     - Investigation (with HITL panel)
     - Evidence
     - Compliance
     - Report

### Integration Points
- **SOCState**: Pydantic model for incident data
- **LangGraph Workflow**: `build_workflow()` compiles the 6-agent pipeline
- **MemorySaver**: In-memory checkpoint storage (can swap for persistent store)
- **Streamlit Session State**: Maintains case, logs, active agent tracking

---

**Status**: ✅ COMPLETE & READY FOR TESTING
