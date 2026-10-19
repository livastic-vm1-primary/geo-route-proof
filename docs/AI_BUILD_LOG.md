# AI-assisted build record — GeoRouteProof prototype (2026-10-20)

All production-impacting assertions are distinguished from unverified experimental results.

## Scope given to the coding assistant

"Build a small, auditable Python tool using official Geoapify geocoding, Places and Routing URLs to assess an AI assistant's walking-time claim. Route network travel time must override straight-line guesswork. Produce source-aware CONFIRMED_ESTIMATE / CONTRADICTED_ESTIMATE / INCONCLUSIVE decisions, with safe handling for uncertain locations and provider failures. Never output a private API key or request any customer or residential records. Supply offline reproducible tests."

The code was authored and revised with substantial AI assistance for one real beneficial owner, not claimed as independently handwritten by a specific human.

## Source-grounded findings used in code

Official Geoapify Geocoding GET /v1/geocode/search provides candidate coordinates and rank confidence. Places GET /v2/places returns GeoJSON coordinates in longitude-latitude order. Routing GET /v1/routing expects waypoints as latitude,longitude and supports mode=walk with JSON output including distance and time. Geoapify official docs were consulted on 2026-10-20.

## Design corrections / quality gates

1. **Coordinate convention:** never send GeoJSON coordinate arrays directly to routing waypoints without converting longitude,latitude to latitude,longitude.
2. **Estimated route vs straight-line:** Haversine is shown only as context and can never certify a ten-minute pedestrian route.
3. **Uncertain geocoding:** missing/low confidence results cannot be promoted to CONFIRMED_ESTIMATE, even if the mock route is short. The 0.65 threshold is a conservative design parameter, not a claim that Geoapify formally certifies routes at that cutoff.
4. **Malformed/non-finite:** NaN, infinity, boolean coordinates, missing routes, negative travel times, unexpected endpoint paths and oversize queries are rejected.
5. **Credential protection:** live requests only to the fixed official Geoapify hostname and allowlisted paths; HTTP error message details are suppressed so keys in URL parameters cannot accidentally appear in console logs.
6. **Reproducibility:** Python 3 standard library, synthetic fixtures marked as such, 13 local unit tests PASS on original VM1 at publication. Offline fixture uses invented venues.
7. **Correct reporting:** no live Geoapify location data has been retrieved, no project is selected for a grant, and neither test execution nor GitHub publication constitutes income.

## Planned after sponsor selection (NOT completed)

Use sponsor-provided or operator-authorized Geoapify API key to produce limited, source-timestamped live traces for named public landmarks. Integrate equivalent Geoapify MCP geocoding/places/routing tools in an AI client and compare semantic tool selection with the deterministic OpenAPI reference. Record genuinely observed conflicts, prompts, human operator corrections, complete code and failure logs, and publish a concise bilingual English/Korean walkthrough.

No wallet assets, gas, identities or project secrets were needed for the existing prototype.

## Official sources

- https://www.geoapify.com/open-geospatial-program/
- https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/
- https://apidocs.geoapify.com/docs/places/
- https://apidocs.geoapify.com/docs/routing/
