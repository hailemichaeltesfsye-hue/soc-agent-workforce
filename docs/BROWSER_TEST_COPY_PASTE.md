# 🌐 BROWSER TESTING WALKTHROUGH — Copy & Paste Version

## BEFORE YOU START
```bash
# Terminal 1: Start the app
cd "c:\Users\pavilion\Documents\Agentic Engineering Course\module-5\soc-agent-workforce"
export GROQ_API_KEY="your-groq-api-key-here"
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py

# Wait for output:
# "You can now view your Streamlit app in your browser"
# "Local URL: http://localhost:8501"
```

```bash
# Terminal 2: Keep terminal open for logs
# (You can watch this to see graph execution progress)
```

## IN BROWSER

### STEP 1: Load Dashboard
```
URL: http://localhost:8501
Expected: Dark dashboard loads, no errors
```

---

## TEST 1: VERIFY HEADER & SIDEBAR

### Check Header Bar
**You should see:**
```
┌──────────────────────────────────────────────────┐
│  ⚡ FalconStream         🟢 Groq: Online         │
│                         🟢 ChromaDB: Connected   │
└──────────────────────────────────────────────────┘
```

✅ **Verify:**
- [ ] ⚡ FalconStream logo visible
- [ ] Two green dots with labels
- [ ] Dark background
- [ ] Blue text color for "FalconStream"

### Check Sidebar
**Left side should show:**
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

✅ **Verify:**
- [ ] Two blue buttons at top
- [ ] "No active cases" message
- [ ] Severity checkboxes

---

## TEST 2: SUBMIT ALERT FORM

### Click "➕ New Alert" Button

**Form appears with:**

#### Top section (2 columns):
```
Left Column:
┌──────────────────────────┐
│ Alert Title              │
│ ├─ Suspicious SSH...     │
│                          │
│ Severity Level           │
│ └─ [critical ▼]          │
└──────────────────────────┘

Right Column:
┌──────────────────────────┐
│ Extracted IOC: IP        │
│ ├─ 198.51.100.23         │
│                          │
│ Alert Source             │
│ └─ [EDR ▼]               │
└──────────────────────────┘
```

#### Middle section (Raw alert payload textarea)

#### Bottom section (3 fields)
```
│ Domains          │ File Hashes      │ User Accounts    │
│ (comma-sep)      │ (comma-sep)      │ (comma-sep)      │
```

✅ **Verify:**
- [ ] All 7 form fields visible
- [ ] Pre-filled with defaults
- [ ] "🔍 Investigate" button blue

### FILL OUT THE FORM

Copy & paste this into each field:

**Alert Title:**
```
Suspicious SSH Brute Force - Production DB Server
```

**Severity Level:**
```
Select: critical
```

**IP Address:**
```
203.0.113.42
```

**Alert Source:**
```
Select: EDR
```

**Raw Alert Payload:**
```
ALERT: SSH_BRUTE_FORCE_ATTACK
Timestamp: 2026-09-02 14:32:10 UTC
Source IP: 203.0.113.42
Target: prod-db-01.company.com (10.0.1.50)
Target User: root@prod-db-01

Details:
- 127 failed SSH login attempts over 10 minutes
- Attempts targeting root user account
- Various SSH key combinations tested
- Successful authentication at 14:42:05 UTC
- Suspicious: Attacker installed persistence via cron job
  * Entry found: */5 * * * * /tmp/.cache/agent
  * Script created: 2026-09-02 14:42:15 UTC

Threat Score: 9.8/10
Recommended Action: Immediate response required
```

**Domains:**
```
attacker-c2.evil.com, malware-payload.net
```

**File Hashes:**
```
5d41402abc4b2a76b9719d911017c592, 6512bd43d9caa6e02c990b0a82652dca
```

**User Accounts:**
```
root, admin, db_service
```

✅ **Verify:**
- [ ] All fields filled
- [ ] Severity shows "critical" (red)
- [ ] Text is readable

### CLICK "🔍 Investigate"

**Expected behavior:**
```
1. Spinner appears: "⏳ Initializing SOC workflow..."
2. Form closes after 2-3 seconds
3. New view loads with:
   - Case title at top
   - Incident ID (INC-XXXXXXXX)
   - 6-step stepper
   - Tab navigation (4 tabs)
```

✅ **Verify:**
- [ ] Spinner appeared
- [ ] No errors in console
- [ ] New investigation view loads
- [ ] Stepper visible with 6 steps

---

## TEST 3: WATCH PIPELINE VISUALIZATION

**You should see the 6-step stepper:**

### Expected progression (over 30-60 seconds):

**Initial state:**
```
┌─────┐       ┌─────┐       ┌─────┐       ┌─────┐       ┌─────┐       ┌─────┐
│  1  │───────│  2  │───────│  3  │───────│  4  │───────│  5  │───────│  6  │
│ SOC │       │ANALYST     │HUNTER│       │COMP │       │REP  │       │APP  │
└─────┘       └─────┘       └─────┘       └─────┘       └─────┘       └─────┘
✓ Completed   ◉ Active     ○ Pending    ○ Pending     ○ Pending      ○ Pending
  GREEN       BLUE         GRAY         GRAY          GRAY           GRAY
```

**As it progresses:**
```
Step 1 → Step 2: SOC Manager completes → Alert Analyst starts
Step 2 → Step 3: Alert Analyst completes → Threat Hunter starts
Step 3 → Step 4: Threat Hunter completes → Compliance starts
Step 4 → Step 5: Compliance completes → Reporter starts
Step 5 → Step 6: Reporter completes → Approval (HITL)
```

**Each step animation:**
- Current active step circle is **BLUE** with glow effect
- Completed steps show **GREEN ✓**
- Connecting lines turn **GREEN** as completed
- Step description text colored to match

✅ **Verify:**
- [ ] Stepper visible and animated
- [ ] Colors change as steps progress
- [ ] No stuck/frozen steps
- [ ] Eventually reaches "Approval" step

---

## TEST 4: CHECK INVESTIGATION TAB (Default)

### After pipeline starts, verify Investigation tab shows:

**Case Header:**
```
"Suspicious SSH Brute Force - Production DB Server"
(INC-ABC12345)
[CRITICAL] ← Red severity badge
```

**Metrics Dashboard (4 boxes in a row):**
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ CURRENT      │ TRIAGE       │ TRIAGE       │ RISK         │
│ STATUS       │ CATEGORY     │ CONFIDENCE   │ SCORE        │
│              │              │              │              │
│ Triaged      │ Suspicious   │ 87%          │ 8.3/10       │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

✅ **Verify:**
- [ ] Case title at top
- [ ] Severity badge (RED for critical)
- [ ] 4 metric boxes with values
- [ ] Values populated (not blank)

**Alert Summary Card:**
```
[Dark card with border]
ALERT SUMMARY

Multiple failed SSH login attempts (127) over 10 minutes 
followed by successful authentication from IP 203.0.113.42...
[rest of your alert text]
```

✅ **Verify:**
- [ ] Card displays alert you submitted
- [ ] No raw JSON
- [ ] Readable text format

---

## TEST 5: CLICK "📊 EVIDENCE" TAB

### You should see organized sections:

**Section 1: Extracted IOCs**

```
🌐 IP ADDRESSES
┌──────────────────────────┐
│ 🌐 203.0.113.42          │
└──────────────────────────┘

🔗 DOMAINS
┌──────────────────────────┐
│ 🔗 attacker-c2.evil.com  │
│ 🔗 malware-payload.net   │
└──────────────────────────┘

🔐 FILE HASHES
┌──────────────────────────┐
│ 🔐 5d41402abc4b2a76b... │
│ 🔐 6512bd43d9caa6e0... │
└──────────────────────────┘

👤 USER ACCOUNTS
┌──────────────────────────┐
│ 👤 root                  │
│ 👤 admin                 │
│ 👤 db_service            │
└──────────────────────────┘
```

**IMPORTANT:** Each item is a **styled tag/badge**, NOT raw JSON

❌ **WRONG** (should NOT see):
```
{
  "ip_addresses": ["203.0.113.42"],
  "domains": ["attacker-c2.evil.com"],
  ...
}
```

✅ **CORRECT** (should see):
```
🌐 203.0.113.42
🔗 attacker-c2.evil.com
```

✅ **Verify:**
- [ ] Each IOC has icon + value
- [ ] NO raw JSON visible
- [ ] NO `{...}` notation
- [ ] Icons match type (🌐 for IP, 🔗 for domain, etc.)

**Section 2: MITRE ATT&CK Mapping**

```
🎯 TACTICS
┌──────────────────────────┐
│ 🎯 Initial Access        │
│ 🎯 Persistence           │
│ 🎯 Defense Evasion       │
└──────────────────────────┘
(Blue left border)

⚙️ TECHNIQUES
┌──────────────────────────┐
│ ⚙️ T1110 - Brute Force   │
│ ⚙️ T1098 - Account...    │
│ ⚙️ T1021 - Remote...     │
└──────────────────────────┘
(Orange left border)
```

✅ **Verify:**
- [ ] MITRE techniques display (not empty)
- [ ] Each has icon + text
- [ ] Color-coded borders
- [ ] NO raw JSON or IDs only

---

## TEST 6: CLICK "📋 COMPLIANCE" TAB

### You should see:

**Compliance Status:**
```
┌──────────────────────┐
│ COMPLIANCE STATUS    │
│                      │
│ [PASSED] ← Green     │
└──────────────────────┘
```

Possible values: PENDING (blue), PASSED (green), FAILED (orange), BLOCKED (red)

**Required Fields Check:**
```
✓ All Required Fields Present
```

Or if some missing:
```
⚠ Missing 3 Required Fields

Missing:
- endpoint_name
- alert_source_system
- raw_event_context
```

**Revision & Self-Healing Timeline (if available):**

```
🔴 Rejected by Threat Hunter
   └─ Insufficient evidence provided
      2026-09-02 12:25:10

🟢 Approved by Compliance Auditor
   └─ All fields complete
      2026-09-02 12:30:45

🔵 Revision Requested
   └─ Please add more IOC context
      2026-09-02 12:35:20
```

Each timeline item has:
- Colored dot (red/green/blue)
- Action title
- Reason/message
- Timestamp
- Left border accent matching dot color

✅ **Verify:**
- [ ] Status badge visible (any color)
- [ ] Required fields displayed
- [ ] Timeline items readable (if any)
- [ ] NO raw JSON in timeline

---

## TEST 7: CLICK "📄 REPORT" TAB

### You should see a professionally formatted report:

**Report Header (Large):**
```
┌─────────────────────────────────────────────────────┐
│ ⚠️  Suspicious SSH Brute Force - Production DB...  │
│    Severity: CRITICAL                              │
│                                                     │
│    (Red gradient background)                        │
└─────────────────────────────────────────────────────┘
```

Gradient color depends on severity:
- Critical: RED
- High: ORANGE
- Medium: GOLD
- Low: GREEN

**Executive Summary Section:**
```
EXECUTIVE SUMMARY
─────────────────
A sophisticated SSH brute force attack was detected
targeting the production database server. The attacker
successfully compromised the root account and installed
persistence mechanisms...
[readable narrative text]
```

**Timeline & Evidence (2 columns):**
```
┌─────────────────────────┬─────────────────────────┐
│ Triage Results          │ Threat Hunt Summary     │
│                         │                         │
│ [Card with text]        │ [Card with text]        │
└─────────────────────────┴─────────────────────────┘
```

**Recommended Remediation:**
```
RECOMMENDED REMEDIATION
───────────────────────
1. Immediately terminate SSH sessions
2. Reset root account password
3. Remove malicious cron job from /var/spool/cron
4. Review SSH logs for lateral movement
5. Patch SSH configuration
6. Monitor for related C2 activity
...
```

**Download Buttons:**
```
┌────────────────────────┬────────────────────────┐
│ 📥 Download as         │ 💾 Download as         │
│    Markdown            │    JSON                │
│                        │                        │
│ (Creates .md file)     │ (Creates .json file)   │
└────────────────────────┴────────────────────────┘
```

✅ **Verify:**
- [ ] Report header visible with gradient
- [ ] Executive summary is readable narrative (NOT JSON)
- [ ] Two column cards for timeline
- [ ] Remediation shows as list (NOT JSON)
- [ ] Download buttons present
- [ ] NO raw JSON in report sections

**Test downloads:**
1. Click "📥 Download as Markdown"
   - File saves: `incident_report_INC-XXXXX.md`
   - Open in text editor
   - Should show readable Markdown format

2. Click "💾 Download as JSON"
   - File saves: `incident_report_INC-XXXXX.json`
   - Open in text editor
   - Should show structured JSON (for archival)

---

## TEST 8: TEST HITL APPROVAL (If Applicable)

**If pipeline reaches approval stage, on Investigation tab you'll see:**

```
╔════════════════════════════════════════════════════╗
║ ✋ Action Required: Human Approval                 ║
║                                                    ║
║ The incident analysis is complete. Review the     ║
║ report and provide your decision to proceed.      ║
║                                                    ║
║ ┌──────────────┬──────────────┬──────────────┐   ║
║ │ ✅ Approve & │ ❌ Reject &  │ ⏸ Hold for  │   ║
║ │ Escalate     │ Close        │ Review       │   ║
║ └──────────────┴──────────────┴──────────────┘   ║
╚════════════════════════════════════════════════════╝
```

**Test clicking each button:**

1. **Click ✅ Approve & Escalate**
   - Spinner: "Processing approval..."
   - Success: "Approved! Escalating incident..."
   - Page reloads
   - Status updates to "escalated"

2. **Click ❌ Reject & Close**
   - Spinner: "Processing rejection..."
   - Success: "Incident rejected and closed."
   - Page reloads
   - Status updates to "closed"

3. **Click ⏸ Hold for Review**
   - Spinner: "Holding case..."
   - Success: "Case held for further review."
   - Page reloads
   - Status updates to "awaiting_review"

✅ **Verify:**
- [ ] Alert banner appears when needed
- [ ] Three buttons responsive
- [ ] Spinner shows on click
- [ ] Success message displays
- [ ] Page reloads after action

---

## FINAL CHECKLIST

Mark these as you go:

### Layout & Styling
- [ ] Dark theme throughout (#0E1117 background)
- [ ] Professional enterprise look
- [ ] No visible Streamlit branding (no hamburger menu, footer, built-in header)
- [ ] Responsive layout
- [ ] Fonts are clean and readable (Inter family)

### Functionality
- [ ] Alert form submits successfully
- [ ] 6-step pipeline visualizes and progresses
- [ ] Each tab loads content correctly
- [ ] Evidence displays as tags/cards (NO raw JSON)
- [ ] Report shows formatted text (NO raw JSON)
- [ ] Downloads create files
- [ ] HITL approval works

### Colors
- [ ] Critical severity = RED
- [ ] High severity = ORANGE
- [ ] Medium severity = GOLD
- [ ] Low severity = GREEN
- [ ] Active step = BLUE
- [ ] Completed step = GREEN ✓
- [ ] Pending step = GRAY

### Data Formatting
- [ ] ✅ IP addresses as tags with 🌐 icon
- [ ] ✅ Domains as tags with 🔗 icon
- [ ] ✅ File hashes as tags with 🔐 icon
- [ ] ✅ User accounts as tags with 👤 icon
- [ ] ✅ MITRE tactics with 🎯 icon
- [ ] ✅ MITRE techniques with ⚙️ icon
- [ ] ❌ NO raw JSON visible anywhere
- [ ] ❌ NO `{"key": "value"}` notation
- [ ] ✅ All text readable narrative format

---

## SUCCESS!

If all checkboxes above are marked ✅, then:

```
┌──────────────────────────────────────────────────┐
│  ✅ PROJECT 100% COMPLETE & WORKING             │
│                                                  │
│  ✅ Backend: 6 agents operational               │
│  ✅ Frontend: Professional dashboard             │
│  ✅ Integration: Groq + tools + memory           │
│  ✅ Testing: All scenarios passing               │
│  ✅ UI: Professional enterprise aesthetic        │
│  ✅ No raw JSON: All data formatted              │
│  ✅ HITL: Approval workflow functional           │
│                                                  │
│  STATUS: PRODUCTION READY                        │
└──────────────────────────────────────────────────┘
```

## PROBLEMS?

See these docs:
- **UI_TESTING_GUIDE.md** - Detailed troubleshooting
- **PROJECT_STATUS.md** - Full project status
- **STREAMLIT_SETUP.md** - Setup issues

**Need help?** Check terminal output for errors (may have hints about what failed)
