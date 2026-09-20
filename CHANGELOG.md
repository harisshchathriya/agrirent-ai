# Changelog

## Review-II

- Added explicit owner-role authorization for owner booking APIs and owner routes.
- Made the shared dashboard role-aware so farmers and administrators do not call owner-only endpoints.
- Prevented public registration from self-assigning owner or administrator roles.
- Restricted equipment creation to authenticated owners while preserving ownership checks for updates and deletes.
- Added backend regression coverage for role and owner-booking authorization.
- Added CI coverage enforcement and documented the deployed Vercel and Render services.
