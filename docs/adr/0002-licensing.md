# ADR 0002: MIT for code, CC0 for data, DCO for contributions

- Status: accepted
- Date: 2026-11-04

## Context

Goals: anyone can fork or reuse the project, and government staff can review, contribute to and
reuse it without friction. There are no commercial goals. Prior art:

| Project | Code | Data |
|---|---|---|
| civic-connector (Baltimore MCP) | MIT | n/a (live APIs) |
| civic-ai-tools | MIT | CC0 (directory data) |
| Govdirectory | CC0 | CC0 |
| Open Referral HSDS | n/a | CC-BY-SA 4.0 (spec) |
| FixMyStreet | AGPL-3.0 | n/a |
| 18F / code.mil | public domain (CC0) | DCO for contributions |

## Decision

- **Code: MIT.** The shortest and most widely approved permissive license. Copyleft
  (GPL/AGPL) would protect against proprietary forks, which we don't mind, and often slows
  government and vendor legal review.
- **Data: CC0 1.0.** A government can copy entries straight into official printed task cards or
  web pages with no attribution line and no license review. The data is also compatible with
  Wikidata. Facts like phone numbers generally aren't copyrightable anyway; CC0 removes any
  doubt about the parts that are (our written steps and the catalog's structure).
- **Contributions: DCO sign-off** (`git commit -s`), not a CLA. A CLA is a contract that
  government lawyers would have to review; the DCO is a one-line certification.
- Both licenses include an "AS IS" no-warranty disclaimer, which is the project's main legal
  protection.

## Consequences

- Package metadata is `MIT AND CC0-1.0` with both license files, because the wheel bundles the
  data.
- Others may build commercial or closed products on this work. That's accepted.
- The project gets no legal guarantee of attribution. We ask for it politely instead.
