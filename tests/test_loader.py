import textwrap
from pathlib import Path

import pytest

from civic_atlas.loader import load, parse_jurisdiction_path
from civic_atlas.models import JurisdictionKind


@pytest.mark.parametrize(
    ("path", "kind", "ocd", "parent"),
    [
        ("us", JurisdictionKind.COUNTRY, "ocd-division/country:us", None),
        ("us/nc", JurisdictionKind.STATE, "ocd-division/country:us/state:nc", "us"),
        (
            "us/nc/county/wake",
            JurisdictionKind.COUNTY,
            "ocd-division/country:us/state:nc/county:wake",
            "us/nc",
        ),
        (
            "us/nc/place/raleigh",
            JurisdictionKind.PLACE,
            "ocd-division/country:us/state:nc/place:raleigh",
            "us/nc",
        ),
        (
            "us/pa/county/adams/place/franklin",
            JurisdictionKind.PLACE,
            "ocd-division/country:us/state:pa/county:adams/place:franklin",
            "us/pa/county/adams",
        ),
    ],
)
def test_parse_jurisdiction_path(path, kind, ocd, parent):
    parsed = parse_jurisdiction_path(path)
    assert parsed.kind is kind
    assert parsed.ocd_id == ocd
    assert parsed.parent_id == parent


@pytest.mark.parametrize(
    "path", ["usa", "us/nc/raleigh", "us/nc/city/raleigh", "us/nc/place/Raleigh"]
)
def test_parse_jurisdiction_path_rejects_bad_layouts(path):
    with pytest.raises(ValueError):
        parse_jurisdiction_path(path)


def test_fixture_catalog_loads_cleanly(fixture_catalog):
    assert not fixture_catalog.issues
    assert "us/zz/place/springfield" in fixture_catalog.jurisdictions
    assert fixture_catalog.services["property-tax-bill"].jurisdiction_id == "us/zz/county/east"


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")


PROV = """
provenance:
  source_urls: ["https://example.org"]
  last_checked: 2026-11-01
"""


def test_load_reports_problems_without_stopping(tmp_path):
    _write(tmp_path / "us/jurisdiction.yaml", "name: US\nkind: country\n" + PROV)
    # kind does not match the folder
    _write(tmp_path / "us/nc/jurisdiction.yaml", "name: NC\nkind: county\n" + PROV)
    # unknown key (typo) is an error
    _write(
        tmp_path / "us/nc/county/wake/jurisdiction.yaml",
        "name: Wake\nkind: county\nwebsite: x\n" + PROV,
    )
    # bad YAML
    _write(tmp_path / "us/nc/place/raleigh/jurisdiction.yaml", "name: [unclosed\n")
    # service id must match file name
    _write(
        tmp_path / "us/services/wrong-name.yaml",
        textwrap.dedent("""
        id: right-name
        title: T
        summary: S
        provider: P
        category: contact
        channels:
          - type: web
            label: L
            url: https://example.org
        """)
        + PROV,
    )
    # ignored template folder
    _write(tmp_path / "_template/jurisdiction.yaml", "nonsense: true\n")

    result = load(tmp_path)
    messages = "\n".join(str(i) for i in result.issues)
    assert "kind is 'county' but the folder path means 'state'" in messages
    assert "website" in messages
    assert "YAML syntax error" in messages
    assert "must match the file name" in messages
    assert "_template" not in messages
    assert "us" in result.jurisdictions


def test_channel_requires_an_address():
    from pydantic import ValidationError

    from civic_atlas.models import Channel

    with pytest.raises(ValidationError):
        Channel(type="web", label="no url")
    with pytest.raises(ValidationError):
        Channel(type="phone", label="no number")


def test_verified_status_requires_a_person():
    from pydantic import ValidationError

    from civic_atlas.models import Provenance

    with pytest.raises(ValidationError):
        Provenance(
            source_urls=["https://example.org"], last_checked="2026-11-01", status="verified"
        )
    ok = Provenance(
        source_urls=["https://example.org"],
        last_checked="2026-11-01",
        status="verified",
        verified_by="someone",
        verified_on="2026-11-01",
    )
    assert ok.verified_by == "someone"
