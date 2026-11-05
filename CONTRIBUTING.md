# Contributing to civic-atlas

Thank you for helping! This project is meant to be easy to contribute to, whether you're a
student, a neighbor who noticed a wrong phone number, a developer, or government staff.

## Ways to help

| You want to... | Do this |
|---|---|
| Report something wrong | Open a **Report inaccurate info** issue. No code needed. |
| Check an entry against its source | Follow the [verification guide](docs/verification-guide.md) |
| Add a missing task | Copy `jurisdictions/_template/services/_example-service.yaml` (see below) |
| Add a new city or county | See [docs/adding-a-jurisdiction.md](docs/adding-a-jurisdiction.md) |
| Improve the code or MCP server | See "Working on the code" below |

## Ground rules for catalog data

These protect the people who rely on the catalog. Reviewers will check every one.

1. **Only facts you can source.** Every phone number, URL, fee and rule must appear on an
   official page listed in `provenance.source_urls`. Never guess or fill gaps from memory. If
   two official pages disagree, record both in `notes`.
2. **Your own words.** Write summaries and steps yourself, in plain language. Don't copy text
   or images from government websites.
3. **Be honest about status.** New or changed entries are `status: draft`. Only someone who
   has checked every fact against the source sets `verified`, with `verified_by` (their GitHub
   handle) and `verified_on`.
4. **Update `last_checked`** whenever you compare an entry against its sources.
5. **People do every step themselves.** Steps describe what the resident does. Never suggest
   that someone else should enter their passwords or payment details.
6. **Not official.** Never use government logos or seals, and never describe this project as
   official.
7. **No test submissions.** Don't file practice requests with a government service to see how a
   form works. That creates real work for staff.

## Adding or editing a service

1. Copy `jurisdictions/_template/services/_example-service.yaml` into the right
   `services/` folder (for example `jurisdictions/us/nc/place/raleigh/services/`).
2. Rename it to `<id>.yaml`, using a short lowercase id with hyphens, such as
   `report-pothole.yaml`. The `id:` inside the file must match.
3. Fill it in. In VS Code with the recommended YAML extension, you get autocomplete and checks
   as you type (from `schema/`).
4. Check your work:

   ```bash
   uv run civic-atlas validate
   uv run pytest
   ```

5. Open a pull request and fill in the checklist.

**YAML tips.** Indent with spaces, not tabs. Text containing `: ` needs quotes, so write
`label: "Hours: 9 to 5"`. Bare numbers such as `211` are fine in phone numbers and aliases.

## Working on the code

```bash
uv sync                          # install everything, including dev tools
uv run pytest                    # tests
uv run ruff check . && uv run ruff format .
uv run civic-atlas schema        # regenerate schema/ after changing models.py
uv run civic-atlas serve         # run the MCP server on stdio
```

- Python 3.11+, managed with [uv](https://docs.astral.sh/uv/).
- Runtime dependencies are deliberately few: `mcp`, `pydantic` and `ruamel.yaml`. Discuss
  before adding one.
- The MCP server must stay offline and read-only. See
  [docs/legal-and-safety.md](docs/legal-and-safety.md) and
  [docs/adr/0001-offline-static-catalog.md](docs/adr/0001-offline-static-catalog.md).
- Changes to emergency handling in `routing.py` need tests for both missed emergencies and
  false alarms.

## Sign your commits (DCO)

We use the [Developer Certificate of Origin](DCO) instead of a contributor license agreement.
By adding a `Signed-off-by` line, you certify that you have the right to submit your
contribution under this project's licenses (MIT for code, CC0 for data):

```bash
git commit -s -m "Fix the missed-collection phone hours"
```

If you're contributing as part of your job, check with your employer first. See
[docs/contributing-as-government-staff.md](docs/contributing-as-government-staff.md).

## Code of Conduct

Everyone taking part agrees to the [Code of Conduct](CODE_OF_CONDUCT.md).
