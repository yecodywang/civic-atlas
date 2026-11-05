import pytest

from civic_atlas.routing import check_emergency, who_to_contact

EMERGENCIES = [
    "my neighbor's house is on fire",
    "I smell gas in my kitchen",
    "someone was hit by a car",
    "there was a car crash and people are hurt",
    "a man is breaking in next door",
    "my dad is not breathing",
    "I hear shots fired",
    "there's a power line down across the road",
    "I want to kill myself",
]

NOT_EMERGENCIES = [
    "how do I get a free smoke alarm installed",
    "a fire hydrant is leaking",
    "sign up for emergency alerts",
    "what's the non-emergency number",
    "my trash wasn't picked up",
    "question about my tax bill",
]


@pytest.mark.parametrize("situation", EMERGENCIES)
def test_emergencies_are_detected(situation):
    assert check_emergency(situation).detected


@pytest.mark.parametrize("situation", NOT_EMERGENCIES)
def test_routine_requests_are_not_flagged(situation):
    assert not check_emergency(situation).detected


@pytest.mark.parametrize("situation", EMERGENCIES)
def test_emergency_answers_lead_with_911(fixture_catalog, situation):
    answer = who_to_contact(fixture_catalog, situation, "springfield")
    assert "911" in answer["emergency"]["action"]
    assert "911" in answer["safety"]


def test_crisis_language_adds_988(fixture_catalog):
    answer = who_to_contact(fixture_catalog, "I want to end my life", "springfield")
    assert "988" in answer["emergency"]["crisis_line"]


def test_text_to_911_comes_from_the_county(fixture_catalog):
    answer = who_to_contact(fixture_catalog, "there is a fire", "springfield")
    assert "text 911" in answer["emergency"]["text"]


@pytest.mark.parametrize("situation", EMERGENCIES + NOT_EMERGENCIES + ["blah blah"])
def test_every_answer_carries_the_danger_line(fixture_catalog, situation):
    answer = who_to_contact(fixture_catalog, situation, "springfield")
    assert answer["safety"].startswith("If anyone is in danger")
    assert answer["disclaimer"]


def test_routes_tax_questions_to_the_county(fixture_catalog):
    answer = who_to_contact(
        fixture_catalog, "I have a question about my property tax bill", "springfield"
    )
    assert "emergency" not in answer
    top = answer["matches"][0]
    assert top["handled_by"] == "East County"
    assert top["service_id"] == "property-tax-bill"


def test_unmatched_situations_get_the_fallback(fixture_catalog):
    answer = who_to_contact(fixture_catalog, "something unusual about llamas", "springfield")
    assert answer["matches"] == []
    assert answer["fallback"]["channel"]["phone"] == "555-0100"
