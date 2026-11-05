"""'Who do I contact?' routing for non-emergency situations.

Scope: civic-atlas covers **non-emergency** services only. It does not try to detect or route
emergencies (see docs/adr/0003-non-emergency-scope.md). Routing matches a person's words against
the routing tables of the jurisdictions in scope and falls back to a general help line.
"""

from __future__ import annotations

from typing import Any

from civic_atlas.catalog import DISCLAIMER, Catalog
from civic_atlas.loader import JurisdictionRecord
from civic_atlas.models import RoutingRule
from civic_atlas.text import contains_phrase, tokens


def _rule_score(rule: RoutingRule, situation_tokens: list[str]) -> int:
    return sum(1 for kw in rule.keywords if contains_phrase(situation_tokens, tokens(kw)))


def _rule_dict(catalog: Catalog, rule: RoutingRule, source: JurisdictionRecord) -> dict[str, Any]:
    handled_by = catalog.jurisdictions.get(rule.jurisdiction) if rule.jurisdiction else None
    out: dict[str, Any] = {
        "situation": rule.situation,
        "go_to": rule.go_to,
        "explanation": rule.explanation,
        "handled_by": handled_by.name if handled_by else None,
        "handled_by_id": rule.jurisdiction,
        "routing_table": source.id,
    }
    if rule.channel:
        out["channel"] = rule.channel.model_dump(mode="json", exclude_none=True)
    if rule.service:
        out["service_id"] = rule.service
        out["next_step"] = f"Call get_service('{rule.service}') for step-by-step instructions."
    return out


def who_to_contact(catalog: Catalog, situation: str, jurisdiction: str) -> dict[str, Any]:
    """Route a plain-language, non-emergency situation to the right office."""
    home = catalog.resolve(jurisdiction)
    answer: dict[str, Any] = {
        "situation": situation,
        "jurisdiction": home.name,
        "jurisdiction_id": home.id,
    }

    situation_tokens = tokens(situation)
    scored: list[tuple[int, int, RoutingRule, JurisdictionRecord]] = []
    order = 0
    for rec, _relation in catalog.scope(home.id):
        if rec.routing is None:
            continue
        for rule in rec.routing.rules:
            score = _rule_score(rule, situation_tokens)
            if score:
                scored.append((score, order, rule, rec))
            order += 1
    scored.sort(key=lambda t: (-t[0], t[1]))
    answer["matches"] = [_rule_dict(catalog, rule, rec) for _, _, rule, rec in scored[:3]]

    if not answer["matches"]:
        for rec, _relation in catalog.scope(home.id):
            if rec.routing is not None:
                fb = rec.routing.fallback
                answer["fallback"] = {
                    "go_to": fb.go_to,
                    "channel": fb.channel.model_dump(mode="json", exclude_none=True),
                    "explanation": fb.explanation,
                }
                break

    answer["disclaimer"] = DISCLAIMER
    return answer
