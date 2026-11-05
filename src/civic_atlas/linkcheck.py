"""Polite link checker for the URLs in the catalog.

This is the only code in the project that makes network requests. It runs on a schedule in CI
(weekly), never from the MCP server. Rules (docs/legal-and-safety.md):

* one request at a time, with a pause between requests;
* a HEAD request first, falling back to GET only if HEAD isn't allowed;
* a generic User-Agent naming the project, with no personal contact details;
* sites that block automated clients (HTTP 401/403/429) are reported as "unverifiable" for a
  human to check, never retried aggressively or worked around.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Literal

from civic_atlas.catalog import Catalog

USER_AGENT = "civic-atlas-linkcheck/0.1 (+https://github.com/yecodywang/civic-atlas)"
BLOCKED_CODES = {401, 403, 429}

Outcome = Literal["ok", "unverifiable", "broken"]


@dataclass(frozen=True)
class LinkResult:
    url: str
    outcome: Outcome
    detail: str
    used_by: tuple[str, ...]


def collect_urls(catalog: Catalog) -> dict[str, set[str]]:
    """Every URL in the catalog, mapped to the entries that use it."""
    urls: dict[str, set[str]] = {}

    def add(url, where: str) -> None:
        if url:
            urls.setdefault(str(url), set()).add(where)

    for rec in catalog.jurisdictions.values():
        where = f"{rec.id}/jurisdiction.yaml"
        for u in rec.data.provenance.source_urls:
            add(u, where)
        for w in rec.data.websites:
            add(w.url, where)
        for c in rec.data.key_contacts:
            add(c.url, where)
        if rec.routing:
            rwhere = f"{rec.id}/routing.yaml"
            for u in rec.routing.provenance.source_urls:
                add(u, rwhere)
            for rule in rec.routing.rules:
                if rule.channel:
                    add(rule.channel.url, rwhere)
            add(rec.routing.fallback.channel.url, rwhere)
    for svc in catalog.services.values():
        for u in svc.data.provenance.source_urls:
            add(u, svc.id)
        for c in svc.data.channels:
            add(c.url, svc.id)
    return urls


def _request(url: str, method: str, timeout: float) -> int:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def check_url(url: str, *, timeout: float = 20.0) -> tuple[Outcome, str]:
    try:
        status = _request(url, "HEAD", timeout)
        if status in (405, 501):
            status = _request(url, "GET", timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "broken", f"connection failed: {exc}"
    if 200 <= status < 400:
        return "ok", str(status)
    if status in BLOCKED_CODES:
        return "unverifiable", f"HTTP {status} (site blocks automated checks; check by hand)"
    return "broken", f"HTTP {status}"


def check_links(
    catalog: Catalog, *, delay: float = 1.0, limit: int | None = None, timeout: float = 20.0
) -> list[LinkResult]:
    results = []
    items = sorted(collect_urls(catalog).items())
    if limit is not None:
        items = items[:limit]
    for i, (url, used_by) in enumerate(items):
        if i:
            time.sleep(delay)
        outcome, detail = check_url(url, timeout=timeout)
        results.append(LinkResult(url, outcome, detail, tuple(sorted(used_by))))
    return results
