# SOC Agent Workforce

An AI-powered Security Operations Center pipeline that automates alert triage, threat hunting, and compliance auditing with a Human-In-The-Loop (HITL) approval step.

## How to Run the UI

To start the SOC Analyst Portal (Streamlit Dashboard), run the following command from the root of this project:

```bash
uv run streamlit run src/soc_agent_workforce/app/streamlit_app.py
```

## Environment Setup

Make sure you have populated your `.env` file first based on `.env.example`:

- `GROQ_API_KEY` (Required for LLM processing)
- `ABUSEIPDB_API_KEY` (Required for IP reputation checks)
- `LANGCHAIN_TRACING_V2=true` (Required to stream traces to LangSmith)

## Running Tests

To run the integration and unit tests:

```bash
uv run pytest tests/
```
