"""Whole-catalog checks beyond what a single file's schema can express."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from civic_atlas.loader import Issue, LoadResult, load
from civic_atlas.models import SCHEMA_MODELS, Status

STALE_AFTER_DAYS = 180


def schema_text(kind: str) -> str:
    schema = SCHEMA_MODELS[kind].model_json_schema()
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://github.com/yecodywang/civic-atlas/schema/{kind}.schema.json",
        **schema,
    }
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def schema_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "schema"


def write_schemas(out_dir: Path | None = None) -> list[Path]:
    out_dir = out_dir or schema_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for kind in SCHEMA_MODELS:
        path = out_dir / f"{kind}.schema.json"
        path.write_text(schema_text(kind), encoding="utf-8")
        written.append(path)
    return written


def check_schemas(out_dir: Path | None = None) -> list[Issue]:
    out_dir = out_dir or schema_dir()
    issues = []
    for kind in SCHEMA_MODELS:
        path = out_dir / f"{kind}.schema.json"
        if not path.exists() or path.read_text(encoding="utf-8") != schema_text(kind):
            issues.append(
                Issue(
                    "error", f"schema/{kind}.schema.json", "out of date; run `civic-atlas schema`"
                )
            )
    return issues


def cross_reference_issues(result: LoadResult) -> list[Issue]:
    issues: list[Issue] = []
    jids = result.jurisdictions
    root = result.root

    def rel(path: Path) -> str:
        return path.relative_to(root).as_posix()

    for rec in jids.values():
        jfile = f"{rec.id}/jurisdiction.yaml"
        if rec.parent_id and rec.parent_id not in jids:
            issues.append(
                Issue(
                    "error",
                    jfile,
                    f"parent jurisdiction {rec.parent_id!r} has no jurisdiction.yaml",
                )
            )
        primaries = 0
        for ov in rec.data.overlaps:
            if ov.id not in jids:
                issues.append(Issue("error", jfile, f"overlaps unknown jurisdiction {ov.id!r}"))
            if ov.id == rec.id:
                issues.append(Issue("error", jfile, "a jurisdiction cannot overlap itself"))
            primaries += ov.primary
        if primaries > 1:
            issues.append(Issue("error", jfile, "at most one overlap may be primary"))
        if rec.routing:
            rfile = f"{rec.id}/routing.yaml"
            seen: set[str] = set()
            for rule in rec.routing.rules:
                if rule.id in seen:
                    issues.append(Issue("error", rfile, f"duplicate rule id {rule.id!r}"))
                seen.add(rule.id)
                if rule.jurisdiction and rule.jurisdiction not in jids:
                    issues.append(
                        Issue(
                            "error",
                            rfile,
                            f"rule {rule.id!r}: unknown jurisdiction {rule.jurisdiction!r}",
                        )
                    )
                if rule.service and rule.service not in result.services:
                    issues.append(
                        Issue("error", rfile, f"rule {rule.id!r}: unknown service {rule.service!r}")
                    )
                if not (rule.service or rule.channel):
                    issues.append(
                        Issue("error", rfile, f"rule {rule.id!r}: needs a service or a channel")
                    )

    for svc in result.services.values():
        for ref in svc.data.related:
            if ref not in result.services:
                issues.append(
                    Issue("error", rel(svc.path), f"related service {ref!r} does not exist")
                )
            if ref == svc.id:
                issues.append(
                    Issue("error", rel(svc.path), "a service cannot be related to itself")
                )
    return issues


def freshness_issues(
    result: LoadResult, today: date, max_age_days: int = STALE_AFTER_DAYS
) -> list[Issue]:
    issues: list[Issue] = []
    entries = [
        (f"{r.id}/jurisdiction.yaml", r.data.provenance) for r in result.jurisdictions.values()
    ]
    entries += [
        (s.path.relative_to(result.root).as_posix(), s.data.provenance)
        for s in result.services.values()
    ]
    entries += [
        (f"{r.id}/routing.yaml", r.routing.provenance)
        for r in result.jurisdictions.values()
        if r.routing
    ]
    for where, prov in entries:
        age = (today - prov.last_checked).days
        if age < 0:
            issues.append(
                Issue("error", where, f"last_checked {prov.last_checked} is in the future")
            )
        elif age > max_age_days:
            issues.append(
                Issue(
                    "warning",
                    where,
                    f"last checked {age} days ago (over {max_age_days}); please re-verify",
                )
            )
        if prov.status is Status.NEEDS_REVIEW:
            issues.append(Issue("warning", where, "marked needs-review"))
    return issues


def validate(
    root: Path | None = None, *, today: date | None = None, check_schema_files: bool = True
):
    """Run every check. Returns ``(LoadResult, issues)``."""
    result = load(root)
    issues = list(result.issues)
    issues += cross_reference_issues(result)
    issues += freshness_issues(result, today or date.today())
    if check_schema_files:
        issues += check_schemas()
    return result, issues
