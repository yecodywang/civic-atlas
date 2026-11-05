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
        # Health: the City has no health department; the County provides public health.
        ("does Raleigh have a health department", "Wake County Public Health", "Wake County"),
        ("I need a flu shot", "Wake County Public Health", "Wake County"),
        ("I don't have insurance and need a doctor", "community clinics", "Wake County"),
        ("I'm pregnant and need help buying baby formula", "WIC", "Wake County"),
        ("how do I apply for medicaid", "Medicaid", "Wake County"),
    ],
)
def test_routing_examples(real_catalog, situation, go_to_contains, handled_by):
    answer = who_to_contact(real_catalog, situation, "raleigh")
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
        ("where can I get an STD test", "hiv-sti-testing"),
        ("my kid needs shots for 7th grade", "get-vaccinations"),
        ("I need a dentist", "public-health-clinics"),
        ("low cost doctor", "low-cost-primary-care"),
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


def test_catalog_contains_no_emergency_numbers():
    """Emergency numbers are out of scope (ADR 0003); the validator enforces it."""
    from civic_atlas.loader import load
    from civic_atlas.validate import scope_issues

    assert scope_issues(load(REPO_DATA)) == []
