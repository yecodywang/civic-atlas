"""'Who do I contact?' routing.

Safety rules (see docs/legal-and-safety.md). These are deliberately hard-coded, not data-driven,
so no edit to the catalog can weaken them:

1. Every answer carries a line telling the person to call the emergency number if anyone is in
   danger, because keyword matching will always miss some emergencies.
2. If the situation looks like an emergency, the answer leads with the emergency number, before
   any catalog routing.
3. Crisis language (suicide, self-harm) also adds the national crisis line where one is known.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from civic_atlas.catalog import DISCLAIMER, Catalog
from civic_atlas.loader import JurisdictionRecord
from civic_atlas.models import RoutingRule
from civic_atlas.text import contains_phrase, remove_phrase, tokens

# Emergency number by country code (first folder of the jurisdiction id).
EMERGENCY_NUMBERS: dict[str, str] = {"us": "911"}

# National crisis lines by country code.
CRISIS_LINES: dict[str, str] = {
    "us": "Call or text 988 (988 Suicide & Crisis Lifeline), available 24/7.",
}

# Phrases that contain an emergency word but are routine requests. These are removed before
# checking for emergencies.
NOT_EMERGENCIES = [
    "smoke alarm",
    "smoke detector",
    "fire alarm installation",
    "fire hydrant",
    "fire department",
    "fire station",
    "fire pit",
    "fire inspection",
    "burn permit",
    "open burning",
    "flu shot",
    "fire marshal",
    "emergency alert",
    "emergency notification",
    "emergency management",
    "emergency preparedness",
    "non emergency",
    "nonemergency",
    "not an emergency",
    "not emergency",
]

EMERGENCY_PHRASES = [
    "emergency",
    "fire",
    "flame",
    "smoke",
    "burning",
    "gas leak",
    "smell gas",
    "smell of gas",
    "carbon monoxide",
    "explosion",
    "not breathing",
    "can t breathe",
    "cant breathe",
    "cannot breathe",
    "trouble breathing",
    "unconscious",
    "unresponsive",
    "passed out",
    "heart attack",
    "chest pain",
    "stroke",
    "seizure",
    "overdose",
    "bleeding",
    "badly hurt",
    "injured",
    "injury",
    "someone is hurt",
    "car crash",
    "car accident",
    "crash",
    "hit by a car",
    "break in",
    "breaking in",
    "intruder",
    "robbery",
    "being robbed",
    "assault",
    "attacked",
    "shot",
    "shooting",
    "gun",
    "weapon",
    "knife",
    "stabbing",
    "kidnap",
    "missing child",
    "drowning",
    "trapped",
    "power line down",
    "downed power line",
    "live wire",
    "danger",
    "dangerous",
    "threatening",
]

CRISIS_PHRASES = [
    "suicide",
    "suicidal",
    "kill myself",
    "end my life",
    "hurt myself",
    "self harm",
    "want to die",
]

_NOT_EMERGENCY_TOKENS = [tokens(p) for p in NOT_EMERGENCIES]
_EMERGENCY_TOKENS = [(p, tokens(p)) for p in EMERGENCY_PHRASES]
_CRISIS_TOKENS = [(p, tokens(p)) for p in CRISIS_PHRASES]


def emergency_number(country: str) -> str | None:
    return EMERGENCY_NUMBERS.get(country)


def danger_line(country: str) -> str:
    number = emergency_number(country)
    if number:
        return f"If anyone is in danger or this is an emergency, call {number} now."
    return "If anyone is in danger or this is an emergency, call your local emergency number now."


@dataclass(frozen=True)
class EmergencyCheck:
    detected: bool
    matched: list[str]
    crisis: bool


def check_emergency(situation: str) -> EmergencyCheck:
    toks = tokens(situation)
    for phrase in _NOT_EMERGENCY_TOKENS:
        toks = remove_phrase(toks, phrase)
    matched = [p for p, pt in _EMERGENCY_TOKENS if contains_phrase(toks, pt)]
    crisis = [p for p, pt in _CRISIS_TOKENS if contains_phrase(toks, pt)]
    return EmergencyCheck(
        detected=bool(matched or crisis), matched=matched + crisis, crisis=bool(crisis)
    )


def _text_to_911(catalog: Catalog, ref: str) -> bool | None:
    for rec, _ in catalog.scope(ref):
        if rec.data.emergency and rec.data.emergency.text_to_911 is not None:
            return rec.data.emergency.text_to_911
    return None


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
    """Route a plain-language situation to the right place. Emergencies always come first."""
    home = catalog.resolve(jurisdiction)
    country = home.country
    check = check_emergency(situation)
    answer: dict[str, Any] = {
        "situation": situation,
        "jurisdiction": home.name,
        "jurisdiction_id": home.id,
        "safety": danger_line(country),
    }

    if check.detected:
        number = emergency_number(country) or "your local emergency number"
        emergency: dict[str, Any] = {
            "detected": True,
            "matched_words": check.matched,
            "action": f"This may be an emergency. Call {number} now. Do not wait for a website or form.",
        }
        texting = _text_to_911(catalog, home.id)
        if number == "911" and texting is True:
            emergency["text"] = (
                "If you cannot safely speak, you can text 911 here. Calling is best when you can."
            )
        if check.crisis and country in CRISIS_LINES:
            emergency["crisis_line"] = CRISIS_LINES[country]
        answer["emergency"] = emergency

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
