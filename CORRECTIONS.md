# Corrections policy

Accuracy is the most important thing this project offers. A wrong phone number or an outdated
step can cost someone time, money or a missed deadline, so corrections take priority over all other
work.

## How to report something wrong

1. Open an issue using the **Report inaccurate info** template. Include the entry (or a link to it),
   what's wrong, and a link to the official page that shows the correct information.
2. Or open a pull request that fixes the entry directly. See [CONTRIBUTING.md](CONTRIBUTING.md).
   Update `provenance.source_urls` and `provenance.last_checked` in the same change.

You don't need a GitHub account to tell us something is wrong. Anyone with an account can open an
issue on your behalf, and the take-home guides point readers here.

## What happens next

| Situation | Target response |
|---|---|
| Wrong emergency, safety or phone information | Fix or remove the entry as soon as a maintainer sees it |
| Wrong instructions, link or eligibility details | Fix within a few days, or mark `needs-review` right away |
| Report from government staff about their own service | Treated as a strong source; fixed on the same priority as above |
| Disagreement about wording or scope | Discussed in the issue |

When we can't confirm a report quickly, we set the entry's `provenance.status` to `needs-review`.
The MCP server and printed task cards then show that the entry may be out of date.

## For government staff

You never need permission from us to point out an error in a description of your own service. If
you'd rather we stop describing a service, or describe it differently, open an issue and explain why.
We'll work with you. See also [docs/contributing-as-government-staff.md](docs/contributing-as-government-staff.md).
