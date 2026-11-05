# Security policy

## Reporting a vulnerability

Please **do not** open a public issue for a security problem. Use GitHub's private vulnerability
reporting instead: go to this repository's **Security** tab and choose **Report a vulnerability**.
Only the maintainers can see the report.

We aim to acknowledge reports within a week. This is a volunteer project, so please be patient.

## Scope

In scope:
- The `civic-atlas` Python package and its MCP server (`src/civic_atlas/`)
- The Claude Code plugin and marketplace files (`plugins/`, `.claude-plugin/`)
- GitHub Actions workflows in `.github/`
- Catalog data that could lead someone to an unsafe or fraudulent destination, such as a link that
  now points to a phishing or look-alike site

Out of scope: government websites and services themselves. Report problems with those to the
government that runs them.

## Design notes relevant to security

- The MCP server is **offline and read-only**. It reads YAML files bundled with the package. It makes
  no network requests, and it never handles credentials, payment details or personal information.
- The only network activity in this repository is the scheduled link checker
  (`civic-atlas check-links`), which sends slow, serial requests to the URLs listed in the catalog.
