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
