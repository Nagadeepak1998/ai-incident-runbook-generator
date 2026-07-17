from __future__ import annotations

import re
from collections import Counter

from runbook_generator.models import Incident, MatchedSection, RunbookSection

TOKEN_RE = re.compile(r"[a-z0-9_]+")


def rank_sections(
    incident: Incident, sections: list[RunbookSection], limit: int = 3
) -> list[MatchedSection]:
    incident_terms = _incident_terms(incident)
    ranked: list[MatchedSection] = []

    for section in sections:
        section_terms = _section_terms(section)
        matched_terms = sorted(set(incident_terms) & set(section_terms))
        score = _score(incident, section, incident_terms, section_terms, matched_terms)
        if score > 0:
            ranked.append(
                MatchedSection(
                    id=section.id,
                    title=section.title,
                    score=round(score, 3),
                    matched_terms=matched_terms[:12],
                )
            )

    return sorted(ranked, key=lambda item: item.score, reverse=True)[:limit]


def _incident_terms(incident: Incident) -> Counter[str]:
    text = " ".join(
        [
            incident.service,
            incident.title,
            incident.severity,
            *incident.alerts,
            *incident.logs,
            *incident.recent_changes,
            *incident.metrics.keys(),
        ]
    )
    return Counter(TOKEN_RE.findall(text.lower()))


def _section_terms(section: RunbookSection) -> Counter[str]:
    text = " ".join(
        [
            section.service,
            section.title,
            section.severity,
            *section.keywords,
            *section.symptoms,
            *section.checks,
            *section.actions,
        ]
    )
    return Counter(TOKEN_RE.findall(text.lower()))


def _score(
    incident: Incident,
    section: RunbookSection,
    incident_terms: Counter[str],
    section_terms: Counter[str],
    matched_terms: list[str],
) -> float:
    overlap = sum(min(incident_terms[term], section_terms[term]) for term in matched_terms)
    service_bonus = 4.0 if section.service.lower() == incident.service.lower() else 0.0
    severity_bonus = 2.0 if section.severity.lower() == incident.severity.lower() else 0.0
    keyword_bonus = sum(1.5 for keyword in section.keywords if keyword.lower() in incident_terms)
    return overlap + service_bonus + severity_bonus + keyword_bonus
