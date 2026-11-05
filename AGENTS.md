# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository.

**Scope: civic-atlas covers non-emergency services only. It does not detect, classify or route
emergencies.** It can point people to non-emergency lines (such as the police non-emergency
number), utility service lines, and City or County services such as health clinics and medical
or social services. Don't add emergency detection, emergency or crisis numbers (911, 988), or
"call 911" logic. `civic-atlas validate` rejects emergency numbers. To revisit this, open an
issue referencing [docs/adr/0003-non-emergency-scope.md](docs/adr/0003-non-emergency-scope.md).

## What this repo is

- `jurisdictions/`: the catalog (CC0). YAML, with folders mirroring Open Civic Data ids. See
  [docs/data-model.md](docs/data-model.md).
- `src/civic_atlas/`: Python package (MIT). Models, loader, search, routing, MCP server, CLI.
- `plugins/`, `.claude-plugin/`, `integrations/`: ways to connect it to AI clients.

## Commands

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format .
uv run civic-atlas validate        # after any data change
uv run civic-atlas schema          # after changing models.py
```

Use `uv` for everything Python. Don't use pip.

## Rules

- **Data facts need an official source.** Every phone number, URL, fee and rule must appear on a
  page in `provenance.source_urls`. Never invent or "fill in" facts from memory.
- **New or changed entries are `status: draft`.** Only a human who checked every fact sets
  `verified`.
- **Write steps in your own words.** Don't copy government page text.
- **The MCP server stays offline and read-only.** No network calls, no tools that submit
  requests or payments, no handling of personal data. See
  [docs/legal-and-safety.md](docs/legal-and-safety.md).
- Keep runtime dependencies to `mcp`, `pydantic` and `ruamel.yaml` unless a maintainer agrees
  otherwise.
