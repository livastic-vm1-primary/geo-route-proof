# GeoRouteProof: source-grounded walking-claim checker

AI-assisted, standard-library-only Python prototype for the Geoapify Open Geospatial Program Batch 2. It is built by ONE South Korea-based economic owner under the public project label PaperPilot Tools. The project is NOT yet selected for any grant, no real sponsor contract exists, and grant earnings currently equal zero.

## What a real buyer or reviewer can test

AI agents often claim a cafe or other public amenity is "within a 10-minute walk" using only the great-circle distance and a guessed origin. GeoRouteProof explicitly separates a Geoapify Geocoding match with confidence, a public Places category/radius search, and a real Geoapify pedestrian Routing estimate, then returns CONFIRMED_ESTIMATE, CONTRADICTED_ESTIMATE or INCONCLUSIVE with evidence for each venue. It does not promise actual accessibility, opening hours, or a live journey.

## Run instantly without a key, account or internet

python3 route_reality.py --demo

python3 -m unittest discover -s tests -v

The bundled fixture uses entirely SYNTHETIC provider-shaped data. These are tests for the program logic, not claims about real Seoul landmarks, walking routes, or live Geoapify uptime. The demo cannot demonstrate a paid service sale.

## Run against actual Geoapify APIs using your own authorized key

Set GEOAPIFY_API_KEY privately in your environment, then:

python3 route_reality.py --origin "Seoul Station, Seoul, South Korea" --category catering.cafe --minutes 10 --limit 3 --radius 1200

The real script requests only three official HTTPS Geoapify endpoints:
- Geocoding GET /v1/geocode/search?text=...&format=json&limit=3
- Places GET /v2/places?categories=...&filter=circle:lon,lat,radius&bias=proximity:lon,lat&limit=...
- Routing GET /v1/routing?waypoints=lat,lon|lat,lon&mode=walk&format=json

At most 2 + 6 HTTP GET calls with a 12-second timeout each. It never pays, signs a crypto transfer, discloses a public key, scans personal addresses, or sends data to another server. It does not print private API keys in errors or output. It refuses invalid coordinate ranges, unrecognized category syntax, ambiguous origins, malformed routes and impossible timings.

## Why the API ordering is important

Geoapify Places GeoJSON coordinates are [longitude, latitude], while Routing waypoints use latitude,longitude. An AI code generator can easily transpose these fields, making an invented walkability claim sound precise. Tests cover these boundary cases. Straight-line distances are advisory, not evidence of a usable walking path.

## Proposed Batch 2 completion after written sponsor selection

- Add an independently testable Geoapify MCP comparison to the same geospatial question and document the source of any disagreement.
- Record three real, authorized Geoapify API runs against public landmark locations in Seoul, Paris and San Francisco without collecting private residential addresses; redact credentials and use controlled call counts.
- Write the bilingual English/Korean tutorial about agent hallucinations, source confidence and lat/lon field ordering.
- Keep prompt/instruction transcript excerpts and AI-assisted development disclosure, provider error/fix log and realistic pricing/call-budget discussion.
- Add executable live-vs-offline integration fixtures and contributor feedback on Geoapify API and MCP tool documentation. Do not claim any of those future steps are already complete.

## References

Official docs: https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/
Official Places: https://apidocs.geoapify.com/docs/places/
Official Routing: https://apidocs.geoapify.com/docs/routing/
Program: https://www.geoapify.com/open-geospatial-program/

MIT for the author-written Python code. Upstream provider, model, OpenStreetMap and external data rights remain with their owners. No funding or payment has been accepted as of October 20, 2026.

## AI-assisted design and testing record

The public [AI-assisted build log](docs/AI_BUILD_LOG.md) records the original scope, actual source checks, conservative corrections, 13/13 offline tests and explicitly uncompleted sponsor-key/MCP/live-data work. There is no grant award or buyer contract yet.

## Working interactive preview (explicitly fictional)

**[Open the published GeoRouteProof demo](https://livastic-vm1-primary.github.io/geo-route-proof/)** — a genuinely deployed GitHub Pages build on the original author's repository. The preview is self-contained and uses only the **SYNTHETIC** JSON in `docs/demo-input.json`. It is not a Geoapify API result, does not know your location, and never asks for or embeds a live API key.

The browser displays the same default outcomes as the original Python fixture: Fictional Cafe A CONFIRMED_ESTIMATE (470 seconds), Fictional Cafe B CONTRADICTED_ESTIMATE (800 seconds), and Fictional Cafe C INCONCLUSIVE (no valid walk route) at 10 minutes. Change the budget to 4 or 14 minutes, or simulate low origin confidence 0.40; a low-confidence origin always makes all three inconclusive.

    node --test tests/demo.test.mjs
    python3 -B -m unittest discover -s tests -v

**Verification actually performed:** Python tests 13/13 PASS, JavaScript classifier tests 10/10 PASS, HTML safe text-only DOM rendering checks PASS, source code committed/pushed, GitHub Pages built, live homepage and local fixture HTTP200. A real Chrome browser on VM1 showed the 1/1/1 original result, low-confidence 0/0/3, and reset 1/1/1. Neither original Geoapify API key calls nor project selection, awarded sponsorship or real funds have been claimed.

Actual live geospatial analysis still uses `route_reality.py` and requires the owner's separate legitimate `GEOAPIFY_API_KEY`. Geoapify's selected-project extended key will only be provided if the original one-owner application is genuinely selected. The application is pending; this preview is supporting public evidence only.

## Geoapify pedestrian routing sanity gates (peer-reviewed, 2026-10-20)

Independent VM5 QA of this original VM1 project found three synthetic negative cases which the initial implementation accepted as a short walk: a 20 m route to a venue more than 300 m away in straight-line geodesic distance, a 550 m walk reported in 2 seconds, and a nontrivial 550 m walk reported in zero seconds. The original code would mark all three as confirmed estimates if the reported time met the budget.

The revised original Python `route_reality.py` and local browser-only `docs/demo-model.mjs` now reject physically inconsistent routes as `INCONCLUSIVE`, with the independent source-distance lower bound allowing the greater of 15 m or 3% geodesic rounding tolerance and a conservative 3 m/s upper sanity limit for pedestrian walking. These thresholds are **heuristic conservative plausibility checks**, not a certification of geospatial truth, accessibility or the human's walking speed. The normal synthetic fixtures are unchanged.

VM5 originally reproduced the three RED cases on old source and delivered a no-secret, four-file guarded patch through fleet coordination; VM1 reviewed and applied only that patch in the original source checkout and reran **18/18 Python plus 14/14 JavaScript tests PASS**, including every original 13+10 regression. This was an offline correctness fix, NOT an actual paid milestone, selection or public release of private real provider response. The original API key, real Seoul provider output and confidential workflow data remain VM1-private; no account changes or money were needed.
