# AGENTS.md (catalog data)

**Non-emergency services only.** Don't add emergency or crisis numbers (911, 988), emergency
detection, or "call 911" guidance to any entry, routing rule or key contact. The validator rejects
them. City or County health clinics, medical and social services, utility service lines and
police non-emergency lines are in scope. See
[../docs/adr/0003-non-emergency-scope.md](../docs/adr/0003-non-emergency-scope.md).

Before editing data, read [../CONTRIBUTING.md](../CONTRIBUTING.md#ground-rules-for-catalog-data):
every fact needs an official source in `provenance.source_urls`, new entries are `draft`, and
steps are written in your own words. Run `uv run civic-atlas validate` afterwards.
