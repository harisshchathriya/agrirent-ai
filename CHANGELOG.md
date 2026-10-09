# Changelog

## Review-III

- Added authenticated `GET /ai/recommendations` for farmer-only equipment recommendations using booking history, with historical popularity fallback.
- Made recommendation flags reflect whether personal or overall booking history positively scores available candidates; unmatched history now produces neutral recommendations with a no-match explanation.
- Added authenticated `GET /ai/demand-trends` with continuous monthly category history and a guarded three-month moving-average forecast when six observed months are available.
- Added a three-origin chronological MAE comparison against a last-month naive baseline; the current local history is too sparse to produce real evaluation metrics or a forecast.
- Added the AI recommendation and demand services, response schemas, and frontend integration through `frontend/src/services/aiService.js`.
- Reused existing booking and equipment data without changing the database schema.
- Made equipment image URLs optional on create/update, preserving omitted images and rendering a shared placeholder for missing or failed images; no migration was required.
- Added owner equipment editing with image preview and explicit image removal.
- Added demand forecast and optional image regression coverage.
- Initial pre-merge read-only production smoke check (2026-10-09) returned 200 for `/health`, `/docs`, `/openapi.json`, the frontend, and equipment reads; the then-deployed OpenAPI omitted the AI routes and both AI URLs returned 404. This records the state before the Review-III deployment.
- Post-merge verification confirmed the deployed OpenAPI lists both AI routes; fresh unauthenticated requests returned 401, while earlier authorized production requests returned 200. GitHub Actions passed on merged main commit `8779368`. The previously observed demand-trends response had one month of history and insufficient data for a defensible forecast.

## Review-II

- Added farmer/owner selection during public registration and blocked administrator self-registration.
- Added a secure, time-limited, single-use password-reset flow with development/demo-only reset URL logging.
- Added explicit owner-role authorization for owner booking APIs and owner routes.
- Made the shared dashboard role-aware so farmers and administrators do not call owner-only endpoints.
- Prevented public registration from self-assigning owner or administrator roles.
- Restricted equipment creation to authenticated owners while preserving ownership checks for updates and deletes.
- Added backend regression coverage for role and owner-booking authorization.
- Added CI coverage enforcement and documented the deployed Vercel and Render services.
