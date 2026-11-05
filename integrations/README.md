# Integrations

civic-atlas ships one reference integration, a **local MCP server**, plus a **Claude Code plugin**
and **marketplace** that package it. This folder is the place for more ways to connect.

| Integration | Status | Where |
|---|---|---|
| MCP server (stdio), from a clone | Working | `civic-atlas serve` ([README](../README.md#quick-start)) |
| MCP server via `uvx`, no clone | Works once the repo is public | see below |
| Claude Code plugin + marketplace | Preview | [`plugins/civic-atlas/`](../plugins/civic-atlas/), [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) |
| Claude Desktop | Config snippet below (untested) | |
| VS Code, Cursor and other MCP clients | Config snippets below (untested) | |
| MCP Bundle (`.mcpb`), one-click install | Planned | `integrations/mcpb/` |
| Printable task cards / take-home guide | Working (Markdown) | `civic-atlas render` |
| Hosted HTTP server | Not planned yet (see [docs/legal-and-safety.md](../docs/legal-and-safety.md)) | |

Every integration runs the same offline, read-only server. None of them contact government
systems.

## Claude Code

From a clone (recommended while the project is young):

```bash
git clone https://github.com/yecodywang/civic-atlas.git
cd civic-atlas
uv sync
claude mcp add civic-atlas -- uv run --directory "$PWD" civic-atlas serve
```

Without a clone (fetches and caches the package):

```bash
claude mcp add civic-atlas -- uvx --from git+https://github.com/yecodywang/civic-atlas civic-atlas serve
```

As a plugin (adds the MCP server and a skill with answering guidelines):

```text
/plugin marketplace add yecodywang/civic-atlas
/plugin install civic-atlas@civic-atlas
```

## Claude Desktop

Add this to `claude_desktop_config.json` (Settings, then Developer, then Edit Config). Use the
absolute path to your clone. If Claude Desktop can't find `uv`, use its full path (`which uv`).

```json
{
  "mcpServers": {
    "civic-atlas": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/civic-atlas", "civic-atlas", "serve"]
    }
  }
}
```

## Other MCP clients

Most clients accept the same command. For example, VS Code's `.vscode/mcp.json`:

```json
{
  "servers": {
    "civic-atlas": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/civic-atlas", "civic-atlas", "serve"]
    }
  }
}
```

Cursor (`~/.cursor/mcp.json`) and many others use the `mcpServers` shape shown for Claude Desktop.

## Options

| Setting | How | Default |
|---|---|---|
| Default place for questions | `civic-atlas serve --jurisdiction <id or name>` or `CIVIC_ATLAS_DEFAULT_JURISDICTION` | `us/nc/place/raleigh` |
| Use a different catalog folder | `civic-atlas --data /path/to/jurisdictions serve` or `CIVIC_ATLAS_DATA` | data bundled with the package |

## Keeping the data fresh

The catalog is bundled with the package. A clone is as fresh as your last `git pull`. A `uvx`
or plugin install is a **snapshot** taken when it was first installed, because `uv` caches what
it built. To refresh:

```bash
git pull                                   # clone
uvx --refresh --from git+https://github.com/yecodywang/civic-atlas civic-atlas list   # uvx cache
```

For the plugin, update it from `/plugin`. Once releases exist, the plugin will pin a release
tag so updates are deliberate and reviewable.

## Adding an integration

Open an issue first, describing the client and how it would be installed. New integrations must
keep the safety rules in [docs/legal-and-safety.md](../docs/legal-and-safety.md): offline,
read-only, the emergency line in every answer, no acting on a user's behalf, no personal data.
