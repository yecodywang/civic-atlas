"""Render printable task cards and a take-home guide (Markdown) from the catalog.

The course proposal describes one-page, step-by-step task cards for each task on the menu, which
together form a take-home guide. This module produces exactly that from the catalog, so the
printed material and the MCP server never disagree.

Output (for ``--jurisdiction raleigh``)::

    build/cards/us-nc-place-raleigh/
      README.md            task menu, grouped like the course's menu
      key-contacts.md      numbers and sites to save on your phone
      who-to-contact.md    the routing chart (City, County, State)
      <service-id>.md      one card per service
"""

from __future__ import annotations

from pathlib import Path

from civic_atlas.catalog import DISCLAIMER, SCOPE_NOTE, Catalog, Relation
from civic_atlas.loader import ServiceRecord
from civic_atlas.models import Category, Channel, Status

CATEGORY_TITLES = {
    Category.FIX_REPORT: "Fix & report",
    Category.PAY_MANAGE: "Pay & manage",
    Category.STAY_INFORMED: "Stay informed & safe",
    Category.FIND_HELP: "Find help",
    Category.HAVE_A_SAY: "Have a say",
    Category.CONTACT: "Know who to contact",
}

STATUS_TEXT = {
    Status.DRAFT: "Draft: compiled from official pages but not yet checked by a volunteer.",
    Status.VERIFIED: "Verified by a volunteer.",
    Status.NEEDS_REVIEW: "Needs review: this may be out of date.",
}


def _channel_line(ch: Channel) -> str:
    parts = [f"**{ch.label}**"]
    if ch.phone:
        parts.append(f"call {ch.phone}" if ch.type.value == "phone" else f"text {ch.phone}")
    if ch.email:
        parts.append(f"email {ch.email}")
    if ch.url:
        parts.append(f"<{ch.url}>")
    line = ": ".join([parts[0], ", ".join(parts[1:])]) if len(parts) > 1 else parts[0]
    extras = [x for x in (ch.hours, ch.purpose, ch.notes) if x]
    if extras:
        line += f" ({'; '.join(extras)})"
    return f"- {line}"


def render_card(catalog: Catalog, svc: ServiceRecord) -> str:
    d = svc.data
    rec = catalog.jurisdictions[svc.jurisdiction_id]
    out = [f"# {d.title}", ""]
    out.append(f"**Provided by:** {d.provider} ({rec.name})")
    out += ["", d.summary, ""]
    if d.referral_only:
        out += ["*This card points you to the right place. Ask them for the full steps.*", ""]

    out += ["## Ways to do it", ""] + [_channel_line(c) for c in d.channels] + [""]
    if d.what_you_need:
        out += ["## What you need", ""] + [f"- {x}" for x in d.what_you_need] + [""]
    if d.steps:
        for title, steps in (
            ("Steps online (phone, tablet or computer)", d.steps.online),
            ("Steps in the app", d.steps.app),
            ("Steps by phone", d.steps.call),
            ("Steps in person", d.steps.in_person),
        ):
            if steps:
                out += [f"## {title}", ""] + [f"{i}. {s}" for i, s in enumerate(steps, 1)] + [""]
    good = []
    if d.cost:
        good.append(f"**Cost:** {d.cost}")
    if d.eligibility:
        good.append(f"**Who can use it:** {d.eligibility}")
    good += d.notes
    if good:
        out += ["## Good to know", ""] + [f"- {x}" for x in good] + [""]
    if d.related:
        links = [
            f"[{catalog.services[r].data.title}]({r}.md)"
            for r in d.related
            if r in catalog.services
        ]
        out += ["## Related", ""] + [f"- {link}" for link in links] + [""]

    prov = d.provenance
    out += [
        "---",
        "",
        f"> {SCOPE_NOTE}",
        ">",
        f"> {STATUS_TEXT[prov.status]} Last checked {prov.last_checked.isoformat()}.",
        "> Sources: " + ", ".join(f"<{u}>" for u in prov.source_urls),
        ">",
        f"> {DISCLAIMER}",
        "",
    ]
    return "\n".join(out)


def render_index(catalog: Catalog, jurisdiction: str) -> str:
    home = catalog.resolve(jurisdiction)
    by_cat: dict[Category, list[tuple[ServiceRecord, str]]] = {}
    for rec, relation in catalog.scope(home.id):
        if relation is Relation.OVERLAP:
            continue
        for svc in catalog.services.values():
            if svc.jurisdiction_id == rec.id:
                by_cat.setdefault(svc.data.category, []).append((svc, rec.name))
    out = [
        f"# {home.name}: task menu",
        "",
        "Pick three tasks you want to get done. Each card has the steps.",
        "",
    ]
    for cat in Category:
        items = sorted(by_cat.get(cat, []), key=lambda t: t[0].data.title)
        if not items:
            continue
        out += [f"## {CATEGORY_TITLES[cat]}", ""]
        for svc, owner in items:
            flag = " (referral)" if svc.data.referral_only else ""
            out.append(f"- [ ] [{svc.data.title}]({svc.id}.md), {owner}{flag}")
        out.append("")
    out += [
        "Also: [Key contacts to save on your phone](key-contacts.md) and "
        "[Who do I contact?](who-to-contact.md)",
        "",
        f"> {SCOPE_NOTE} {DISCLAIMER}",
        "",
    ]
    return "\n".join(out)


def render_key_contacts(catalog: Catalog, jurisdiction: str) -> str:
    home = catalog.resolve(jurisdiction)
    out = [f"# Key contacts: {home.name}", "", "Save these in your phone's contacts.", ""]
    for rec, relation in catalog.scope(home.id):
        if relation is Relation.OVERLAP or not (rec.data.key_contacts or rec.data.websites):
            continue
        out += [f"## {rec.name}", ""]
        out += [_channel_line(c) for c in rec.data.key_contacts]
        out += [f"- {w.label}: <{w.url}>" for w in rec.data.websites]
        out.append("")
    out += [f"> {DISCLAIMER}", ""]
    return "\n".join(out)


def render_routing(catalog: Catalog, jurisdiction: str) -> str:
    home = catalog.resolve(jurisdiction)
    out = [
        f"# Who do I contact? ({home.name})",
        "",
        f"*{SCOPE_NOTE}*",
        "",
        "| Situation | Who handles it | How to reach them |",
        "|---|---|---|",
    ]
    for rec, _relation in catalog.scope(home.id):
        if rec.routing is None:
            continue
        for rule in rec.routing.rules:
            if rule.channel:
                how = rule.channel.phone or rule.channel.email or str(rule.channel.url or "")
            elif rule.service:
                how = f"[see card]({rule.service}.md)"
            else:
                how = ""
            out.append(f"| {rule.situation} | {rule.go_to} | {how} |")
        fb = rec.routing.fallback
        out += ["", f"**Not sure?** {fb.explanation} {fb.channel.phone or fb.channel.url}", ""]
    out += [f"> {DISCLAIMER}", ""]
    return "\n".join(out)


def render_all(catalog: Catalog, jurisdiction: str, out_dir: Path) -> list[Path]:
    home = catalog.resolve(jurisdiction)
    target = out_dir / home.id.replace("/", "-")
    target.mkdir(parents=True, exist_ok=True)
    files = {
        "README.md": render_index(catalog, home.id),
        "key-contacts.md": render_key_contacts(catalog, home.id),
        "who-to-contact.md": render_routing(catalog, home.id),
    }
    for rec, relation in catalog.scope(home.id):
        if relation is Relation.OVERLAP:
            continue
        for svc in catalog.services.values():
            if svc.jurisdiction_id == rec.id:
                files[f"{svc.id}.md"] = render_card(catalog, svc)
    written = []
    for name, text in files.items():
        path = target / name
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written
