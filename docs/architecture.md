# Architecture

civic-atlas is a **data project with a small reference server**, not a web service.

```
 jurisdictions/**/*.yaml ──► loader.py ──► Catalog (in memory) ──┬─► server.py   MCP tools (stdio)
   (CC0 data, PRs)            ruamel.yaml   catalog.py search     ├─► render.py   task cards (Markdown)
                              + models.py   routing.py 911-first  ├─► validate.py CI checks
                              (Pydantic)                          └─► linkcheck.py weekly, polite
```

## Pieces

| Module | Job |
|---|---|
| `models.py` | Pydantic models for the three file kinds (jurisdiction, service, routing). The single source of truth; `schema/*.json` is generated from them. |
| `loader.py` | Finds the data folder, walks it, and turns folder paths into jurisdiction ids and OCD ids. Collects every problem instead of stopping at the first. |
| `catalog.py` | In-memory index: resolve a place by id, alias or OCD id; compute its *scope* (itself, the counties it overlaps, its ancestors); keyword search. |
| `routing.py` | `who_to_contact`: a hard-coded emergency check, then the routing tables in scope, then a fallback help line. |
| `server.py` | The MCP server (official MCP Python SDK, `MCPServer`, stdio). Five read-only tools. |
| `render.py` | Printable task menu, task cards, key-contacts sheet and routing chart. |
| `validate.py` | Cross-file checks (references, overlaps, duplicate ids, staleness) and schema drift. |
| `linkcheck.py` | The only network code. Checks catalog URLs slowly and politely. Never used by the server. |
| `cli.py` | `civic-atlas serve | validate | schema | render | check-links | list`. |

## Where the data comes from at runtime

1. `$CIVIC_ATLAS_DATA`, if set
2. `civic_atlas/_data/jurisdictions` inside the installed wheel (bundled at build time)
3. `jurisdictions/` in a source checkout

## Scope: how a question about Raleigh reaches County and State answers

`Catalog.scope("raleigh")` returns, nearest first:

1. `us/nc/place/raleigh` (self)
2. `us/nc/county/wake` (primary overlap)
3. `us/nc/county/durham` (partial overlap, ranked lower and left out of key contacts)
4. `us/nc` and `us` (ancestors)

Search and routing use this scope, and every result says which government provides it.

## Design constraints

- **Offline and read-only** ([ADR 0001](adr/0001-offline-static-catalog.md)). There is no network
  access, no writes, and no personal data.
- **Few dependencies**: `mcp`, `pydantic` and `ruamel.yaml`. Search is plain Python, so it's easy
  for students to read and change.
- **Safety in code, not data** ([legal-and-safety.md](legal-and-safety.md)). The emergency check,
  the danger line and the disclaimer can't be removed by editing YAML.
- **Multi-place from day one.** Nothing in the code is Raleigh-specific except the default
  jurisdiction for the server.
