# Coverage: "Raleigh City Services Index" (RNC Fall 2026)

The maintainer compiled a services index from the Raleigh Neighborhood College Fall 2026 class slides
(Classes 1–6 and 9) and from raleighnc.gov and wake.gov (checked Nov 1, 2026). This page records how
each item was handled when it was ingested on **2026-11-04**. Every fact that went into the catalog was
re-checked against a live official page that day, using plain HTTP fetches and a browser for pages that
block automated clients or need JavaScript (raleighnc.gov, the Ask Raleigh portal).

Rules applied:

- **Non-emergency scope** ([ADR 0003](../adr/0003-non-emergency-scope.md)). 911, text-to-911, EMS,
  downed power lines and 911 caller tips are not in the catalog.
- **No named staff contacts.** Individual employees' names, emails and direct lines from the slides
  were left out. Department and program contacts are used instead.
- **Slide-only facts need a live source.** Items that couldn't be confirmed on an official page are
  listed under "Not ingested" below, so a volunteer can follow up.

Status key: **added** (new entry), **updated** (existing entry changed), **covered** (already
there), **not ingested** (reason given).

## 1. Front doors

| Index item | Status | Catalog entry / notes |
|---|---|---|
| Ask Raleigh | updated | `ask-raleigh`: no account needed, ticket per request, estimated delivery times, the full category list (read in the portal) |
| General City help line 919-996-3000, TDD | covered | Raleigh key contacts; routing fallback |
| Frequently called numbers | covered | Raleigh websites; used as a source throughout |
| Public records request | added | `request-public-records` (portal: raleighnc.nextrequest.com) |
| MyRaleigh Subscriptions | covered | `myraleigh-subscriptions` |
| ReadyWake Alerts | covered | `readywake-alerts` |
| RTN | updated | `watch-council-meetings`: RTN 10, 11 and 18 |
| New residents info | not ingested | Informational page, not a task. Candidate for a future "new to Raleigh" entry |
| Planning and Development Customer Service Center | added | `get-permit-help` (Permit Helpline 919-996-2500, One Exchange Plaza, 4th floor) |
| Services by address | not ingested | Couldn't confirm a specific lookup tool at raleighnc.gov/services |
| Engage Raleigh | covered | `engage-raleigh-surveys` |
| City events calendar | not ingested | Mentioned in `watch-council-meetings` notes |
| City Council | updated | `watch-council-meetings`: location, phone 919-996-3050, all-Council email |
| Council meeting video (Granicus) | covered | `watch-council-meetings` |
| Boards and commissions | updated | `serve-on-board-or-commission`. **The SeamlessDocs interest form now returns "page not found".** Each board's page says how to apply |
| Volunteer programs | added | `volunteer-raleigh` (**registration on hold as of Nov 2026**) |
| Strategic Plan | not ingested | Informational document, not a task |
| Social media | not ingested | Low value as catalog entries; handles change often |
| Council meeting schedule (slides) | not ingested | The Council page shows upcoming meetings rather than a standing schedule, and this week's evening session moved to Wednesday, Nov 4. The entry points to the calendar instead |

## 2a. Ask Raleigh request catalog

Checked in the portal with a browser on 2026-11-04. The categories match the index, except that "Dead Animals" is no longer a separate category; Dead Animal Removal is under Public Nuisance.

| Request types | Catalog entry |
|---|---|
| Potholes, Sinkholes & Pavement (30 days; collapsing road → 919-829-1911) | `report-pothole` (updated) |
| Signs and Signals (includes streetlights; 180 days), Faded Markings | `report-traffic-signal-or-sign` (added), `report-streetlight-out` (updated) |
| Transportation Improvement Request | `request-traffic-calming` (added) |
| Sidewalk Issues | `report-sidewalk-damage` (covered) |
| Dead Animal Removal (5 days) | `report-dead-animal` (added) |
| Graffiti | `report-graffiti` (covered) |
| Public Nuisance, Unsafe or Unfit Housing (60 days), Solid Waste Code Enforcement | `report-code-violation` (added) |
| Vehicles: Abandoned or Parked in Yard | `report-abandoned-vehicle` (updated) |
| Noise Complaint; Noise: Bar/Restaurant/Club | `report-noise` (updated) |
| Missed garbage, recycling, yard waste | `report-missed-collection` (covered) |
| Flooding, Drainage or Runoff; Waterway Spills & Pollution | `report-flooding-drainage` (updated) |
| Park and Greenway Service, Playgrounds, Tree Service (365 days) | `report-tree-or-park-problem` (added) |
| Permits & Planning (all four) | `get-permit-help` (added) |
| Buses, Parking Service, Bike & Scooters, Curb Damage, Downtown Services, Something in My Way, Street Debris, Street Resurfacing, Unpaved Street, Report a Crime, Request not found | Listed in `ask-raleigh` notes and categories; no separate entries yet |

## 2. By department

| Index item | Status | Catalog entry / notes |
|---|---|---|
| Curbside collection, yard waste weekly, cart rules, recycling rules | added | `curbside-collection-rules`. Live page confirms 15 bags and 5 bundles; "weekly since Sep 8, 2026" wasn't stated on the page (the City's news mentions the new weekly service) |
| Bulky, special, e-waste | updated | `schedule-bulky-item-pickup`. **Correction:** the index says bulky loads are "yard waste, recyclables, cardboard, e-waste and extra garbage". Per the City, a bulky load is household items such as furniture and mattresses, and extra bags and yard waste are a Special Load. E-waste moved to **Mondays only on Oct 26, 2026**. The City's page gives both 15 and 24 as the Special Load bag limit |
| Yard Waste Center | added | `yard-waste-center` (now cashless) |
| Raleigh Reuse | added | `curbside-collection-rules` |
| Solid Waste contact sws@raleighnc.gov | added | in `schedule-bulky-item-pickup`, `curbside-collection-rules` |
| Stormwater contact 919-996-3940 | not ingested | Not shown on the pages checked; existing flooding entry uses the street and private-property drainage lines |
| Drainage Assistance Program | added | `drainage-assistance-program` |
| Raleigh Rainwater Rewards | added | `rainwater-rewards` |
| Stormwater volunteering, flood safety | not ingested | Not checked yet |
| Raleigh Water service area, rates, social media | not ingested | Informational statistics from slides |
| Raleigh Water Self-Service, AutoPay, phone, mail, in person | covered | `pay-utility-bill`, `set-up-utility-autopay` |
| Customer care email | updated | `pay-utility-bill` |
| "Bill also covers solid waste fees" | not ingested | Not confirmed on a live page (the bulky page confirms pickup charges go on the utility bill) |
| iMAPS, Permit Portal, UDO, Open Data | added | `look-up-property-maps`, `get-permit-help` (addresses confirmed to load) |
| Current development activity, Reflecting Raleigh, rezoning timeline | not ingested | Not checked yet |
| 2026 bond referendum | not ingested | The vote was Nov 3, 2026, so it's already past |
| Transit (GoRaleigh, GoRaleigh Access) | not ingested | Good candidate for future entries |
| Budget documents and engagement | added | `follow-city-budget`. Slide dates (listening sessions, hearing June 1, 2027) aren't on the budget page yet, so they were left out |
| Finance ACFR/PAFR | not ingested | Informational documents |
| GIS and open data | added | `look-up-property-maps` |
| Emergency Communications (911), text-to-911, caller tips | not ingested | Out of scope (ADR 0003) |
| Police non-emergency 919-829-1911 | covered | Raleigh key contacts. Raleigh Fire's contact page also lists 919-996-3335; noted |
| Online crime report | added | `report-crime-online` (crc.raleighpd.org) |
| Crime Stoppers | added | `crime-stoppers-tip` (919-996-1193, p3tips.com/897). raleighcrimestoppers.org wasn't on the City page |
| Free smoke alarm installation | updated | `request-smoke-alarm`: online form, up to two alarms, no hard-wired alarms, callback within 24 hours |
| Fire education and community event requests | added | `request-fire-education-event` (14-day notice) |
| Fire hazard / fire code report, arson line | added | `report-fire-hazard` |
| Fire Marshal 919-996-6392, Fire Administration 919-996-6115 | added | `report-fire-hazard`, `request-smoke-alarm`, Raleigh key contacts |
| Fire stations as Safe Place sites | not ingested | Youth crisis service, outside the non-emergency scope |
| RecLink, support, Recreation Business Office | updated | `reclink-register-program` (RBO 919-996-4800, new non-resident fee from Dec 1, 2026) |
| Facility rentals, 14-day minimum | updated | `reserve-park-shelter` (14-day minimum confirmed in the RecLink FAQ) |
| Register in person at a staffed center | not ingested | Not stated on the RecLink FAQ checked |
| Find a park, greenways | covered | `find-park-greenway-center` |
| Dix Park, Parks newsletter, advisory board | not ingested | Not checked yet |
| Digital Inclusion (Parks) | added | `digital-help` |
| Office of Sustainability programs (Solarize / Electrify the Triangle, toolkits) | not ingested | Not found on the City's sustainability pages checked; contact is sustainable.raleigh@raleighnc.gov |
| Neighborhood Climate Action Fund | added | `neighborhood-funding` |
| Office of Strategy and Innovation (Impact Partner Grant) | not ingested | For organizations, not residents |
| Code Enforcement (8-inch grass rule) | added | `report-code-violation` |
| Home repair amounts | covered | `home-repair-programs` (income limits from the live page; slide dollar amounts not re-confirmed) |
| Homebuyer assistance $45K / $60K | added | `homebuyer-assistance`. The City's page lists two different maximum purchase prices; noted |
| Care Navigation, homelessness prevention | added | `housing-crisis-help`. The live page describes coordinated entry and service centers; "Care Navigation" wasn't named there |
| Community Engagement programs | added | `neighborhood-registry`, `raleigh-tool-share`, `neighborhood-funding`, `volunteer-raleigh`, `digital-help`. Not yet: Neighborhood College, Citizens Leadership Academy, Partnership Raleigh, Summer Youth Employment, Foster Grandparents, Raleigh Engagement Network, Community Engagement Vehicle, Neighborhood Navigators, Engage Raleigh Expo |
| Communications (Your City Answered, Locals Guide, public Wi-Fi, City View calendar) | not ingested | Not checked yet; public Wi-Fi locations would be a useful entry |
| City Manager's Office contact | not ingested | Named staff contact |

## 3. Who does what (City, County, State)

| Index item | Status | Catalog entry / notes |
|---|---|---|
| 3a emergency rows (911, EMS, downed lines) | not ingested | Out of scope |
| Fire non-emergency 919-996-6115 | added | Raleigh key contacts |
| Hydrant / water main → Raleigh Water 919-996-3245 | covered | `report-water-sewer-problem` (re-confirmed on the Report a Leak page) |
| Animal Control 919-831-6311; impounded pets → Wake County Animal Center | added | `report-animal-problem`, `wake-animal-center-lost-pets` |
| Non-emergency ambulance | not ingested | Private providers |
| Sheriff | not ingested | Source was sponsored content |
| Wake convenience centers, HHW, landfill | added | `convenience-centers`, `household-hazardous-waste`. **North Wake HHW is temporarily closed after fire damage** (Saturday collection events instead) |
| Wake County parks | added | `wake-county-parks` |
| NC State Parks | not ingested | Not checked yet |
| Property tax (City sets rate, County bills) | updated | `property-tax-bill` |
| Vehicle property tax via NC DMV | added | `vehicle-property-tax` |
| Streets: City vs NCDOT, HB620 map, NCDOT reporting | added | `report-state-road-problem`, notes in `report-pothole` |
| Street signs, signals, neighborhood traffic numbers | added | `report-traffic-signal-or-sign`, `request-traffic-calming` |
| Health and human services; Senior and Adult Services; Network of Care | added | `senior-adult-services`, `food-nutrition-services` (plus the earlier health entries) |
| Elections | added | `register-to-vote` |
| Register of Deeds | added | `birth-death-marriage-certificates` (**online ordering down until Nov 9, 2026**) |
| Schools (WCPSS, Wake Tech) | not ingested | Not checked yet; candidates for `district/` entries |
| Restaurant inspections | not ingested | Not checked yet |

## 3c–3d. Property tax and relief

| Index item | Status | Notes |
|---|---|---|
| One bill with separate City and County lines | updated | Recorded in `property-tax-bill` from the maintainer's 2026-11-01 browser check of a real bill. This resolves the index's "Remaining gaps" question |
| FY2027 rates .5371 / .3720, $20 waste fee | updated | Confirmed on Wake's Tax Rates & Fees page. **Correction:** Wake County's increase was **2 cents**, not "1.7 cents" |
| Due Sept 1; interest from Jan 6 (2%, then 0.75%/month) | updated | Confirmed with G.S. 105-360 and Wake's 2026 bills page |
| Payment fees (eCheck free, 2.3% card/wallet, $3.95 debit), mail, in person | updated | Confirmed on Wake's Payment Information page |
| Real Estate Search by address | updated | `property-tax-bill` |
| Relief programs, income limits, June 1 deadline | covered | `property-tax-relief`. **New:** late applications for good cause accepted through Dec 31, 2026 |

## 3e. Statewide and federal

| Index item | Status | Notes |
|---|---|---|
| NC 211 | covered | `nc-211` |
| NC DMV | added | `vehicle-property-tax` |
| Social Security, Medicare | not ingested | Not checked yet |
| USA.gov | covered | `us` jurisdiction website |

## 4. "Remaining gaps" from the index

| Gap | Resolution |
|---|---|
| City phone directory out of date (SeeClickFix, "Progress Energy") | Still true on 2026-11-04. Recorded in `report-streetlight-out` notes |
| Court dates and traffic tickets | Already routed to the State court system (NC Judicial Branch), not "Wake County courts" |
| Tax bill layout (separate City line?) | Resolved: the index's own 3c check shows separate lines |
| Class 10 slides | Still to compare when available |

## Time-sensitive facts to re-check soon

- SNAP: USDA told states to hold November benefit files during the federal shutdown (`food-nutrition-services`).
- Register of Deeds online ordering is down until Nov 9, 2026 (`birth-death-marriage-certificates`).
- North Wake HHW is closed after fire damage (`household-hazardous-waste`).
- Volunteer Raleigh registration is on hold (`volunteer-raleigh`).
- Late tax-relief applications are accepted through Dec 31, 2026 (`property-tax-relief`).
- RecLink's new non-resident program fee starts Dec 1, 2026 (`reclink-register-program`).
