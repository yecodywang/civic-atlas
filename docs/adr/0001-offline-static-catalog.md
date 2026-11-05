# ADR 0001: Offline, static catalog as the reference implementation

- Status: accepted
- Date: 2026-11-04

## Context

Similar projects such as Baltimore's `civic-connector` proxy live city APIs (311, transit, open
data) behind an MCP server, with caching. Our goal is different: explain *how to use* services
and *who to contact*. That information changes over months, not minutes, and it's mostly found on
web pages, not in APIs. Raleigh's own site also blocks automated clients.

## Decision

The reference MCP server answers only from a curated YAML catalog bundled with the package. It
makes no network requests and has no write actions. Freshness comes from human verification,
staleness warnings and a weekly link check, not from live calls.

## Consequences

- It is safe and cheap to run anywhere. It can't add load to government systems or act for
  anyone.
- It needs one runtime and three dependencies. It is easy to install and audit, and easy for
  students to understand.
- Answers can be out of date between verifications. We address this with provenance on every
  answer, `draft`/`needs-review` statuses and the corrections policy.
- Live data, if ever needed, goes through the [live adapter policy](../legal-and-safety.md).
