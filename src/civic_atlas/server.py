"""Reference MCP server for civic-atlas.

Offline and read-only by design: every tool answers from the YAML catalog bundled with the package.
Nothing here makes a network request, submits a form, or handles personal information.

Run it with ``civic-atlas serve`` (stdio). See README.md for wiring it into Claude.
"""

from __future__ import annotations

import os
from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from civic_atlas import __version__
from civic_atlas.catalog import DISCLAIMER, Catalog, Relation
from civic_atlas.loader import JurisdictionRecord
from civic_atlas.models import Category
from civic_atlas.routing import danger_line, emergency_block, emergency_number, who_to_contact

DEFAULT_JURISDICTION_ENV = "CIVIC_ATLAS_DEFAULT_JURISDICTION"
FALLBACK_DEFAULT = "us/nc/place/raleigh"

INSTRUCTIONS = """\
civic-atlas helps people find and use local government services: who to contact, which website
or phone line to use, what to bring, and the steps to follow. Coverage starts with Raleigh, North
Carolina, together with Wake County and North Carolina services.

How to use these tools:
- For "who do I call / where do I go" questions, use who_to_contact first.
- To find how to do a task, use search_services, then get_service for steps.
- get_key_contacts gives the short list of numbers and sites worth saving on a phone.

Rules for answering people:
- Safety first. If anything suggests an emergency or that someone is in danger, tell them to call
  911 right away, before anything else.
- This is an independent volunteer catalog, not an official government source. Say so when it
  matters, cite the source_urls, and tell people to confirm details on the official site,
  especially for payments, deadlines and eligibility.
- Entries marked status "draft" or "needs-review" have not been checked by a person recently.
  Mention this when you rely on one.
- People complete every step themselves on the official website, app or phone line. Never offer
  to submit a request, make a payment, or sign in for them. Never ask for passwords, account
  numbers or payment details.
- Pay attention to who provides a service (City, County, State or nonprofit). Mixing these up is
  the most common source of confusion, so name the right one.
"""

READ_ONLY = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)

JurisdictionArg = Annotated[
    str | None,
    Field(
        description=(
            "Jurisdiction id (e.g. 'us/nc/place/raleigh'), OCD id, or short name ('raleigh'). "
            "Defaults to the server's default jurisdiction."
        )
    ),
]


def _default_jurisdiction(catalog: Catalog, requested: str | None) -> str:
    for candidate in (requested, os.environ.get(DEFAULT_JURISDICTION_ENV), FALLBACK_DEFAULT):
        if not candidate:
            continue
        try:
            return catalog.resolve(candidate).id
        except LookupError:
            continue
    places = sorted(r.id for r in catalog.jurisdictions.values() if r.data.kind.value == "place")
    return places[0] if places else sorted(catalog.jurisdictions)[0]


def _provenance(prov) -> dict[str, Any]:
    return prov.model_dump(mode="json", exclude_none=True)


def _jurisdiction_label(rec: JurisdictionRecord) -> dict[str, str]:
    return {"id": rec.id, "name": rec.name, "kind": rec.data.kind.value}


def build_server(
    catalog: Catalog | None = None, default_jurisdiction: str | None = None
) -> MCPServer:
    """Create the MCP server. Pass a ``catalog`` to serve other data (tests use fixtures)."""
    catalog = catalog or Catalog.load()
    default_jid = _default_jurisdiction(catalog, default_jurisdiction)

    mcp = MCPServer(
        "civic-atlas",
        title="civic-atlas: local government services guide (unofficial)",
        instructions=INSTRUCTIONS,
        version=__version__,
        website_url="https://github.com/yecodywang/civic-atlas",
    )

    def resolve(ref: str | None) -> JurisdictionRecord:
        try:
            return catalog.resolve(ref or default_jid)
        except LookupError as exc:
            raise ToolError(str(exc)) from None

    @mcp.tool(annotations=READ_ONLY)
    def list_jurisdictions() -> dict[str, Any]:
        """List the places this catalog covers: cities, counties, states, and how they relate."""
        items = []
        for rec in sorted(catalog.jurisdictions.values(), key=lambda r: r.id):
            items.append(
                {
                    **_jurisdiction_label(rec),
                    "ocd_id": rec.ocd_id,
                    "parent": rec.parent_id,
                    "overlaps": [o.model_dump(exclude_none=True) for o in rec.data.overlaps],
                    "service_count": sum(
                        1 for s in catalog.services.values() if s.jurisdiction_id == rec.id
                    ),
                }
            )
        return {
            "default_jurisdiction": default_jid,
            "jurisdictions": items,
            "safety": danger_line(catalog.jurisdictions[default_jid].country),
            "disclaimer": DISCLAIMER,
        }

    @mcp.tool(annotations=READ_ONLY)
    def search_services(
        query: Annotated[
            str,
            Field(
                description="What the person wants to do, in their words. Empty lists everything."
            ),
        ],
        jurisdiction: JurisdictionArg = None,
        category: Annotated[
            Category | None,
            Field(description="Optional task-menu group to filter by."),
        ] = None,
        limit: Annotated[int, Field(ge=1, le=50)] = 8,
    ) -> dict[str, Any]:
        """Find services for a task, such as 'report a pothole' or 'pay my water bill'.

        Searches the place itself, the counties it lies in, and its state. Each result says who
        provides it. Call get_service with a result's id for the steps.
        """
        home = resolve(jurisdiction)
        hits = catalog.search(query, home.id, category=category, limit=limit)
        results = []
        for h in hits:
            d = h.service.data
            results.append(
                {
                    "id": d.id,
                    "title": d.title,
                    "summary": d.summary,
                    "provided_by": h.jurisdiction.name,
                    "provider": d.provider,
                    "provider_type": d.provider_type.value,
                    "category": d.category.value,
                    "referral_only": d.referral_only,
                    "status": d.provenance.status.value,
                    "last_checked": d.provenance.last_checked.isoformat(),
                    "source_urls": [str(u) for u in d.provenance.source_urls],
                    "scope": h.relation.value,
                    "score": h.score,
                }
            )
        out: dict[str, Any] = {
            "query": query,
            "jurisdiction": _jurisdiction_label(home),
            "safety": danger_line(home.country),
        }
        # People often search first, even in an emergency, so search gets the same check.
        emergency = emergency_block(catalog, query, home.id)
        if emergency:
            out["emergency"] = emergency
        out["results"] = results
        if not results:
            out["tip"] = (
                "No catalog entry matched. Try who_to_contact with the situation, or "
                "get_key_contacts for the general help lines."
            )
        out["disclaimer"] = DISCLAIMER
        return out

    @mcp.tool(annotations=READ_ONLY)
    def get_service(
        service_id: Annotated[str, Field(description="A service id from search_services.")],
    ) -> dict[str, Any]:
        """Get everything about one service: channels, what to bring, steps, cost, and sources."""
        try:
            svc = catalog.get_service(service_id)
        except LookupError as exc:
            raise ToolError(f"{exc}. Use search_services to find ids.") from None
        rec = catalog.jurisdictions[svc.jurisdiction_id]
        body = svc.data.model_dump(mode="json", exclude_none=True)
        body.pop("provenance", None)
        return {
            **body,
            "provided_by": _jurisdiction_label(rec),
            "provenance": _provenance(svc.data.provenance),
            "safety": danger_line(rec.country),
            "reminder": (
                "The person should do each step themselves on the official site, app or phone "
                "line. Do not submit anything for them or ask for passwords or account numbers."
            ),
            "disclaimer": DISCLAIMER,
        }

    @mcp.tool(name="who_to_contact", annotations=READ_ONLY)
    def who_to_contact_tool(
        situation: Annotated[
            str,
            Field(description="The situation in plain words, e.g. 'my trash wasn't picked up'."),
        ],
        jurisdiction: JurisdictionArg = None,
    ) -> dict[str, Any]:
        """Decide where to go: 911, a non-emergency line, the city, the county, or the state.

        Always checks for emergencies first. Returns the best matching routes, or a general help
        line when nothing matches.
        """
        home = resolve(jurisdiction)
        return who_to_contact(catalog, situation, home.id)

    @mcp.tool(annotations=READ_ONLY)
    def get_key_contacts(jurisdiction: JurisdictionArg = None) -> dict[str, Any]:
        """The short list of phone numbers and websites worth saving, for a place and its county."""
        home = resolve(jurisdiction)
        groups = []
        for rec, relation in catalog.scope(home.id):
            if relation is Relation.OVERLAP:
                continue
            if not (rec.data.key_contacts or rec.data.websites):
                continue
            groups.append(
                {
                    **_jurisdiction_label(rec),
                    "contacts": [
                        c.model_dump(mode="json", exclude_none=True) for c in rec.data.key_contacts
                    ],
                    "websites": [w.model_dump(mode="json") for w in rec.data.websites],
                    "provenance": _provenance(rec.data.provenance),
                }
            )
        return {
            "jurisdiction": _jurisdiction_label(home),
            "emergency_number": emergency_number(home.country),
            "safety": danger_line(home.country),
            "groups": groups,
            "disclaimer": DISCLAIMER,
        }

    return mcp


def main(default_jurisdiction: str | None = None) -> None:
    build_server(default_jurisdiction=default_jurisdiction).run()


if __name__ == "__main__":
    main()
