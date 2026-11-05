"""Command-line interface: ``civic-atlas <command>``."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from civic_atlas import __version__


def _cmd_validate(args: argparse.Namespace) -> int:
    from civic_atlas.validate import validate

    result, issues = validate(args.data, check_schema_files=not args.skip_schema)
    for issue in issues:
        if issue.level == "error" or not args.quiet:
            print(issue)
    errors = sum(1 for i in issues if i.level == "error")
    warnings = len(issues) - errors
    statuses = Counter(s.data.provenance.status.value for s in result.services.values())
    status_text = ", ".join(f"{n} {k}" for k, n in sorted(statuses.items())) or "none"
    print(
        f"\n{len(result.jurisdictions)} jurisdictions, {len(result.services)} services "
        f"({status_text}); {errors} error(s), {warnings} warning(s)."
    )
    if errors or (args.strict and warnings):
        return 1
    return 0


def _cmd_schema(args: argparse.Namespace) -> int:
    from civic_atlas.validate import check_schemas, write_schemas

    if args.check:
        issues = check_schemas()
        for issue in issues:
            print(issue)
        if not issues:
            print("schema files are up to date.")
        return 1 if issues else 0
    for path in write_schemas():
        print(f"wrote {path}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    from civic_atlas.catalog import Catalog

    catalog = Catalog.load(args.data)
    for rec in sorted(catalog.jurisdictions.values(), key=lambda r: r.id):
        count = sum(1 for s in catalog.services.values() if s.jurisdiction_id == rec.id)
        print(f"{rec.id:<28} {rec.data.kind.value:<9} {count:>3} services  {rec.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="civic-atlas",
        description="An open catalog of how to use local government services.",
    )
    parser.add_argument("--version", action="version", version=f"civic-atlas {__version__}")
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="path to a 'jurisdictions' folder (default: bundled data or $CIVIC_ATLAS_DATA)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="check every catalog file and cross-reference")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    p.add_argument("--quiet", action="store_true", help="only print errors")
    p.add_argument("--skip-schema", action="store_true", help="skip the schema/ sync check")
    p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("schema", help="regenerate schema/*.schema.json from the models")
    p.add_argument("--check", action="store_true", help="fail if the files are out of date")
    p.set_defaults(func=_cmd_schema)

    p = sub.add_parser("list", help="list jurisdictions and service counts")
    p.set_defaults(func=_cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
