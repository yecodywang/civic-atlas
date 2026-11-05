# Adding a new city, town or county

Thanks for bringing civic-atlas to a new place! A new place is welcome as soon as it has a few
well-sourced entries and someone willing to look after it.

## 1. Open an issue

Use the **New jurisdiction** issue template. Say which place it is and who will steward it, so
others don't duplicate the work.

## 2. Create the folders

Use the folder pattern from [data-model.md](data-model.md):

```bash
cp -r jurisdictions/_template jurisdictions/us/nc/place/cary
rm jurisdictions/us/nc/place/cary/services/_example-service.yaml   # after you've read it
```

Make sure every parent has a `jurisdiction.yaml`. For example, a new state needs
`jurisdictions/us/<state>/jurisdiction.yaml`, and a city's counties should exist (a stub with a
name, a website and provenance is enough) so the city can list them under `overlaps`.

## 3. Fill in `jurisdiction.yaml`

- `name`, `kind` (must match the folder: `place` under `place/`, and so on), `aliases`
- `overlaps`: the counties the place lies in, with the main one marked `primary: true`
- `key_contacts`: the general information line, police non-emergency line, utility billing, and so on
- `emergency.text_to_911`: only if you found an official source. Otherwise leave it out.
- `stewards`: your GitHub handle

## 4. Add services

Start with the most common tasks, roughly in this order: the general help line, reporting a
problem (the city's 311 or service-request system), missed trash pickup, paying the water or
utility bill, emergency alerts, property tax (often billed by the county), and finding help.
Copy the template service for each one.

## 5. Add a `routing.yaml`

Even five or six rules make `who_to_contact` useful. Always include a `fallback`, which is usually
the city's general information line.

## 6. Check and submit

```bash
uv run civic-atlas validate
uv run civic-atlas render --jurisdiction <your place>   # read the cards: do they make sense?
uv run civic-atlas serve --jurisdiction <your place>    # optional: try it with an MCP client
```

Then open a pull request.

## Outside the United States

Add your country code to `SUBDIVISION_TYPE` in `src/civic_atlas/loader.py` if its first-level
subdivision isn't called a "state" in OCD ids. Add its emergency number to `EMERGENCY_NUMBERS` in
`src/civic_atlas/routing.py`. Until you do, answers say "call your local emergency number". Both
need tests.
