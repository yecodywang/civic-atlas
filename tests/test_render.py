from civic_atlas.render import render_all, render_card


def test_card_has_steps_safety_status_and_sources(fixture_catalog):
    card = render_card(fixture_catalog, fixture_catalog.services["report-missed-collection"])
    assert card.startswith("# Report a missed trash")
    assert "1. Open the request portal." in card
    assert "call 911" in card
    assert "Draft:" in card
    assert "https://example.org/springfield/trash" in card
    assert "[Report a pothole](report-pothole.md)" in card


def test_render_all_writes_menu_contacts_routing_and_cards(fixture_catalog, tmp_path):
    written = render_all(fixture_catalog, "springfield", tmp_path)
    names = {p.name for p in written}
    assert {"README.md", "key-contacts.md", "who-to-contact.md"} <= names
    assert "report-pothole.md" in names
    assert "property-tax-bill.md" in names  # county service, in scope for the city
    menu = (tmp_path / "us-zz-place-springfield" / "README.md").read_text()
    assert "## Fix & report" in menu
    assert "- [ ] [Report a pothole](report-pothole.md)" in menu
    routing = (tmp_path / "us-zz-place-springfield" / "who-to-contact.md").read_text()
    assert "| Question about a property tax bill | East County Tax Office |" in routing
