from pathlib import Path

import pytest

from civic_atlas.catalog import Catalog

FIXTURES = Path(__file__).parent / "fixtures" / "jurisdictions"
REPO_DATA = Path(__file__).resolve().parents[1] / "jurisdictions"


@pytest.fixture(scope="session")
def fixture_catalog() -> Catalog:
    return Catalog.load(FIXTURES)


@pytest.fixture(scope="session")
def real_catalog() -> Catalog:
    return Catalog.load(REPO_DATA)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
