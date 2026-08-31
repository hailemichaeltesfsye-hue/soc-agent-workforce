from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SOCState(BaseModel):
    """Shared workflow state for the SOC agent workforce."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    incident_id: str
    case_title: str | None = None
    source: Literal["manual", "streamlit", "api", "ingest", "simulator"] = "manual"
    severity: Literal["low", "medium", "high", "critical"] | None = None
    status: Literal[
        "new",
        "triaged",
        "awaiting_human_approval",
        "reopened",
        "escalated",
        "closed",
        "needs_revision",
        "revision_requested",
        "blocked",
    ] = "new"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = None
    investigation_priority: Literal["routine", "urgent", "critical"] = "routine"

    alert_summary: str | None = None
    alert_source_system: str | None = None
    alert_id: str | None = None
    raw_event_context: dict[str, Any] | None = None

    ip_addresses: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    hashes: list[str] = Field(default_factory=list)
    user_accounts: list[str] = Field(default_factory=list)
    endpoint_names: list[str] = Field(default_factory=list)

    triage_notes: str | None = None
    triage_confidence: float | None = None
    triage_category: Literal["benign", "suspicious", "malicious", "unknown"] | None = None
    triage_reasoning: list[str] = Field(default_factory=list)
    triage_evidence: list[str] = Field(default_factory=list)
    triage_revisions: int = 0
    triage_revision_history: list[dict[str, Any]] = Field(default_factory=list)

    threat_hunt_summary: str | None = None
    threat_hunt_findings: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    mitre_tactics: list[str] = Field(default_factory=list)
    suspicious_behavior_summary: str | None = None
    entity_risk_score: float | None = None
    risk_assessment: str | None = None

    compliance_status: Literal["pending", "passed", "failed", "blocked"] = "pending"
    compliance_findings: list[str] = Field(default_factory=list)
    required_fields_present: bool = False
    required_fields_missing: list[str] = Field(default_factory=list)
    compliance_retry_count: int = 0
    compliance_max_retries: int = 3

    incident_report: dict[str, Any] | None = None
    report_ready_for_review: bool = False
    report_approval_status: Literal["pending", "approved", "rejected", "not_required"] = "pending"
    approval_reviewer: str | None = None
    approval_notes: str | None = None

    escalation_target: str | None = None
    escalation_reason: str | None = None
    final_decision: Literal["escalate", "close", "reopen", "request_revision", "hold"] | None = None
    human_in_the_loop_required: bool = True

    self_healing_retry_count: int = 0
    self_healing_max_retries: int = 3
    self_healing_status: Literal[
        "inactive",
        "pending_review",
        "rejected",
        "accepted",
        "max_retries_reached",
    ] = "inactive"
    reviewer_feedback: str | None = None

    final_summary: str | None = None
    evidence_links: list[str] = Field(default_factory=list)
    related_incidents: list[str] = Field(default_factory=list)
    memory_references: list[str] = Field(default_factory=list)

    created_by: str | None = None
    assigned_to: str | None = None
    last_agent: str | None = None

    agent_trace_ids: dict[str, str] = Field(default_factory=dict)
    tool_trace_ids: dict[str, str] = Field(default_factory=dict)

    notes: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
