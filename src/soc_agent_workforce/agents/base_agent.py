from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langsmith import traceable

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from soc_agent_workforce.state import SOCState


class _FallbackLLM:
    """Deterministic local fallback used when no Groq API key is configured."""

    def invoke(self, messages: list[Any]) -> Any:
        content = messages[-1].content if messages else ""
        content_lower = str(content).lower()
        if "triage" in content_lower or "malicious" in content_lower:
            result = "The alert is suspicious and aligns with credential-access or execution tactics."
        elif "review" in content_lower or "hunter" in content_lower:
            result = "The review found enough evidence to continue forward with a documented hunting summary."
        elif "report" in content_lower:
            result = "The incident report is complete and contains the required summary and evidence fields."
        else:
            result = "The workflow step completed successfully."
        return SimpleNamespace(content=result)


class BaseAgent:
    """Shared abstraction for all SOC workflow agents."""

    agent_name: str = "base_agent"
    system_prompt: str = "You are a helpful SOC analysis agent."

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.llm = ChatGroq(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.2,
            )
        else:
            self.llm = _FallbackLLM()

    def _traceable_call(self, prompt: str) -> str:
        @traceable(name=self.agent_name)
        def _wrapped() -> str:
            return self._call_llm(prompt)

        return _wrapped()

    def _call_llm(self, prompt: str) -> str:
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content if hasattr(response, "content") else str(response)

    def read_state(self, state: SOCState, field: str) -> Any:
        return getattr(state, field)

    def write_state(self, state: SOCState, field: str, value: Any) -> None:
        setattr(state, field, value)

    def update_state(self, state: SOCState, **updates: Any) -> SOCState:
        for key, value in updates.items():
            setattr(state, key, value)
        return state
