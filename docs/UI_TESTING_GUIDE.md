# FalconStream SOC Portal — Complete UI Testing Guide

## Project Status: ✅ ALL STEPS COMPLETE (1-9)

| Step | Component | Status |
|------|-----------|--------|
| 1 | Project Structure | ✅ Complete |
| 2 | LangGraph Workflow | ✅ Complete |
| 3 | SOCState Pydantic Model | ✅ Complete |
| 4 | 6 Agent System | ✅ Complete |
| 5 | MCP Server + Tools | ✅ Complete |
| 6 | ChromaDB Memory | ✅ Complete |
| 7 | Environment Setup | ✅ Complete |
| 8 | Graph Implementation | ✅ Complete |
| 9 | Streamlit Dashboard | ✅ Complete |

---

## QUICK START: Launch the Dashboard

### Prerequisites
- Python 3.13+
- UV package manager
- Groq API Key (free from https://console.groq.com)
- Environment variables set

### Step 1: Set Environment Variables
```bash
# Linux/Mac
export GROQ_API_KEY="your-groq-api-key-here"

# Windows PowerShell
$env:GROQ_API_KEY="your-groq-api-key-here"

# Windows Git Bash
export GROQ_API_KEY="your-groq-api-key-here"
```

### Step 2: Start the App
```bash
cd "c:\Users\pavilion\Documents\Agentic Engineering Course\module-5\soc-agent-workforce"
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py
```

### Step 3: Access in Browser
- Opens automatically to **http://localhost:8501**
- If port 8501 is busy, use: `uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py --server.port=8502`

---

## COMPREHENSIVE UI TESTING CHECKLIST

### ✅ TEST 1: Initial Page Load & Header

**What to verify:**
- [ ] Dark theme loads (dark background, light text)
- [ ] ⚡ FalconStream logo displays in top-left
- [ ] Status indicators visible:
  - [ ] 🟢 Groq API: Online (green pulsing dot)
  - [ ] 🟢 ChromaDB: Connected (green pulsing dot)
- [ ] No Streamlit branding visible (no hamburger menu, footer, or built-in header)
- [ ] Font is clean and professional (Inter)

**Expected result:**
```
┌─────────────────────────────────────────────────┐
│  ⚡ FalconStream    🟢 Groq: Online             │
│                     🟢 ChromaDB: Connected      │
└─────────────────────────────────────────────────┘
```

---

### ✅ TEST 2: Sidebar - Alert Queue Management

**What to verify:**
- [ ] **"New Alert"** button is prominent (blue, clickable)
- [ ] **"Refresh"** button exists
- [ ] **"Active Cases:"** section shows message: *"No active cases. Create a new alert to begin."*
- [ ] **"Filter by Severity:"** dropdown shows options:
  - [ ] Critical (checked)
  - [ ] High (checked)
  - [ ] Medium (unchecked)
  - [ ] Low (unchecked)

**Expected result:**
```
📥 Alert Queue Management
┌─────────────┬──────────┐
│  ➕ New     │  🔄 Ref  │
│   Alert     │  resh    │
└─────────────┴──────────┘

📋 Active Cases:
No active cases. Create a new alert to begin.

🔍 Filter by Severity:
☑ Critical  ☑ High  ☐ Medium  ☐ Low
```

---

### ✅ TEST 3: Alert Intake Form

**Action:** Click "➕ New Alert" button

**What to verify:**
- [ ] Form displays with title: **"🚨 Alert Intake & Investigation"**
- [ ] Form subtitle: *"Submit a new security alert or anomaly for investigation."*

#### Form Fields (Left Column):
- [ ] **Alert Title** field (pre-filled: "Suspicious SSH Login Pattern")
- [ ] **Severity Level** dropdown (options: critical, high, medium, low)
  - [ ] Default: "critical"

#### Form Fields (Right Column):
- [ ] **Extracted IOC: IP Address** field (pre-filled: "198.51.100.23")
- [ ] **Alert Source** dropdown (options: EDR, SIEM, IDS/IPS, Manual, Other)
  - [ ] Default: "EDR"

#### Form Fields (Full Width):
- [ ] **Raw Alert Payload** textarea (height=120 lines)
  - [ ] Pre-filled with sample alert text

#### Form Fields (3 Columns):
- [ ] **Domains (comma-separated)** field
- [ ] **File Hashes (comma-separated)** field
- [ ] **User Accounts (comma-separated)** field

#### Form Actions:
- [ ] **🔍 Investigate** button (primary/blue, full width)

**Test Action:** Fill form and submit
```
Alert Title: Test SSH Attack
Severity: critical
IP Address: 192.168.1.100
Alert Source: EDR
Raw Payload: SSH brute force detected from suspicious IP
Domains: evil.com
File Hashes: abc123def456
User Accounts: admin
Click: 🔍 Investigate
```

**Expected result:**
- [ ] Spinner appears: "⏳ Initializing SOC workflow..."
- [ ] Form closes
- [ ] Page reloads with active case investigation view

---

### ✅ TEST 4: Live Pipeline Visualization (6-Step Stepper)

**After submitting alert, verify:**

**Pipeline Steps:**
1. [ ] 👨‍💼 **SOC Manager** - "Intake & Triage"
2. [ ] 🔎 **Alert Analyst** - "Deep Analysis"
3. [ ] 🎯 **Threat Hunter** - "Threat Hunt"
4. [ ] ✓ **Compliance** - "Compliance Check"
5. [ ] 📋 **Reporter** - "Final Report"
6. [ ] ✋ **Approval** - "Human Review"

**Stepper Visual Elements:**
- [ ] Each step has a **circle icon** with step number (1,2,3...) or emoji
- [ ] Active step circle is **BLUE** with animated effect
- [ ] Completed steps are **GREEN** with checkmark ✓
- [ ] Pending steps are **GRAY** with number
- [ ] **Connecting lines** between steps:
  - [ ] Green when completed
  - [ ] Gray when pending
- [ ] Step names are **UPPERCASE**
- [ ] Description text appears below each step

**Example:**
```
┌─────┐         ┌─────┐         ┌─────┐
│  1  │────────│  2  │────────│  3  │
│ SOC │ GREEN  │ANALYST│ACTIVE │HUNTER│
└─────┘  LINE   └─────┘        └─────┘
(Completed)     (Active)       (Pending)
```

---

### ✅ TEST 5: Investigation Tab (Default Tab)

**What to verify when pipeline is running:**

#### Case Header Section:
- [ ] Case title displays (e.g., "Test SSH Attack")
- [ ] Incident ID displays (e.g., "INC-ABC12345")
- [ ] Severity badge shows correct color:
  - [ ] Critical = RED badge
  - [ ] High = ORANGE badge
  - [ ] Medium = GOLD badge
  - [ ] Low = GREEN badge

#### Metrics Dashboard (4-Column Grid):
- [ ] **Current Status** box:
  - [ ] Label: "CURRENT STATUS"
  - [ ] Value: Current workflow status (e.g., "Triaged", "Investigating")
- [ ] **Triage Category** box:
  - [ ] Label: "TRIAGE CATEGORY"
  - [ ] Value: Category (e.g., "Suspicious", "Benign", "Malicious", "Unknown")
- [ ] **Triage Confidence** box:
  - [ ] Label: "TRIAGE CONFIDENCE"
  - [ ] Value: Percentage (e.g., "85%") or "—"
- [ ] **Risk Score** box:
  - [ ] Label: "RISK SCORE"
  - [ ] Value: Score out of 10 (e.g., "7.2/10") or "—"

#### Alert Summary Card:
- [ ] Dark card with border
- [ ] Contains raw alert text submitted
- [ ] Text is readable, formatted as paragraph

#### Triage Analysis Section (if available):
- [ ] **"ANALYST NOTES"** header
- [ ] Contains analyst's triage findings

#### Threat Hunt Findings (if available):
- [ ] **"HUNT SUMMARY"** header
- [ ] Summary paragraph text
- [ ] **"KEY FINDINGS"** sub-section
- [ ] Findings displayed as bullet list (not raw JSON)

---

### ✅ TEST 6: Evidence Tab

**Click the "📊 Evidence" tab**

**What to verify:**

#### Extracted IOCs Section:
- [ ] **🌐 IP Addresses** section:
  - [ ] Displays as styled tags/badges (not raw list)
  - [ ] Each IP shows: 🌐 **192.168.1.100**
  - [ ] Format: `<icon> <value>`
- [ ] **🔗 Domains** section:
  - [ ] Each domain shows: 🔗 **evil.com**
  - [ ] Format: `<icon> <value>`
- [ ] **🔐 File Hashes** section:
  - [ ] Each hash shows: 🔐 **abc123def456...**
  - [ ] Hash is truncated if long
  - [ ] Format: `<icon> <truncated_value>`
- [ ] **👤 User Accounts** section:
  - [ ] Each account shows: 👤 **admin**
  - [ ] Format: `<icon> <value>`

#### MITRE ATT&CK Mapping:
- [ ] **Tactics** sub-section:
  - [ ] Header: "Tactics:"
  - [ ] Each tactic displays as card with 🎯 icon
  - [ ] Example: 🎯 **Initial Access**
  - [ ] Blue left border accent
- [ ] **Techniques** sub-section:
  - [ ] Header: "Techniques:"
  - [ ] Each technique displays as card with ⚙️ icon
  - [ ] Example: ⚙️ **T1566.002 - Phishing: Spearphishing Link**
  - [ ] Orange left border accent

#### Risk Assessment:
- [ ] Card with narrative text describing risk level
- [ ] No raw JSON output visible

**IMPORTANT:** No raw JSON anywhere (e.g., NOT like `{"ip": "192.168.1.100", "severity": "high"}`)

---

### ✅ TEST 7: Compliance Tab

**Click the "📋 Compliance" tab**

**What to verify:**

#### Compliance Status Indicator:
- [ ] Status badge displays with color coding:
  - [ ] PENDING = Blue badge
  - [ ] PASSED = Green badge
  - [ ] FAILED = Orange badge
  - [ ] BLOCKED = Red badge
- [ ] Label: "COMPLIANCE STATUS"

#### Compliance Findings:
- [ ] Each finding displayed as a styled card (NOT raw JSON)
- [ ] Contains readable text

#### Required Fields Check:
- [ ] Status indicator:
  - [ ] If all present: ✓ **All Required Fields Present** (green badge)
  - [ ] If missing: ⚠️ **Missing N Required Fields** (orange badge)
- [ ] List of missing fields (if any):
  - [ ] Displayed as bullet points
  - [ ] Each field name in code format: `field_name`

#### Self-Healing & Revision Timeline:
- [ ] **"Revision & Self-Healing Timeline"** header
- [ ] Timeline items displayed chronologically with:
  - [ ] Colored dot indicator (left-aligned)
  - [ ] **Action Title** (e.g., "Rejected by Threat Hunter")
  - [ ] **Reason/Feedback** text
  - [ ] **Timestamp** (e.g., "2026-09-02 12:30:45")
  - [ ] Left border accent:
    - [ ] RED for "Rejected" actions
    - [ ] GREEN for "Approved" actions
    - [ ] BLUE for neutral actions

**Example Timeline:**
```
🔴 ← Rejected by Threat Hunter
     Insufficient evidence provided
     2026-09-02 12:25:10

🟢 ← Approved by Compliance Auditor
     All fields complete
     2026-09-02 12:30:45

🔵 ← Revision Requested
     Please add more IOC context
     2026-09-02 12:35:20
```

---

### ✅ TEST 8: Final Report Tab

**Click the "📄 Report" tab**

**What to verify:**

#### Report Header:
- [ ] Large header banner with gradient background
- [ ] Color gradient matches severity:
  - [ ] Critical = Red gradient
  - [ ] High = Orange gradient
  - [ ] Medium = Gold gradient
  - [ ] Low = Green gradient
- [ ] Case title displayed prominently (28px font)
- [ ] Severity label shown (e.g., "CRITICAL")

#### Executive Summary Section:
- [ ] Header: "EXECUTIVE SUMMARY"
- [ ] Narrative text describing the incident (NOT raw JSON)

#### Timeline & Evidence Section:
- [ ] Two-column layout:
  - [ ] **Left column: "Triage Results"** card
  - [ ] **Right column: "Threat Hunt Summary"** card
- [ ] Each card contains readable text

#### Recommended Remediation Section:
- [ ] Header: "RECOMMENDED REMEDIATION"
- [ ] Bulleted or numbered list of actions (NOT raw JSON)

#### MITRE ATT&CK Coverage Section:
- [ ] Header: "MITRE ATT&CK COVERAGE"
- [ ] Narrative text or formatted list

#### Download Buttons:
- [ ] **📥 Download as Markdown** button:
  - [ ] Click to download `.md` file
  - [ ] File name format: `incident_report_INC-ABC12345.md`
  - [ ] File contains formatted report text
- [ ] **💾 Download as JSON** button:
  - [ ] Click to download `.json` file
  - [ ] File name format: `incident_report_INC-ABC12345.json`
  - [ ] File contains structured JSON data

---

### ✅ TEST 9: HITL (Human-in-the-Loop) Approval Panel

**Trigger condition:** When pipeline reaches "awaiting_human_approval" status

**What to verify on Investigation tab:**

#### Alert Banner:
- [ ] Red/orange warning banner appears
- [ ] Header: "✋ Action Required: Human Approval"
- [ ] Message: *"The incident analysis is complete. Review the report and provide your decision to proceed."*

#### Action Buttons (3 buttons in a row):
- [ ] **✅ Approve & Escalate** (blue/primary button)
  - [ ] Click shows spinner: "Processing approval..."
  - [ ] On success: "Approved! Escalating incident..."
  - [ ] Page reloads
- [ ] **❌ Reject & Close** (secondary button)
  - [ ] Click shows spinner: "Processing rejection..."
  - [ ] On success: "Incident rejected and closed."
  - [ ] Page reloads
- [ ] **⏸ Hold for Review** (secondary button)
  - [ ] Click shows spinner: "Holding case..."
  - [ ] On success: "Case held for further review."
  - [ ] Page reloads

**Test Action:**
1. Wait for case to reach approval stage
2. Review the Final Report tab
3. Click one of the three action buttons
4. Verify response appears and page updates

---

### ✅ TEST 10: Case Queue Persistence (If Multiple Cases)

**Action:** Submit 2-3 different alerts in succession

**What to verify:**
- [ ] Each case gets unique incident ID (INC-ABC12345, INC-XYZ67890)
- [ ] Case queue in sidebar shows most recent at top
- [ ] Each queue item shows:
  - [ ] Timestamp (relative, e.g., "5 mins ago")
  - [ ] Case title
  - [ ] Severity badge (color-coded)
  - [ ] Status badge
- [ ] Cases persist across page refreshes (session state)

**Example Queue Display:**
```
Active Cases:
┌──────────────────────────────┐
│ 2 mins ago                   │
│ Test SSH Attack              │
│ [CRITICAL] [INVESTIGATING]   │
└──────────────────────────────┘
┌──────────────────────────────┐
│ 15 mins ago                  │
│ Suspicious Domain Access     │
│ [HIGH] [AWAITING APPROVAL]   │
└──────────────────────────────┘
```

---

### ✅ TEST 11: Error Handling

**What to test:**
- [ ] Submit form with empty required fields → Error message appears
- [ ] Invalid IP format → Validation error
- [ ] Network timeout during graph execution → Error displayed gracefully
- [ ] Agent failure → Error card shows in Investigation tab

**Expected behavior:**
- [ ] Errors display in readable format (NOT stack traces)
- [ ] Suggest corrective action
- [ ] Allow retry

---

### ✅ TEST 12: Responsive Design

**Test on different screen sizes:**
- [ ] Desktop (1920x1080)
  - [ ] All 4 metrics in grid view
  - [ ] Sidebar visible
  - [ ] Tabs displayed horizontally
- [ ] Laptop (1366x768)
  - [ ] Layout adapts, all elements visible
- [ ] Tablet (768x1024)
  - [ ] Sidebar collapses or minimizes
  - [ ] Metrics stack vertically

---

### ✅ TEST 13: Color & Styling Verification

**Verify color scheme:**
- [ ] Background: Dark gray `#0E1117`
- [ ] Secondary BG: `#161B22`
- [ ] Border/divider: `#30363D`
- [ ] Text primary: Light gray `#C9D1D9`
- [ ] Text secondary: Medium gray `#8B949E`
- [ ] Accent blue: `#58A6FF` (headers, active elements)
- [ ] Accent green: `#238636` (success, low severity)
- [ ] Accent orange: `#D29922` (high severity)
- [ ] Accent red: `#DA3633` (critical severity)

**Badges:**
- [ ] Critical = Red text on dark red semi-transparent background
- [ ] High = Orange text on dark orange semi-transparent background
- [ ] Medium = Gold text on dark gold semi-transparent background
- [ ] Low = Green text on dark green semi-transparent background

---

## AUTOMATED TEST SCRIPTS

Pre-built test scripts available in `scripts/`:

### Test 1: Workflow Graph
```bash
uv run python scripts/test_step7.py
```
**Verifies:** Graph structure, node execution, state transitions

### Test 2: Streaming Graph
```bash
uv run python scripts/test_step7_stream.py
```
**Verifies:** Event streaming, real-time progress updates

### Test 3: MCP Tools
```bash
uv run python scripts/test_mcp_tools.py
```
**Verifies:** IP reputation lookup, MITRE technique retrieval

### Test 4: HITL Approval
```bash
uv run python scripts/test_hitl.py
```
**Verifies:** Human approval checkpoint, state pausing/resuming

### Test 5: Compliance Validation
```bash
uv run python scripts/test_compliance_validation.py
```
**Verifies:** Field requirements, compliance checks

**Run all tests:**
```bash
for test in scripts/test_*.py; do
  echo "Running $test..."
  uv run python "$test"
  echo "✓ Passed\n"
done
```

---

## MANUAL END-TO-END TEST SCENARIO

### Scenario: Suspicious SSH Brute Force Attack

**Setup:**
1. Start Streamlit: `uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py`
2. Open browser: `http://localhost:8501`

**Steps:**

#### 1. Alert Submission
- Click "➕ New Alert"
- Fill form:
  ```
  Title: SSH Brute Force Attack Detected
  Severity: critical
  Alert Source: EDR
  Raw Payload: Multiple failed SSH login attempts (127) from IP 203.0.113.42 
               targeting root@prod-db-01 over 10 minutes, followed by one 
               successful authentication. Attacker installed persistence via 
               cron job. Detection triggered at 2026-09-02 14:32:10 UTC.
  IP Address: 203.0.113.42
  Domains: attacker-c2.evil.com
  File Hashes: 5d41402abc4b2a76b9719d911017c592
  User Accounts: root
  ```
- Click "🔍 Investigate"

#### 2. Monitor Pipeline
- Watch stepper progress:
  - SOC Manager → Alert Analyst → Threat Hunter → Compliance → Reporter → Approval
- Each step should animate/highlight as it executes
- Check "Investigation" tab for progress updates

#### 3. Review Evidence
- Click "📊 Evidence" tab
- Verify:
  - [ ] IP 203.0.113.42 displays as tag
  - [ ] Domain attacker-c2.evil.com shows
  - [ ] File hash shows (truncated)
  - [ ] User root displayed
  - [ ] MITRE techniques mapped (e.g., T1110 - Brute Force)

#### 4. Check Compliance
- Click "📋 Compliance" tab
- Verify:
  - [ ] Compliance status shows
  - [ ] Any required fields listed
  - [ ] Revision history (if any rejections occurred)

#### 5. Review Report
- Click "📄 Report" tab
- Verify:
  - [ ] Professional formatted report
  - [ ] Severity banner (red for critical)
  - [ ] Executive summary (readable text, not JSON)
  - [ ] Timeline & Evidence sections
  - [ ] Remediation recommendations

#### 6. Download Report
- Click "📥 Download as Markdown"
- Verify:
  - [ ] File downloads as `incident_report_INC-XXXXX.md`
  - [ ] Open in text editor
  - [ ] Content is formatted Markdown (readable)
- Click "💾 Download as JSON"
- Verify:
  - [ ] File downloads as `incident_report_INC-XXXXX.json`
  - [ ] Contains structured JSON data

#### 7. HITL Approval
- Monitor status or wait for approval prompt
- When ready, click "✅ Approve & Escalate"
- Verify:
  - [ ] Spinner appears
  - [ ] Status updates
  - [ ] Case marked as escalated/closed

---

## TROUBLESHOOTING

### App Won't Start
```bash
# Check Python version
python --version  # Should be 3.13+

# Reinstall dependencies
uv sync

# Try different port
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py --server.port=8502
```

### Port Already in Use
```bash
# On Linux/Mac
lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs kill -9

# On Windows (PowerShell)
Get-Process | Where-Object {$_.Handles -match "8501"} | Stop-Process -Force
```

### Graph Execution Hangs
- Check Groq API key is set: `echo $GROQ_API_KEY`
- Verify internet connection
- Check ChromaDB is accessible
- Increase timeout: Edit `streamlit_app.py`, change `recursion_limit` from 100 to 200

### UI Not Loading
- Clear browser cache: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
- Hard refresh: Ctrl+F5 (or Cmd+Shift+R on Mac)
- Try incognito/private window

### Raw JSON Appearing in UI
- This should NOT happen. If it does, report the specific location
- Expected: All data rendered as styled cards, tags, tables
- Unexpected: `{"key": "value"}` visible in UI

---

## SUCCESS CRITERIA CHECKLIST

✅ **All items should have checkmarks when complete:**

- [ ] App launches without errors
- [ ] Dark theme loads correctly
- [ ] FalconStream header visible with status indicators
- [ ] Alert intake form works (submits case)
- [ ] 6-step pipeline visualizes correctly
- [ ] Investigation tab shows metrics and analysis
- [ ] Evidence tab shows IOCs as styled tags (no raw JSON)
- [ ] MITRE techniques displayed with color coding
- [ ] Compliance tab shows status and revision timeline
- [ ] Final report tab displays professional formatted report
- [ ] Download buttons work (Markdown and JSON)
- [ ] HITL approval panel appears and buttons function
- [ ] Case queue shows multiple cases
- [ ] Error messages are clear and helpful
- [ ] Styling is professional and consistent
- [ ] No Streamlit branding visible
- [ ] All colors match spec (dark theme with accent colors)
- [ ] All 5 agent functions properly (Manager, Analyst, Hunter, Auditor, Reporter)
- [ ] Graph state persists across page refreshes
- [ ] Responsive layout works on different screen sizes

---

## SIGN-OFF

**If all checkmarks above are complete, the project is production-ready.**

```
Project: SOC Agent Workforce
Status: ✅ COMPLETE
Version: 1.0.0
Last Updated: 2026-09-02
All 9 implementation steps finished.
Streamlit UI fully functional and professional.
Ready for end-user testing and deployment.
```
