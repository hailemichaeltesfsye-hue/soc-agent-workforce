# SOC Agent Workforce

An AI-powered Security Operations Center (SOC) pipeline that automates alert triage, threat hunting, and compliance auditing — with a **Human-In-The-Loop (HITL)** approval step before any action is finalized.

## Overview

Instead of a single monolithic model, incoming security alerts flow through a team of specialized agents that mirror a real SOC's division of labor: triage and analysis, threat hunting, compliance auditing, and incident reporting, coordinated by a SOC manager agent — with MITRE ATT&CK data and IP-reputation lookups feeding the analysis, and a Streamlit dashboard for observability.

## Agents (`src/soc_agent_workforce/agents/`)

| Agent | Role |
|---|---|
| `soc_manager.py` | Coordinates the overall workflow and hands off tasks between agents |
| `alert_analyst.py` | Triages and analyzes incoming alerts |
| `threat_hunter.py` | Investigates suspicious activity and correlates indicators |
| `compliance_auditor.py` | Validates findings and actions against compliance requirements |
| `incident_reporter.py` | Produces the final incident report |
| `base_agent.py` | Shared base class for all agents |

## Stack

- **Python** — agent logic and orchestration (`graph/workflow.py`)
- **MCP (Model Context Protocol)** — custom server (`mcp/server.py`) exposing tools for AbuseIPDB lookups (`abuseipdb_client.py`) and MITRE ATT&CK data (`mitre_dataset.py`)
- **ChromaDB** — vector memory for past incidents and MITRE technique data (`memory/chroma_client.py`, `incident_memory.py`, `mitre_memory.py`)
- **Streamlit** — SOC Analyst Portal dashboard (`app/streamlit_app.py`)
- **uv** — Python package and environment management (`pyproject.toml`, `uv.lock`)
- **LangSmith** (optional) — trace streaming for observability

## Project Structure

```
soc-agent-workforce/
├── data/
│   ├── mitre/
│   │   └── attack_techniques.json     # MITRE ATT&CK technique reference data
│   └── synthetic_alerts.json          # Sample/test alert data
├── docs/
│   ├── architecture.md
│   ├── PLAN.md
│   ├── PROJECT_STATUS.md
│   ├── QUICK_TEST_CARD.md
│   ├── STREAMLIT_SETUP.md
│   ├── UI_TESTING_GUIDE.md
│   ├── DOCUMENTATION_INDEX.md
│   └── BROWSER_TEST_COPY_PASTE.md
├── scripts/
│   ├── bootstrap_chroma.py            # Seeds the ChromaDB vector store
│   ├── load_mitre_data.py             # Loads MITRE ATT&CK data into the system
│   ├── test_compliance_validation.py
│   ├── test_hitl.py
│   ├── test_mcp_tools.py
│   ├── test_step7.py
│   └── test_step7_stream.py
├── src/soc_agent_workforce/
│   ├── agents/
│   │   ├── soc_manager.py
│   │   ├── alert_analyst.py
│   │   ├── threat_hunter.py
│   │   ├── compliance_auditor.py
│   │   ├── incident_reporter.py
│   │   └── base_agent.py
│   ├── app/
│   │   └── streamlit_app.py           # SOC Analyst Portal UI
│   ├── graph/
│   │   └── workflow.py                # Agent workflow / state graph definition
│   ├── mcp/
│   │   ├── server.py                  # MCP server
│   │   ├── abuseipdb_client.py        # IP reputation tool
│   │   └── mitre_dataset.py           # MITRE ATT&CK tool
│   ├── memory/
│   │   ├── chroma_client.py           # ChromaDB connection
│   │   ├── incident_memory.py         # Historical incident memory
│   │   └── mitre_memory.py            # MITRE technique memory
│   └── state.py                       # Shared workflow state
├── tests/
│   └── test_workflow.py
├── .env.example                       # Example environment variables
├── .python-version
├── pyproject.toml                     # Project metadata and dependencies (uv)
└── uv.lock                            # Locked dependency versions
```

## Getting Started

### Prerequisites

- Python (version pinned in `.python-version`)
- [uv](https://github.com/astral-sh/uv) installed

### Installation

```bash
git clone https://github.com/hailemichaeltesfsye-hue/soc-agent-workforce.git
cd soc-agent-workforce
uv sync
```

### Environment Setup

Copy `.env.example` to `.env` and populate:

- `GROQ_API_KEY` — required for LLM processing
- `ABUSEIPDB_API_KEY` — required for IP reputation checks
- `LANGCHAIN_TRACING_V2=true` — required to stream traces to LangSmith (optional)

### How to Run the UI

Start the SOC Analyst Portal (Streamlit dashboard) from the project root:

```bash
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py
```

### Running Tests

Run the integration and unit tests:

```bash
uv run pytest tests/
```

## Author

**Hailemichael Tesfaye Mekuria**
[LinkedIn](https://www.linkedin.com/in/hailemichael-tesfaye-2b7114401/) · [GitHub](https://github.com/hailemichaeltesfsye-hue)
