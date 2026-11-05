from datetime import date

from civic_atlas.loader import load
from civic_atlas.validate import check_schemas, cross_reference_issues, freshness_issues
from tests.conftest import FIXTURES


def test_fixture_cross_references_are_clean():
    assert cross_reference_issues(load(FIXTURES)) == []


def test_stale_entries_are_warned():
    issues = freshness_issues(load(FIXTURES), today=date(2027, 12, 1))
    assert issues
    assert all(i.level == "warning" for i in issues)


def test_future_dates_are_errors():
    issues = freshness_issues(load(FIXTURES), today=date(2026, 1, 1))
    assert any(i.level == "error" and "future" in i.message for i in issues)


def test_generated_schema_files_are_in_sync():
    assert check_schemas() == []


def test_templates_are_valid_examples():
    from civic_atlas.loader import read_yaml
    from civic_atlas.models import Jurisdiction, Routing, Service
    from tests.conftest import REPO_DATA

    template = REPO_DATA / "_template"
    Jurisdiction.model_validate(read_yaml(template / "jurisdiction.yaml"))
    Routing.model_validate(read_yaml(template / "routing.yaml"))
    Service.model_validate(read_yaml(template / "services" / "_example-service.yaml"))
