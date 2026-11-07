# Roadmap

Rough priorities, not promises. Work in progress is tracked on the
[civic-atlas roadmap board](https://github.com/users/yecodywang/projects/1) and in
[issues](https://github.com/yecodywang/civic-atlas/issues). Open an issue to discuss anything here.

## Now (pilot)

- [ ] Human verification of the 68 Raleigh, Wake and NC draft entries (#26)
- [ ] Re-check time-sensitive facts (#27)
- [ ] Try the MCP server and printed cards with the *Raleigh at Your Fingertips* pilot (#29)
- [ ] Follow up on the "not ingested" items in [docs/research/rnc-fall-2026-index-coverage.md](research/rnc-fall-2026-index-coverage.md) (#28)
- [x] Publish the repository; enable private vulnerability reporting, Pages, branch protection

## Four ways to use the catalog

Each has an epic issue with sub-issues:

1. Plain files that agents can read without tools (#6)
2. The MCP server, preferred when available (#9, including the mcp-builder review in #20)
3. GitHub Pages and the wiki (#12)
4. Open data registries: exports, versioned releases, AWS RODA and BigQuery Analytics Hub (#15)

Contributor tooling (ingest and validate skills, guidance on government websites) is #21.

## Next

- [ ] Tagged releases; the plugin pins a release (#11)
- [ ] MCP Bundle (`.mcpb`) for one-click install in Claude Desktop
- [ ] Printable PDF or HTML output from `render`, with large-print styling
- [ ] Spanish translations of cards (fields for translated titles and steps)
- [ ] Neighboring places: Cary, Garner, Durham (the city), Wake County towns
- [ ] More State services: courts, DMV, NC Medicaid details

## Later

- [ ] Optional semantic search (kept optional, to keep the core dependency-light)
- [ ] Live, read-only adapters under the [live adapter policy](legal-and-safety.md#live-adapter-policy-for-the-future)
- [ ] A nonprofit or fiscal sponsor home for the project
