"""Command-line interface: ``civic-atlas <command>``."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from civic_atlas import __version__


def _cmd_serve(args: argparse.Namespace) -> int:
    from civic_atlas.catalog import Catalog, CatalogError
    from civic_atlas.server import build_server

    try:
        catalog = Catalog.load(args.data)
    except CatalogError as exc:
        # stdout belongs to the MCP protocol; report problems on stderr.
        print(f"civic-atlas: cannot start: {exc}", file=sys.stderr)
        return 1
    build_server(catalog, default_jurisdiction=args.jurisdiction).run()
    return 0


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


def _cmd_render(args: argparse.Namespace) -> int:
    from civic_atlas.catalog import Catalog
    from civic_atlas.render import render_all

    catalog = Catalog.load(args.data)
    written = render_all(catalog, args.jurisdiction, args.out)
    print(f"wrote {len(written)} files to {written[0].parent}")
    return 0


def _cmd_check_links(args: argparse.Namespace) -> int:
    from civic_atlas.catalog import Catalog
    from civic_atlas.linkcheck import check_links

    catalog = Catalog.load(args.data)
    results = check_links(catalog, delay=args.delay, limit=args.limit)
    counts = Counter(r.outcome for r in results)
    for r in results:
        if r.outcome != "ok" or args.verbose:
            print(
                f"{r.outcome.upper():<13} {r.url}\n              {r.detail}; used by {', '.join(r.used_by)}"
            )
    print(
        f"\n{len(results)} links: {counts['ok']} ok, {counts['unverifiable']} unverifiable, "
        f"{counts['broken']} broken."
    )
    return 1 if counts["broken"] else 0


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

    p = sub.add_parser("serve", help="run the MCP server over stdio")
    p.add_argument(
        "--jurisdiction",
        default=None,
        help="default jurisdiction for tools (default: $CIVIC_ATLAS_DEFAULT_JURISDICTION or raleigh)",
    )
    p.set_defaults(func=_cmd_serve)

    p = sub.add_parser("validate", help="check every catalog file and cross-reference")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    p.add_argument("--quiet", action="store_true", help="only print errors")
    p.add_argument("--skip-schema", action="store_true", help="skip the schema/ sync check")
    p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("schema", help="regenerate schema/*.schema.json from the models")
    p.add_argument("--check", action="store_true", help="fail if the files are out of date")
    p.set_defaults(func=_cmd_schema)

    p = sub.add_parser("render", help="write printable Markdown task cards for a jurisdiction")
    p.add_argument("--jurisdiction", default="raleigh", help="jurisdiction id or short name")
    p.add_argument("--out", type=Path, default=Path("build/cards"), help="output folder")
    p.set_defaults(func=_cmd_render)

    p = sub.add_parser("check-links", help="check catalog URLs (slow and polite; uses the network)")
    p.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    p.add_argument("--limit", type=int, default=None, help="only check the first N URLs")
    p.add_argument("--verbose", action="store_true", help="also list links that are ok")
    p.set_defaults(func=_cmd_check_links)

    p = sub.add_parser("list", help="list jurisdictions and service counts")
    p.set_defaults(func=_cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
