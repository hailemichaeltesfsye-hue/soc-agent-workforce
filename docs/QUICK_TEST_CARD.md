# 🚀 QUICK TEST REFERENCE CARD

## Copy This Into Your Terminal

### START THE APP
```bash
cd "c:\Users\pavilion\Documents\Agentic Engineering Course\module-5\soc-agent-workforce"
export GROQ_API_KEY="your-api-key-here"
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py
```

### THEN OPEN IN BROWSER
```
http://localhost:8501
```

---

## 5-MINUTE TEST SCENARIO

### 1. SUBMIT ALERT (30 seconds)
```
Click: ➕ New Alert

Fill:
  Title: "Test SSH Brute Force"
  Severity: "critical"
  Alert Source: "EDR"
  Raw Payload: "Multiple failed SSH attempts from 192.168.1.100"
  IP Address: "192.168.1.100"
  Domains: "attacker.evil.com"
  File Hashes: "abc123def456"
  User Accounts: "admin"

Click: 🔍 Investigate
```

### 2. WATCH PIPELINE (2-3 minutes)
```
Watch stepper progress:
  ✓ SOC Manager (completed)
  ◉ Alert Analyst (active, blue)
  ○ Threat Hunter (pending)
  ○ Compliance
  ○ Reporter
  ○ Approval
```

### 3. CHECK EVIDENCE TAB (1 minute)
```
Tab: 📊 Evidence

Verify:
  ☑ IP 192.168.1.100 appears as tag
  ☑ Domain attacker.evil.com shows
  ☑ File hash visible
  ☑ MITRE techniques listed
```

### 4. CHECK REPORT TAB (1 minute)
```
Tab: 📄 Report

Verify:
  ☑ Red severity banner
  ☑ Executive summary text
  ☑ Remediation recommendations
  ☑ Download buttons work
```

### 5. APPROVE CASE (30 seconds)
```
Tab: 🔍 Investigation

When "✋ Action Required" appears:
  Click: ✅ Approve & Escalate

Verify:
  ☑ Spinner appears
  ☑ Status updates
```

---

## CHECKLIST: IS EVERYTHING WORKING?

- [ ] App starts without errors
- [ ] Dark theme loads
- [ ] Header shows FalconStream + status indicators
- [ ] Alert form works
- [ ] 6-step pipeline visualizes
- [ ] Evidence shows as tags (NOT raw JSON)
- [ ] Report displays formatted
- [ ] Download buttons work
- [ ] HITL buttons function
- [ ] No errors in console

**All checked?** → ✅ PROJECT IS COMPLETE

---

## IF SOMETHING BREAKS

### App won't start
```bash
uv sync
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py --server.port=8502
```

### Port 8501 busy
```bash
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py --server.port=8503
```

### Raw JSON appearing (shouldn't happen)
This means a field isn't formatted. Report the location.

### Graph hangs
- Check API key is set
- Check internet connection
- Wait longer (Groq might be rate-limited)

---

## WHAT YOU'RE TESTING

| Component | Where | Expected |
|-----------|-------|----------|
| Dark Theme | Everywhere | #0E1117 background |
| Header | Top | ⚡ FalconStream + 🟢🟢 status |
| Sidebar | Left | Alert queue + filters |
| Form | Main | Alert intake fields |
| Stepper | Above tabs | 6 colored circles |
| Investigation | Tab 1 | Metrics + HITL buttons |
| Evidence | Tab 2 | Tags + MITRE cards |
| Compliance | Tab 3 | Status + timeline |
| Report | Tab 4 | Formatted + download |

---

## TESTING SCENARIOS (Optional)

### Scenario 1: Critical SSH Attack
```
Title: SSH Brute Force Attack
Severity: critical
IP: 203.0.113.42
Domains: attacker-c2.evil.com
User: root
Expected: Red badges, urgent status
```

### Scenario 2: Medium Phishing
```
Title: Suspicious Email Link
Severity: medium
Domains: phishing-site.com
User: user@company.com
Expected: Gold badges, investigation status
```

### Scenario 3: Low Policy Violation
```
Title: USB Device Access
Severity: low
IP: 10.0.0.50
User: employee@company.com
Expected: Green badges, routine priority
```

---

## FILE LOCATIONS (For Reference)

```
Main Dashboard:
  src/soc_agent_workforce/app/streamlit_app.py (1600 lines)

Agents:
  src/soc_agent_workforce/agents/ (6 files)

Workflow:
  src/soc_agent_workforce/graph/workflow.py

Testing:
  scripts/test_*.py (5 test scripts)

Docs:
  UI_TESTING_GUIDE.md (comprehensive)
  PROJECT_STATUS.md (completion summary)
  STREAMLIT_SETUP.md (dashboard setup)
```

---

## API KEYS (Free Tiers)

**Groq** (LLM)
- URL: https://console.groq.com
- Free: Yes, with rate limits
- Setup: Get key, export GROQ_API_KEY

**AbuseIPDB** (IP Reputation)
- URL: https://www.abuseipdb.com
- Free: Yes, limited requests
- Optional: App works without it

**LangSmith** (Tracing - Optional)
- URL: https://smith.langchain.com
- Free: Yes
- Optional: For observability only

---

## SUCCESS INDICATORS

✅ **You'll know it's working when:**
1. Streamlit starts with no errors
2. Dark dashboard loads in browser
3. Form submits without errors
4. Stepper shows 6 steps progressing
5. Evidence displays as styled tags (no raw JSON)
6. Report shows formatted text
7. Download buttons produce files
8. HITL approval works

❌ **Something's wrong if:**
1. Streamlit crashes on startup
2. Raw JSON visible in UI
3. Stepper stuck on one step
4. Buttons don't respond
5. Form rejections aren't explained
6. No API responses (check GROQ_API_KEY)

---

## PROJECT COMPLETION

```
┌──────────────────────────────────────────┐
│ ✅ ALL 9 IMPLEMENTATION STEPS COMPLETE   │
│                                          │
│ Status: PRODUCTION READY                 │
│ Backend: 6-Agent LangGraph               │
│ Frontend: Professional Streamlit UI      │
│ Integration: Groq + AbuseIPDB + MITRE    │
│ Testing: Comprehensive guides included   │
│                                          │
│ Version: 1.0.0                           │
│ Last Updated: 2026-09-02                 │
└──────────────────────────────────────────┘
```

---

## NEED FULL DETAILS?

Read these files for comprehensive info:

📖 **UI_TESTING_GUIDE.md** - 13 complete test scenarios  
📖 **PROJECT_STATUS.md** - Full step-by-step completion summary  
📖 **STREAMLIT_SETUP.md** - Dashboard setup instructions  
📖 **PLAN.md** - Original architecture & design  
📖 **README.md** - Project overview  

---

## DONE? CELEBRATE! 🎉

You have a production-ready SOC analyst platform with:
- 6 intelligent agents
- Self-healing loops
- HITL approval workflow
- Professional enterprise UI
- Complete testing suite
- Full documentation

**All 9 Steps: ✅ COMPLETE**
