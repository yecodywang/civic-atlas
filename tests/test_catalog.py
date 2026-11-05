import pytest

from civic_atlas.catalog import Relation


def test_resolve_by_id_alias_and_ocd(fixture_catalog):
    assert fixture_catalog.resolve("us/zz/place/springfield").name == "City of Springfield"
    assert fixture_catalog.resolve("Springfield").id == "us/zz/place/springfield"
    assert fixture_catalog.resolve("ocd-division/country:us/state:zz/place:springfield").id == (
        "us/zz/place/springfield"
    )
    with pytest.raises(LookupError):
        fixture_catalog.resolve("gotham")


def test_scope_orders_self_overlaps_then_ancestors(fixture_catalog):
    scope = [(r.id, rel) for r, rel in fixture_catalog.scope("springfield")]
    assert scope == [
        ("us/zz/place/springfield", Relation.SELF),
        ("us/zz/county/east", Relation.PRIMARY_OVERLAP),
        ("us/zz/county/west", Relation.OVERLAP),
        ("us/zz", Relation.ANCESTOR),
        ("us", Relation.ANCESTOR),
    ]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("my trash wasn't picked up", "report-missed-collection"),
        ("garbage bins", "report-missed-collection"),
        ("there are potholes on my street", "report-pothole"),
        ("question about my tax bill", "property-tax-bill"),
        ("I need rent help", "state-helpline"),
    ],
)
def test_search_ranks_the_right_service_first(fixture_catalog, query, expected):
    hits = fixture_catalog.search(query, "springfield")
    assert hits, query
    assert hits[0].service.id == expected


def test_search_spans_county_and_state(fixture_catalog):
    hits = {h.service.id: h for h in fixture_catalog.search("tax bill", "springfield")}
    assert hits["property-tax-bill"].relation is Relation.PRIMARY_OVERLAP


def test_search_filters_by_category(fixture_catalog):
    hits = fixture_catalog.search("", "springfield", category="fix-report")
    assert {h.service.id for h in hits} == {"report-missed-collection", "report-pothole"}


def test_search_from_county_does_not_include_city_services(fixture_catalog):
    hits = fixture_catalog.search("trash", "us/zz/county/east")
    assert all(h.service.id != "report-missed-collection" for h in hits)
