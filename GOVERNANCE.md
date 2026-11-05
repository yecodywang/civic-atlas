# Governance

civic-atlas is young and governance is deliberately light. It will grow as the project does.

## Roles

- **Maintainers** review and merge changes, triage issues, and look after the code, schema and CI.
  The founding maintainer is the repository owner.
- **Jurisdiction stewards** look after the catalog for one place, such as Raleigh. A steward
  re-verifies entries, reviews data pull requests for that place, and keeps an eye on local
  changes. Each jurisdiction lists its stewards in `jurisdiction.yaml` (`stewards:`). Anyone who has
  made several good data contributions to a place can ask to become a steward.
- **Contributors** are everyone else who files issues, verifies entries, or sends pull requests.

## How decisions are made

- Most changes need one maintainer or steward approval.
- Changes to the schema, the safety rules in [docs/legal-and-safety.md](docs/legal-and-safety.md),
  or the licenses need a maintainer approval and an open issue describing the change first.
- Significant design decisions are recorded as Architecture Decision Records in
  [docs/adr/](docs/adr/).

## Principles

1. **Accuracy first.** Corrections take priority over new features. See
   [CORRECTIONS.md](CORRECTIONS.md).
2. **Residents do every step themselves.** This project explains and routes. It never acts on
   someone's behalf with a government service.
3. **Independent and transparent.** The project is not official, and it never presents itself as
   official. Every fact links to its source.
4. **Welcoming to newcomers**, including students, youth volunteers and government staff. See the
   [Code of Conduct](CODE_OF_CONDUCT.md).

## Adding a new place

Anyone can propose a new municipality or county. See
[docs/adding-a-jurisdiction.md](docs/adding-a-jurisdiction.md). A new place gets merged once it has
at least one steward and passes `civic-atlas validate`.
