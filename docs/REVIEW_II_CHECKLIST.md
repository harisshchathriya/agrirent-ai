# AgriRent AI - Review-II Readiness Checklist

**Branch:** `review-ii`

## Functionality

| Requirement | Status | Evidence |
|---|---|---|
| Registration and login | Complete | JWT auth routes and service tests |
| Equipment list and details | Complete | Public equipment API and frontend pages |
| Add equipment | Complete | Owner-only API and protected frontend route |
| Booking creation | Complete | Validation for ownership, dates, availability, and overlap |
| My bookings | Complete | Authenticated renter-scoped endpoint and page |
| Owner bookings | Complete | Owner-role and equipment-ownership checks |
| Approval, rejection, completion, cancellation | Complete | Owner routes, service logic, and API tests |
| PostgreSQL persistence | Complete | SQLAlchemy models and deployment configuration |

The current Problem Statement scope excludes AI recommendations, maps, weather,
payments, ratings/reviews, notifications, and analytics.

## Role-Based Access

| Role | Dashboard | Equipment | My Bookings | Owner Panel | Owner APIs |
|---|---|---|---|---|---|
| Farmer | Allowed | Browse allowed; creation forbidden | Allowed | Redirected | Forbidden |
| Owner | Allowed | Browse and creation allowed; own resources managed | Allowed | Allowed | Allowed for owned resources |
| Admin | Allowed | Existing general access preserved | Allowed | Redirected | Forbidden unless explicitly changed |

Public registration creates farmers only. Owner and administrator accounts must be
provisioned through a trusted database or administrative process.

## Security

- Passwords are bcrypt-hashed and never returned in API responses.
- JWT authentication uses `SECRET_KEY` from the environment.
- Owner booking routes require authentication, the owner role, and resource ownership.
- CORS is configured from `FRONTEND_URL`; production must use the deployed Vercel origin.
- Local `.env` files are ignored and are not tracked.

## Testing

Latest local result:

```text
76 passed, 1 warning
Coverage: 85% overall; booking service: 86%
```

GitHub Actions runs backend tests with a 40% coverage floor, then runs frontend lint
and production build validation.

## Deployment

- Frontend: https://agrirent-ai-teal.vercel.app
- Backend: https://agrirent-ai-backend-yrxg.onrender.com
- Swagger: https://agrirent-ai-backend-yrxg.onrender.com/docs
- OpenAPI: https://agrirent-ai-backend-yrxg.onrender.com/openapi.json
- Health: https://agrirent-ai-backend-yrxg.onrender.com/health

Required deployment variables are `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`,
`ACCESS_TOKEN_EXPIRE_MINUTES`, `FRONTEND_URL`, and frontend `VITE_API_URL`.

## Documentation Artifacts

- `docs/diagrams/System_Architecture.drawio`
- `docs/diagrams/ER_Diagram.drawio`
- `docs/diagrams/Module_Diagram.drawio`
- `docs/diagrams/Class_Diagram.drawio`
- FastAPI OpenAPI contract at `/openapi.json`

## Remaining Verification

- Production smoke tests require valid deployed credentials and must be performed
  manually without storing tokens or passwords in the repository.
- Browser console and responsive checks require a running frontend and backend.
