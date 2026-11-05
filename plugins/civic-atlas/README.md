# civic-atlas plugin for Claude Code (preview)

This plugin connects Claude Code to the civic-atlas catalog, an independent, volunteer-maintained
guide to local government services. It starts with Raleigh, NC, Wake County and North Carolina.
It adds:

- **An MCP server** (`civic-atlas serve`, installed with `uvx`) with read-only tools:
  `who_to_contact`, `search_services`, `get_service`, `get_key_contacts`, `list_jurisdictions`.
- **A skill** (`city-services`) with guidelines for answering residents: name who provides each
  service, cite official sources, and never act on the person's behalf.

Non-emergency services only: civic-atlas does not detect or route emergencies.

## Install

```text
/plugin marketplace add yecodywang/civic-atlas
/plugin install civic-atlas@civic-atlas
```

It needs [uv](https://docs.astral.sh/uv/). The first run downloads the package. See
[integrations/README.md](../../integrations/README.md) for other ways to connect, and for how to
refresh the data.

Not affiliated with or endorsed by any government. See [NOTICE.md](../../NOTICE.md).
