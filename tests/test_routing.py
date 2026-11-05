from civic_atlas.routing import who_to_contact


def test_routes_tax_questions_to_the_county(fixture_catalog):
    answer = who_to_contact(
        fixture_catalog, "I have a question about my property tax bill", "springfield"
    )
    top = answer["matches"][0]
    assert top["handled_by"] == "East County"
    assert top["service_id"] == "property-tax-bill"


def test_unmatched_situations_get_the_fallback(fixture_catalog):
    answer = who_to_contact(fixture_catalog, "something unusual about llamas", "springfield")
    assert answer["matches"] == []
    assert answer["fallback"]["channel"]["phone"] == "555-0100"
    assert answer["disclaimer"]


def test_routing_does_not_try_to_handle_emergencies(fixture_catalog):
    """Emergencies are out of scope (ADR 0003): no detection, no emergency fields."""
    answer = who_to_contact(fixture_catalog, "my house is on fire", "springfield")
    assert "emergency" not in answer
    assert "safety" not in answer
