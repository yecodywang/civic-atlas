"""Find and load the catalog from YAML files on disk.

Folder layout (mirrors Open Civic Data division ids):

    jurisdictions/
      us/                         country        ocd-division/country:us
        nc/                       state          ocd-division/country:us/state:nc
          county/wake/            county         .../state:nc/county:wake
          place/raleigh/          city or town   .../state:nc/place:raleigh
          district/<name>/        special district (school system, transit, ...)

Inside each jurisdiction folder: ``jurisdiction.yaml``, an optional ``routing.yaml``, and
``services/*.yaml``. Folders whose names start with ``_`` (such as ``_template``) are ignored.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from civic_atlas.models import Jurisdiction, JurisdictionKind, Routing, Service

DATA_ENV_VAR = "CIVIC_ATLAS_DATA"

# Name of the first-level subdivision in OCD ids, per country. Add countries here as they join.
SUBDIVISION_TYPE: dict[str, str] = {"us": "state"}
PAIR_TYPES = frozenset({"county", "place", "district"})
_COUNTRY = re.compile(r"^[a-z]{2}$")
_SEGMENT = re.compile(r"^[a-z0-9]+(?:[-_~][a-z0-9]+)*$")


@dataclass(frozen=True)
class Issue:
    level: Literal["error", "warning"]
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper()}: {self.path}: {self.message}"


@dataclass(frozen=True)
class JurisdictionPath:
    id: str
    kind: JurisdictionKind
    ocd_id: str
    parent_id: str | None


@dataclass(frozen=True)
class JurisdictionRecord:
    id: str
    ocd_id: str
    parent_id: str | None
    path: Path
    data: Jurisdiction
    routing: Routing | None = None

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def country(self) -> str:
        return self.id.split("/", 1)[0]


@dataclass(frozen=True)
class ServiceRecord:
    jurisdiction_id: str
    path: Path
    data: Service

    @property
    def id(self) -> str:
        return self.data.id


@dataclass
class LoadResult:
    root: Path
    jurisdictions: dict[str, JurisdictionRecord] = field(default_factory=dict)
    services: dict[str, ServiceRecord] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]


def default_data_root() -> Path:
    """Locate ``jurisdictions/``: env var, then data bundled in the wheel, then the source tree."""
    env = os.environ.get(DATA_ENV_VAR)
    if env:
        return Path(env).expanduser().resolve()
    bundled = resources.files("civic_atlas").joinpath("_data", "jurisdictions")
    if bundled.is_dir():
        return Path(str(bundled))
    repo = Path(__file__).resolve().parents[2] / "jurisdictions"
    if repo.is_dir():
        return repo
    raise FileNotFoundError(
        f"Could not find the catalog data. Set {DATA_ENV_VAR} to the path of a 'jurisdictions' folder."
    )


def parse_jurisdiction_path(rel: str) -> JurisdictionPath:
    """Turn ``us/nc/place/raleigh`` into its kind, OCD id and parent. Raises ``ValueError``."""
    segments = rel.strip("/").split("/")
    country = segments[0]
    if not _COUNTRY.match(country):
        raise ValueError(f"first folder must be a 2-letter country code, got {country!r}")
    if len(segments) == 1:
        return JurisdictionPath(
            rel, JurisdictionKind.COUNTRY, f"ocd-division/country:{country}", None
        )

    subdivision = segments[1]
    if not _SEGMENT.match(subdivision):
        raise ValueError(f"bad subdivision folder name {subdivision!r}")
    subtype = SUBDIVISION_TYPE.get(country, "state")
    ocd = f"ocd-division/country:{country}/{subtype}:{subdivision}"
    if len(segments) == 2:
        return JurisdictionPath(rel, JurisdictionKind.STATE, ocd, country)

    rest = segments[2:]
    if len(rest) % 2:
        raise ValueError(
            "below the state, folders come in pairs of <type>/<name>, e.g. 'place/raleigh'"
        )
    kind = JurisdictionKind.STATE
    for type_, name in zip(rest[::2], rest[1::2], strict=True):
        if type_ not in PAIR_TYPES:
            raise ValueError(
                f"unknown jurisdiction type folder {type_!r}; use one of {sorted(PAIR_TYPES)}"
            )
        if not _SEGMENT.match(name):
            raise ValueError(f"bad folder name {name!r}; use lowercase letters, digits and hyphens")
        ocd += f"/{type_}:{name}"
        kind = JurisdictionKind(type_)
    parent = "/".join(segments[:-2])
    return JurisdictionPath(rel, kind, ocd, parent)


def _yaml() -> YAML:
    return YAML(typ="safe", pure=True)


def read_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return _yaml().load(fh)


def _format_validation_error(exc: ValidationError) -> str:
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"]) or "(top level)"
        parts.append(f"{loc}: {err['msg']}")
    return "; ".join(parts)


def _load_model(path: Path, model: type, rel: str, issues: list[Issue]) -> Any | None:
    try:
        raw = read_yaml(path)
    except YAMLError as exc:
        issues.append(Issue("error", rel, f"YAML syntax error: {exc}"))
        return None
    if not isinstance(raw, dict):
        issues.append(Issue("error", rel, "file must contain a YAML mapping (key: value pairs)"))
        return None
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        issues.append(Issue("error", rel, _format_validation_error(exc)))
        return None


def load(root: Path | None = None) -> LoadResult:
    """Load every jurisdiction, routing table and service under ``root``, collecting issues.

    Loading never stops at the first problem. Callers decide whether issues are fatal
    (see :func:`civic_atlas.catalog.Catalog.load`).
    """
    root = (root or default_data_root()).resolve()
    result = LoadResult(root=root)
    if not root.is_dir():
        result.issues.append(Issue("error", str(root), "data folder does not exist"))
        return result

    for jfile in sorted(root.rglob("jurisdiction.yaml")):
        jdir = jfile.parent
        rel_dir = jdir.relative_to(root).as_posix()
        if any(part.startswith("_") for part in jdir.relative_to(root).parts):
            continue
        rel_file = f"{rel_dir}/jurisdiction.yaml"
        try:
            jpath = parse_jurisdiction_path(rel_dir)
        except ValueError as exc:
            result.issues.append(Issue("error", rel_file, f"folder path: {exc}"))
            continue

        data = _load_model(jfile, Jurisdiction, rel_file, result.issues)
        if data is None:
            continue
        if data.kind is not jpath.kind:
            result.issues.append(
                Issue(
                    "error",
                    rel_file,
                    f"kind is {data.kind.value!r} but the folder path means {jpath.kind.value!r}",
                )
            )

        routing = None
        rfile = jdir / "routing.yaml"
        if rfile.exists():
            routing = _load_model(rfile, Routing, f"{rel_dir}/routing.yaml", result.issues)

        result.jurisdictions[jpath.id] = JurisdictionRecord(
            id=jpath.id,
            ocd_id=jpath.ocd_id,
            parent_id=jpath.parent_id,
            path=jdir,
            data=data,
            routing=routing,
        )

        services_dir = jdir / "services"
        if not services_dir.is_dir():
            continue
        for sfile in sorted(services_dir.glob("*.yaml")):
            if sfile.name.startswith("_"):
                continue
            rel_s = f"{rel_dir}/services/{sfile.name}"
            service = _load_model(sfile, Service, rel_s, result.issues)
            if service is None:
                continue
            if service.id != sfile.stem:
                result.issues.append(
                    Issue(
                        "error", rel_s, f"id {service.id!r} must match the file name {sfile.stem!r}"
                    )
                )
            if service.id in result.services:
                other = result.services[service.id]
                result.issues.append(
                    Issue(
                        "error",
                        rel_s,
                        f"duplicate service id {service.id!r} (also in {other.jurisdiction_id})",
                    )
                )
                continue
            result.services[service.id] = ServiceRecord(jpath.id, sfile, service)

    for stray in sorted(root.rglob("*.yml")):
        result.issues.append(
            Issue(
                "warning",
                stray.relative_to(root).as_posix(),
                "use the .yaml extension; .yml files are ignored",
            )
        )
    return result
