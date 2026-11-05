# civic-atlas

**An open, community-maintained guide to using local government services, starting with
Raleigh, North Carolina.**

City services are spread across many departments, websites and phone numbers, and residents also
have to tell City services apart from County and State ones. civic-atlas collects the answers to
everyday questions in one open catalog:

- *Who do I contact?* 911, the police non-emergency line, the City, Wake County, or the State
- *How do I do it?* Which website or phone line to use, what to have ready, and step-by-step
  instructions
- *Where did this come from?* Every entry links to the official page it was compiled from and
  says when it was last checked

You can use the catalog in three ways:

1. **Ask an AI assistant.** A small, local [MCP](https://modelcontextprotocol.io) server lets
   Claude or another agent answer questions from the catalog.
2. **Print it.** `civic-atlas render` turns the catalog into a task menu, task cards and a
   "who do I contact?" chart, like the take-home guide in the
   *Raleigh at Your Fingertips* course proposal that started this project.
3. **Reuse the data.** The catalog is plain YAML under a public-domain dedication (CC0). Copy
   it, remix it, or build something better.

> **Independent and unofficial.** civic-atlas is a volunteer project. It is not affiliated with
> or endorsed by the City of Raleigh, Wake County, the State of North Carolina, or any other
> government. Always confirm details on the official site. See [NOTICE.md](NOTICE.md).

> **Not for emergencies.** civic-atlas covers non-emergency services only. It does not detect,
> classify or route emergencies. In an emergency, contact emergency services directly. It *does*
> point people to non-emergency lines (such as the police non-emergency number) and to City or
> County services such as health clinics. See
> [docs/adr/0003-non-emergency-scope.md](docs/adr/0003-non-emergency-scope.md).

## What's covered

| Place | What's included |
|---|---|
| City of Raleigh | 23 tasks: Ask Raleigh, reporting street, sidewalk, streetlight, graffiti, trash, flooding, water and noise problems, utility bills and AutoPay, RecLink and parks, alerts, smoke alarms, housing programs, Council and boards, plus a "who do I contact?" routing table |
| Wake County | Public health clinics, vaccines, free HIV/STI testing, WIC, Medicaid, low-cost primary care for the uninsured, ReadyWake alerts, property tax bills (including the City portion), tax relief programs. (Raleigh has no city health department; NC counties provide public health.) |
| North Carolina | NC 211 |
| Durham County | Stub only (a small part of Raleigh is in Durham County) |

All entries are currently **drafts**. They were compiled from official pages but haven't yet been
checked by a human volunteer. Helping verify them is the best way to start contributing; see the
[verification guide](docs/verification-guide.md).

## Quick start

You need [uv](https://docs.astral.sh/uv/) (it installs Python for you if needed).

```bash
git clone https://github.com/yecodywang/civic-atlas.git
cd civic-atlas
uv sync
uv run civic-atlas list        # what's in the catalog
uv run civic-atlas validate    # check the data
```

### Connect it to Claude Code

```bash
claude mcp add civic-atlas -- uv run --directory "$PWD" civic-atlas serve
```

Then ask things like:

- "My trash wasn't picked up. What do I do?"
- "Who do I call about my property tax bill in Raleigh?"
- "How do I set up AutoPay for my water bill?"
- "What alerts should I sign up for?"

Or install the plugin, which adds the server plus answering guidelines:

```text
/plugin install civic-atlas --marketplace yecodywang/civic-atlas
```

For Claude Desktop, VS Code, Cursor and other clients, see
[integrations/README.md](integrations/README.md).

### MCP tools

| Tool | What it does |
|---|---|
| `who_to_contact(situation)` | Routes a non-emergency situation to the right office: the City, the County, the State, a nonprofit, or a non-emergency line |
| `search_services(query)` | Finds tasks across the city, its county and the state, and says who provides each one |
| `get_service(service_id)` | Ways to do it, what you need, steps, cost, notes and sources |
| `get_key_contacts()` | The short list of numbers and sites worth saving on a phone |
| `list_jurisdictions()` | The places covered and how they relate |

The server is **offline and read-only**. It answers from the YAML bundled with the package,
makes no network requests, never submits anything for anyone, and never asks for personal
information. Answers include sources and a disclaimer, and the server's instructions state its
non-emergency scope.

### Print the task cards

```bash
uv run civic-atlas render --jurisdiction raleigh     # writes build/cards/us-nc-place-raleigh/
```

## How it's organized

```
jurisdictions/                 the catalog (CC0). Folders mirror Open Civic Data ids
  us/                          United States
    nc/                        North Carolina: NC 211
      county/wake/             Wake County: services/, jurisdiction.yaml
      county/durham/           Durham County (stub)
      place/raleigh/           City of Raleigh: services/, routing.yaml, jurisdiction.yaml
src/civic_atlas/               Python package (MIT): models, loader, search, routing, MCP server, CLI
schema/                        JSON Schema generated from the models (editor autocomplete)
plugins/civic-atlas/           Claude Code plugin
.claude-plugin/                plugin marketplace
integrations/                  other ways to connect
docs/                          architecture, data model, guides, decisions
tests/                         pytest, including checks on the real catalog
```

Counties and cities sit side by side under the state, because cities can cross county lines
(Raleigh is in both Wake and Durham counties). Which counties a city overlaps is recorded as data.
See [docs/data-model.md](docs/data-model.md).

## Contributing

Contributions of every size are welcome, and you don't need to be a programmer:

- **Report something wrong.** Open a
  [Report inaccurate info](https://github.com/yecodywang/civic-atlas/issues/new/choose) issue.
- **Verify an entry.** Check a draft against its official source and mark it verified
  ([guide](docs/verification-guide.md)).
- **Add a task or a place.** See [CONTRIBUTING.md](CONTRIBUTING.md) and
  [docs/adding-a-jurisdiction.md](docs/adding-a-jurisdiction.md).
- **Government staff:** corrections to descriptions of your own services are especially welcome.
  See [docs/contributing-as-government-staff.md](docs/contributing-as-government-staff.md).

Please read the [Code of Conduct](CODE_OF_CONDUCT.md). Contributions are accepted under the
[Developer Certificate of Origin](DCO) (`git commit -s`).

## Licenses

- **Code:** [MIT](LICENSE)
- **Catalog data** (`jurisdictions/`, `schema/`): [CC0 1.0](LICENSE-DATA), public domain. No
  permission or attribution needed.

Why these licenses: [docs/adr/0002-licensing.md](docs/adr/0002-licensing.md).
