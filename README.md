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
