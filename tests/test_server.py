import json

import pytest
from mcp import Client

from civic_atlas.server import build_server

pytestmark = pytest.mark.anyio

EXPECTED_TOOLS = {
    "list_jurisdictions",
    "search_services",
    "get_service",
    "who_to_contact",
    "get_key_contacts",
}


@pytest.fixture
def server(fixture_catalog):
    return build_server(fixture_catalog, default_jurisdiction="springfield")


async def test_tools_are_listed_and_read_only(server):
    async with Client(server) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == EXPECTED_TOOLS
    for tool in tools.values():
        assert tool.annotations.read_only_hint is True
        assert tool.annotations.destructive_hint is False
        assert tool.annotations.open_world_hint is False
        assert tool.description


def test_instructions_state_the_non_emergency_scope(server):
    from civic_atlas.catalog import SCOPE_NOTE

    text = server.instructions
    assert text.startswith(SCOPE_NOTE)
    assert "non-emergency" in text
    assert "not an official" in text
    assert "Never offer" in text


async def call(server, name, args=None):
    async with Client(server) as client:
        result = await client.call_tool(name, args or {})
    assert not result.is_error, result.content
    # Structured content and the text fallback must agree.
    assert json.loads(result.content[0].text) == result.structured_content
    return result.structured_content


async def test_list_jurisdictions(server):
    out = await call(server, "list_jurisdictions")
    assert out["default_jurisdiction"] == "us/zz/place/springfield"
    ids = {j["id"] for j in out["jurisdictions"]}
    assert {"us", "us/zz", "us/zz/county/east", "us/zz/place/springfield"} <= ids


async def test_search_services_labels_the_provider(server):
    out = await call(server, "search_services", {"query": "property tax bill"})
    top = out["results"][0]
    assert top["id"] == "property-tax-bill"
    assert top["provided_by"] == "East County"
    assert top["status"] == "draft"
    assert out["disclaimer"]


async def test_search_with_no_results_gives_a_tip(server):
    out = await call(server, "search_services", {"query": "llama grooming"})
    assert out["results"] == []
    assert "who_to_contact" in out["tip"]


async def test_get_service_includes_steps_sources_and_reminder(server):
    out = await call(server, "get_service", {"service_id": "report-missed-collection"})
    assert out["steps"]["online"]
    assert out["provenance"]["source_urls"]
    assert out["provided_by"]["id"] == "us/zz/place/springfield"
    assert "Do not submit" in out["reminder"]


async def test_get_service_unknown_id_is_a_tool_error(server):
    async with Client(server) as client:
        result = await client.call_tool("get_service", {"service_id": "nope"})
    assert result.is_error
    assert "search_services" in result.content[0].text


async def test_who_to_contact_routes(server):
    out = await call(server, "who_to_contact", {"situation": "nobody picked up my garbage"})
    assert out["matches"][0]["service_id"] == "report-missed-collection"


async def test_unknown_jurisdiction_is_a_tool_error(server):
    async with Client(server) as client:
        result = await client.call_tool(
            "who_to_contact", {"situation": "x", "jurisdiction": "gotham"}
        )
    assert result.is_error


async def test_get_key_contacts_skips_partial_overlaps(server):
    out = await call(server, "get_key_contacts")
    names = [g["name"] for g in out["groups"]]
    assert names[0] == "City of Springfield"
    assert "West County" not in names


async def test_search_results_carry_sources(server):
    out = await call(server, "search_services", {"query": "pothole"})
    hit = out["results"][0]
    assert hit["source_urls"] and hit["last_checked"]


async def test_no_tool_returns_emergency_fields(server):
    """Emergencies are out of scope (ADR 0003)."""
    calls = [
        ("list_jurisdictions", {}),
        ("search_services", {"query": "my house is on fire"}),
        ("get_service", {"service_id": "report-pothole"}),
        ("who_to_contact", {"situation": "my house is on fire"}),
        ("get_key_contacts", {}),
    ]
    for name, args in calls:
        out = await call(server, name, args)
        assert not {"emergency", "safety", "emergency_number"} & set(out), name
