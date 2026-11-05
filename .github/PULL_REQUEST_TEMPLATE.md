## What changed

<!-- One or two sentences. Link the issue if there is one: "Fixes #12". -->

## Checklist

For catalog data changes:

- [ ] Every phone number, link, fee and rule appears on an official page listed in `provenance.source_urls`
- [ ] I checked against those sources on: <!-- YYYY-MM-DD --> and updated `last_checked`
- [ ] Summaries and steps are in my own words (nothing copied from government pages)
- [ ] `status` is honest: `draft` unless I verified every fact (then `verified_by` and `verified_on` are set)
- [ ] I did not submit any test requests to a government service

For everyone:

- [ ] `uv run civic-atlas validate` and `uv run pytest` pass
- [ ] My commits are signed off (`git commit -s`, see [DCO](../DCO))
- [ ] I didn't add emergency detection or emergency numbers (non-emergency scope, see ADR 0003)
