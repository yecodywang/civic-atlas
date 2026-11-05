"""Checks against the real catalog in jurisdictions/.

These protect the answers people rely on most. If a data change breaks one, fix the data or update
the expectation in the same pull request, with a reason.
"""

from datetime import date

import pytest

from civic_atlas.routing import who_to_contact
from civic_atlas.validate import validate
from tests.conftest import REPO_DATA


def test_real_catalog_has_no_errors():
    _, issues = validate(REPO_DATA, today=date.today())
    errors = [str(i) for i in issues if i.level == "error"]
    assert errors == []


def test_raleigh_lies_mostly_in_wake_county(real_catalog):
    raleigh = real_catalog.resolve("raleigh")
    assert raleigh.ocd_id == "ocd-division/country:us/state:nc/place:raleigh"
    overlaps = {o.id: o.primary for o in raleigh.data.overlaps}
    assert overlaps == {"us/nc/county/wake": True, "us/nc/county/durham": False}


def test_text_to_911_is_known_for_raleigh(real_catalog):
    answer = who_to_contact(real_catalog, "there is a fire in my kitchen", "raleigh")
    assert "text 911" in answer["emergency"]["text"]


@pytest.mark.parametrize(
    ("situation", "go_to_contains", "handled_by"),
    [
        # The "who do I contact?" examples from the course proposal.
        ("a fire hydrant is leaking", "Raleigh Water", "City of Raleigh"),
        ("my trash wasn't picked up", "Solid Waste", "City of Raleigh"),
        ("I have a question about my tax bill", "Wake County Tax", "Wake County"),
        # Other common questions.
        ("there is a pothole on my street", "street maintenance", "City of Raleigh"),
        ("the streetlight is out", "Duke Energy", None),
        ("I need help paying rent", "NC 211", "State of North Carolina"),
        ("loud party next door", "Police non-emergency", "City of Raleigh"),
        ("reserve a picnic shelter", "Parks", "City of Raleigh"),
    ],
)
def test_routing_examples(real_catalog, situation, go_to_contains, handled_by):
    answer = who_to_contact(real_catalog, situation, "raleigh")
    assert "emergency" not in answer, situation
    top = answer["matches"][0]
    assert go_to_contains in top["go_to"]
    assert top["handled_by"] == handled_by


@pytest.mark.parametrize(
    ("query", "service_id"),
    [
        ("how do I report a pothole", "report-pothole"),
        ("my trash wasn't picked up", "report-missed-collection"),
        ("pay my water bill", "pay-utility-bill"),
        ("set up autopay", "set-up-utility-autopay"),
        ("get rid of an old couch", "schedule-bulky-item-pickup"),
        ("sign up for emergency alerts", "readywake-alerts"),
        ("city email newsletter", "myraleigh-subscriptions"),
        ("find my property tax bill", "property-tax-bill"),
        ("property tax relief for seniors", "property-tax-relief"),
        ("free smoke alarm", "request-smoke-alarm"),
        ("sign up for a class", "reclink-register-program"),
        ("a fire hydrant is leaking", "report-water-sewer-problem"),
        ("text 911", "text-911"),
    ],
)
def test_search_examples(real_catalog, query, service_id):
    hits = real_catalog.search(query, "raleigh", limit=3)
    assert hits, query
    assert hits[0].service.id == service_id


def test_ambiguous_queries_surface_both_answers(real_catalog):
    hits = real_catalog.search("sign up for a class at the community center", "raleigh", limit=2)
    assert {h.service.id for h in hits} == {"reclink-register-program", "find-park-greenway-center"}


def test_every_service_cites_a_source_and_is_honest_about_status(real_catalog):
    for svc in real_catalog.services.values():
        prov = svc.data.provenance
        assert prov.source_urls, svc.id
        if prov.status.value == "verified":
            assert prov.verified_by, svc.id


# Aliases that describe an emergency on purpose (text-911 is for when you can't safely talk).
EMERGENCY_ALIAS_ALLOWLIST = {"text-911"}


def test_catalog_wording_does_not_trip_the_emergency_matcher(real_catalog):
    """Our own routing keywords, titles and aliases must agree with the emergency matcher.

    If a routing rule's keyword or a service alias looks like an emergency, people using those
    words get a 911-first answer that contradicts the routed answer. Fix the wording or the matcher.
    """
    from civic_atlas.routing import check_emergency

    problems = []
    for rec in real_catalog.jurisdictions.values():
        if rec.routing:
            for rule in rec.routing.rules:
                for kw in rule.keywords:
                    if check_emergency(kw).detected:
                        problems.append(f"routing {rec.id}:{rule.id} keyword {kw!r}")
    for svc in real_catalog.services.values():
        if svc.id in EMERGENCY_ALIAS_ALLOWLIST:
            continue
        for text in [svc.data.title, *svc.data.aliases]:
            if check_emergency(text).detected:
                problems.append(f"service {svc.id}: {text!r}")
    assert problems == []


@pytest.mark.parametrize(
    "situation",
    [
        "this isn't an emergency but my car was broken into",
        "it's not an emergency, just a question about my water bill",
        "not urgent: a streetlight is out",
    ],
)
def test_common_non_emergency_phrasings(real_catalog, situation):
    answer = who_to_contact(real_catalog, situation, "raleigh")
    assert "emergency" not in answer, situation
    assert answer["matches"]
