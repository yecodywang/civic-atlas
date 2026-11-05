"""In-memory catalog: jurisdiction lookup, scoping, and plain keyword search."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path

from civic_atlas.loader import JurisdictionRecord, LoadResult, ServiceRecord, load
from civic_atlas.models import Category
from civic_atlas.text import contains_phrase, tokens

DISCLAIMER = (
    "civic-atlas is an independent volunteer project, not an official government source. "
    "Confirm details on the official site linked in source_urls before relying on them."
)


class Relation(StrEnum):
    """How a jurisdiction in scope relates to the one the user asked about."""

    SELF = "self"
    PRIMARY_OVERLAP = "primary-overlap"  # e.g. Wake County for Raleigh
    ANCESTOR = "ancestor"  # e.g. North Carolina, United States
    OVERLAP = "overlap"  # e.g. Durham County for Raleigh (only part of the city)


_RELATION_WEIGHT = {
    Relation.SELF: 1.0,
    Relation.PRIMARY_OVERLAP: 0.9,
    Relation.ANCESTOR: 0.8,
    Relation.OVERLAP: 0.5,
}


class CatalogError(Exception):
    """Raised when the catalog data has errors and cannot be served."""


@dataclass(frozen=True)
class SearchHit:
    service: ServiceRecord
    jurisdiction: JurisdictionRecord
    relation: Relation
    score: float


class Catalog:
    def __init__(self, result: LoadResult) -> None:
        self.root = result.root
        self.jurisdictions = result.jurisdictions
        self.services = result.services
        self.issues = result.issues

    @classmethod
    def load(cls, root: Path | None = None, *, strict: bool = True) -> Catalog:
        result = load(root)
        if strict and result.errors:
            lines = "\n".join(f"  {e}" for e in result.errors)
            raise CatalogError(f"catalog has {len(result.errors)} error(s):\n{lines}")
        return cls(result)

    # Jurisdictions

    def resolve(self, ref: str) -> JurisdictionRecord:
        """Find a jurisdiction by id (``us/nc/place/raleigh``), OCD id, alias, or unique name."""
        key = ref.strip().strip("/").lower()
        if key in self.jurisdictions:
            return self.jurisdictions[key]
        for rec in self.jurisdictions.values():
            if key == rec.ocd_id or key in (a.lower() for a in rec.data.aliases):
                return rec
        by_name = [
            r
            for r in self.jurisdictions.values()
            if key in (r.data.name.lower(), r.id.rsplit("/", 1)[-1])
        ]
        if len(by_name) == 1:
            return by_name[0]
        known = ", ".join(sorted(self.jurisdictions))
        raise LookupError(f"unknown jurisdiction {ref!r}. Known: {known}")

    def ancestors(self, rec: JurisdictionRecord) -> list[JurisdictionRecord]:
        out = []
        parent = rec.parent_id
        while parent:
            prec = self.jurisdictions.get(parent)
            if prec is None:
                break
            out.append(prec)
            parent = prec.parent_id
        return out

    def scope(self, ref: str) -> list[tuple[JurisdictionRecord, Relation]]:
        """The jurisdiction itself, the governments it overlaps, and its ancestors, nearest first."""
        rec = self.resolve(ref)
        seen = {rec.id}
        out = [(rec, Relation.SELF)]
        for ov in sorted(rec.data.overlaps, key=lambda o: not o.primary):
            orec = self.jurisdictions.get(ov.id)
            if orec and orec.id not in seen:
                seen.add(orec.id)
                out.append((orec, Relation.PRIMARY_OVERLAP if ov.primary else Relation.OVERLAP))
        for anc in self.ancestors(rec):
            if anc.id not in seen:
                seen.add(anc.id)
                out.append((anc, Relation.ANCESTOR))
        return out

    # Services

    def get_service(self, service_id: str) -> ServiceRecord:
        try:
            return self.services[service_id.strip()]
        except KeyError:
            raise LookupError(f"unknown service id {service_id!r}") from None

    def search(
        self,
        query: str,
        jurisdiction: str,
        *,
        category: Category | str | None = None,
        limit: int = 10,
    ) -> list[SearchHit]:
        """Rank services in scope by simple keyword overlap with ``query``."""
        q_tokens = tokens(query, drop_stopwords=True)
        q_all = tokens(query)
        cat = Category(category) if category else None
        scope = self.scope(jurisdiction)
        by_jid = {rec.id: rel for rec, rel in scope}
        hits: list[SearchHit] = []
        for svc in self.services.values():
            relation = by_jid.get(svc.jurisdiction_id)
            if relation is None:
                continue
            data = svc.data
            if cat and data.category is not cat:
                continue
            score = _score(data, q_tokens, q_all) if q_tokens else 1.0
            if score > 0:
                hits.append(
                    SearchHit(
                        service=svc,
                        jurisdiction=self.jurisdictions[svc.jurisdiction_id],
                        relation=relation,
                        score=round(score * _RELATION_WEIGHT[relation], 3),
                    )
                )
        hits.sort(key=lambda h: (-h.score, h.service.data.title))
        return hits[: max(1, limit)]

    def stale(self, *, today: date, max_age_days: int) -> list[str]:
        """Ids (or jurisdiction ids) whose ``last_checked`` is older than ``max_age_days``."""
        out = []
        for svc in self.services.values():
            if (today - svc.data.provenance.last_checked).days > max_age_days:
                out.append(svc.id)
        for rec in self.jurisdictions.values():
            if (today - rec.data.provenance.last_checked).days > max_age_days:
                out.append(rec.id)
        return out


def _score(data, q_tokens: list[str], q_all: list[str]) -> float:
    score = 0.0
    alias_tokens: set[str] = set()
    for alias in data.aliases:
        a = tokens(alias)
        alias_tokens.update(a)
        if len(a) > 1 and contains_phrase(q_all, a):
            score += 6
    title = set(tokens(data.title))
    ident = set(tokens(data.id))
    body = set(tokens(data.summary)) | set(tokens(data.provider)) | set(tokens(data.category.value))
    for t in q_tokens:
        if t in alias_tokens:
            score += 3
        if t in title:
            score += 3
        elif t in ident:
            score += 2
        if t in body:
            score += 1
    return score
