from __future__ import annotations

from pydantic import BaseModel, Field


class Incident(BaseModel):
    service: str
    title: str
    severity: str = Field(pattern="^(sev1|sev2|sev3|sev4)$")
    alerts: list[str] = Field(default_factory=list)
    logs: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    recent_changes: list[str] = Field(default_factory=list)


class RunbookSection(BaseModel):
    id: str
    service: str
    title: str
    severity: str
    keywords: list[str]
    symptoms: list[str]
    checks: list[str]
    actions: list[str]
    escalation: str


class MatchedSection(BaseModel):
    id: str
    title: str
    score: float
    matched_terms: list[str]


class GeneratedRunbook(BaseModel):
    service: str
    title: str
    severity: str
    confidence: float
    summary: str
    likely_cause: str
    immediate_checks: list[str]
    recommended_actions: list[str]
    escalation: str
    evidence: list[str]
    matched_sections: list[MatchedSection]
    risk_flags: list[str]
    redaction_count: int
    status: str


class ReviewFinding(BaseModel):
    code: str
    severity: str = Field(pattern="^(info|warn|blocker)$")
    message: str
    recommendation: str


class RunbookReview(BaseModel):
    service: str
    title: str
    severity: str
    decision: str = Field(pattern="^(approve|review|block)$")
    readiness_score: int
    summary: str
    findings: list[ReviewFinding]
    required_human_approval: bool


class RunbookHistoryWindow(BaseModel):
    run_id: str
    generated_at: str
    runbook: GeneratedRunbook


class ReviewedRunbookWindow(BaseModel):
    run_id: str
    generated_at: str
    service: str
    severity: str
    confidence: float
    decision: str
    readiness_score: int
    redaction_count: int
    finding_codes: list[str]


class RunbookHistoryReview(BaseModel):
    status: str = Field(pattern="^(pass|review|block)$")
    reviewed_windows: int
    blocked_windows: int
    review_windows: int
    approval_required_windows: int
    total_redactions: int
    latest_decision: str
    latest_service: str
    summary: str
    windows: list[ReviewedRunbookWindow]
    recommendations: list[str]


class ExecutionStep(BaseModel):
    step_id: str
    action: str
    owner: str = ""
    status: str = Field(pattern="^(pending|completed|skipped)$")
    expires_at: str
    evidence: list[str] = Field(default_factory=list)


class ExecutionManifest(BaseModel):
    incident_id: str
    service: str
    runbook_id: str
    reference_time: str
    steps: list[ExecutionStep]


class ExecutionFinding(BaseModel):
    code: str
    step_id: str
    severity: str = Field(pattern="^(warn|blocker)$")
    message: str


class ExecutionReview(BaseModel):
    incident_id: str
    service: str
    runbook_id: str
    status: str = Field(pattern="^(verified|blocked)$")
    reviewed_steps: int
    completed_steps: int
    open_steps: int
    expired_steps: int
    findings: list[ExecutionFinding]
    summary: str
