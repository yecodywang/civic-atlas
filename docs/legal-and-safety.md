# Legal and safety design

This page records the risks we've considered and the rules that address them. It is a design
document, not legal advice. Project maintainers should get a lawyer's review before formal
partnerships.

## Rules

1. **Offline by construction.** The MCP server reads only the bundled YAML. It never contacts a
   government system, never submits a request, and never makes a payment. *Why:* it can't add
   load to City services, file bogus requests, or mishandle anyone's account.
2. **People do every step themselves.** Tools explain and route. Server instructions tell
   agents never to act on a user's behalf or ask for passwords, account numbers or card numbers.
   This matches the course proposal: learners do every step on their own devices, and no
   practice requests are submitted.
3. **Emergency first, in code.** `routing.py` checks every `who_to_contact` situation for
   emergency language before anything else and leads with 911. Crisis language adds 988. Every
   answer, including the fallback, carries "if anyone is in danger, call 911", because keyword
   matching will always miss some emergencies. These rules live in code with tests, so no data
   edit can weaken them. Text-to-911 depends on the local dispatch center, so it is a sourced
   data field (`emergency.text_to_911`), not an assumption.
4. **Accuracy and provenance.** Every file needs `source_urls` and `last_checked`. Entries are
   `draft` until a named person verifies them. Validation warns after 180 days. Answers and cards
   show status and sources. Corrections take priority ([CORRECTIONS.md](../CORRECTIONS.md)).
5. **No impersonation.** We never call the project official and never use government logos or
   seals. Non-affiliation notices appear in [NOTICE.md](../NOTICE.md), the README, the server
   instructions, every tool result and every printed card.
6. **Our own words.** Steps and summaries are written fresh. Facts (numbers, addresses, URLs) are
   stated with a link to their source. We don't copy page text or images.
7. **Polite link checking.** The weekly checker sends one request at a time with a pause, tries
   HEAD before GET, and uses a generic User-Agent with no personal email. Sites that block
   automated clients are reported for a human to check; they are never worked around.
8. **No telemetry and no personal data.** Nothing is collected, logged or stored.

## Risks considered

| Risk | Likelihood | Mitigation |
|---|---|---|
| Out-of-date or wrong information causes harm (a missed deadline, a wrong number) | Highest | Rules 3 and 4, the corrections policy, the warranty disclaimers in both licenses |
| The project is mistaken for an official source | Medium | Rule 5 |
| Copying official page content | Low | Rule 6 |
| Load on government websites ("accidental DDoS") | Very low | Rule 1 (the server never calls out), rule 7 |
| Agents filing bogus service requests | Low | Rules 1 and 2 |
| Privacy | Low | Rule 8 |
| Personal liability of volunteers | Low | The "AS IS" disclaimers in MIT and CC0; consider a fiscal sponsor or nonprofit home as the project grows |

## Live adapter policy (for the future)

Some day it may be useful to read live data, such as open data feeds or request status. Before
any code that contacts a government system is merged:

1. An ADR describes the use and why the static catalog isn't enough.
2. It uses only **official, documented APIs or open-data feeds**, never scraping of pages that
   block automated clients.
3. Its terms of use have been read and are followed, with a link in the ADR.
4. It caches aggressively, rate-limits itself, and identifies itself with a project User-Agent.
5. It is **read-only**. Submitting requests on someone's behalf stays out of scope.
6. It is off by default, and the offline server remains the reference implementation.
