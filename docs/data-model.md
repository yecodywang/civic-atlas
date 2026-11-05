# Data model

The authoritative definitions are in [`src/civic_atlas/models.py`](../src/civic_atlas/models.py).
The JSON Schemas in [`schema/`](../schema/) are generated from it. This page explains the ideas.

## Jurisdictions: the folder is the id

Folders under `jurisdictions/` mirror [Open Civic Data division
ids](https://open-civic-data.readthedocs.io/en/latest/ocdids.html):

| Folder | Kind | OCD id |
|---|---|---|
| `us/` | country | `ocd-division/country:us` |
| `us/nc/` | state | `ocd-division/country:us/state:nc` |
| `us/nc/county/wake/` | county | `ocd-division/country:us/state:nc/county:wake` |
| `us/nc/place/raleigh/` | place (city or town) | `ocd-division/country:us/state:nc/place:raleigh` |
| `us/nc/district/<name>/` | special district | `.../district:<name>` |

Below the state, folders come in `<type>/<name>` pairs. Counties and places are **siblings**,
not nested, because cities can cross county lines: most of Raleigh is in Wake County and a small
part is in Durham County. The counties a place lies in go in its `overlaps:` list, with at most
one marked `primary`.

As in OCD, a county is nested in a place's path only to tell same-named places apart. For
example, Pennsylvania has many "Franklin Township"s, so one becomes
`us/pa/county/adams/place/franklin`.

Each jurisdiction folder holds:

- `jurisdiction.yaml`: name, kind, aliases, overlaps, websites, key contacts, emergency facts
  (such as whether text-to-911 works), stewards, and provenance
- `services/<id>.yaml`: one file per task
- `routing.yaml` (optional): the "who do I contact?" table

## Services

| Field | Meaning |
|---|---|
| `id` | Lowercase-with-hyphens, unique across the whole catalog, matching the file name |
| `title`, `summary` | Plain-language name and one or two sentences |
| `provider`, `provider_type` | Who actually runs it (`government`, `nonprofit`, `other`) |
| `category` | The task-menu group: `fix-report`, `pay-manage`, `stay-informed`, `find-help`, `have-a-say`, `contact` |
| `core_skill` | One of the four core skills: `know-who`, `report-request`, `stay-informed`, `accounts-payments` |
| `aliases` | Words people use ("trash", "garbage", "bin"). This drives search, so be generous |
| `channels` | Ways to do it: `web`, `phone`, `text`, `app`, `email`, `in-person`, with `url`, `phone`, `email`, `hours`, `purpose` |
| `what_you_need` | What to have ready |
| `steps` | Numbered steps: `online`, `app`, `call` |
| `cost`, `eligibility`, `notes` | Good-to-know details |
| `referral_only` | True when we point people somewhere rather than teach the steps |
| `related` | Ids of related services |
| `provenance` | Required. See below |

## Provenance (on every file)

| Field | Meaning |
|---|---|
| `source_urls` | The official pages the facts came from (at least one) |
| `last_checked` | When someone last compared the entry against its sources |
| `status` | `draft` (compiled, not yet human-verified), `verified`, or `needs-review` |
| `verified_by`, `verified_on` | Required for `verified`: the GitHub handle and date of the person who checked |
| `notes` | Caveats, such as two official pages disagreeing |

`civic-atlas validate` warns when `last_checked` is more than 180 days old.

## Routing tables

Each rule has a `situation`, `keywords`, `go_to`, the `jurisdiction` that handles it, and either a
`service` id or a `channel`, plus an `explanation`. A rule ranks higher when more of its keywords
appear in the person's words. The `fallback` is used when nothing matches.

Emergencies are **not** in routing tables. They are handled in code first; see
[legal-and-safety.md](legal-and-safety.md).
