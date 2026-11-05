# ADR 0003: Non-emergency services only; no emergency detection or routing

- Status: accepted (replaces the emergency-first routing described in earlier drafts)
- Date: 2026-11-05

## Context

Early versions of the server tried to spot emergencies with keyword lists ("fire", "smell gas",
"not breathing", and so on), put a "call 911" block first in answers, added 988 for crisis
language, and stored whether text-to-911 worked in each place.

In practice that approach was:

- **Unreliable both ways.** It missed plain emergencies ("my dad collapsed and won't wake up")
  and fired on routine requests ("can you help me pay my water bill" while "help me" was a
  trigger). Any list of phrases will keep failing like this.
- **The wrong layer.** The AI model talking to the person can recognize an emergency far better
  than a keyword list. A tool that only sometimes flags emergencies invites people and agents to
  rely on it.
- **A maintenance and liability burden.** It made the project look like it handled emergencies,
  which it can't do well, and it isn't what the project is for.

## Decision

civic-atlas covers **non-emergency** services only, and says so plainly.

- The server does not detect, classify or route emergencies. No tool returns emergency fields.
- The catalog contains no emergency or crisis numbers (911, 988), and `civic-atlas validate`
  rejects channels that use them.
- The scope is stated in one line (`SCOPE_NOTE` in `src/civic_atlas/catalog.py`): at the top of
  the MCP server instructions, on printed cards, and in AGENTS.md, the README, CONTRIBUTING and
  NOTICE.
- In scope: non-emergency lines (for example the police non-emergency number), utilities' service
  lines, and City or County services such as health clinics and medical or social services.

## Consequences

- The server, data and tests are simpler, with no phrase lists to keep tuning.
- The safety of emergency situations rests with the connected AI client and with people, where
  it belongs. The scope line tells both what this tool doesn't do.
- Contributors who want to add emergency handling should open an issue to revisit this ADR, not
  add it piecemeal.
