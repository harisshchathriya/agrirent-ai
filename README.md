# AgriRent AI

Agricultural Equipment Rental Platform

## Project Overview

AgriRent AI is a full-stack rental platform for agricultural equipment. Farmers can browse equipment, request bookings, and manage their own rentals, while owners can list equipment, approve booking requests, and manage their inventory. The application also includes an admin role for platform oversight and a secure JWT-based authentication flow.

This repository is aligned to Review-II: the product scope is the working rental workflow, role-based access control, persistence, validation, and deployment readiness rather than later AI or enhancement features. Administrator accounts remain backend-controlled.

## Problem Statement

The core problem is to reduce the friction between equipment owners and farmers who need short-term access to agricultural machinery. The application connects both parties through a transparent booking workflow, enforces ownership rules, and provides a role-aware dashboard for operations.

## Features

- Farmer and owner public registration with role-aware screens and permissions; admin is backend-controlled
- JWT authentication, bcrypt password hashing, and secure password-reset tokens
- Equipment listing, detail view, and ownership-restricted create/update/delete flows
- Booking creation and lifecycle management
- Validation for past-date, invalid-range, overlap, and ownership rules
- Owner-only booking approval, rejection, completion, and cancellation actions
- PostgreSQL persistence via SQLAlchemy ORM
- Pydantic request validation and safe CORS configuration
- Health endpoint and basic backend logging

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- Axios
- React Router

### Backend

- FastAPI
- SQLAlchemy ORM
- Pydantic
- PostgreSQL
- JWT / bcrypt

### Architecture

The application follows a simple three-tier design:

- Frontend: React app serving role-based pages and API calls
- Backend: FastAPI application with routers, services, and validation logic
- Database: PostgreSQL for users, equipment, bookings, images, and reviews

## Roles and Permissions

| Role | Access |
| --- | --- |
| Farmer | Browse equipment, create bookings, view own bookings |
| Owner | Manage own equipment, view owner bookings, approve/reject/complete/cancel bookings for their equipment |
| Admin | Backend-controlled role; not available through public registration |

Authorization is enforced on the backend and not only in the UI.

## Database / ER Information

The Review-II database uses PostgreSQL and includes the core application entities:

- Users
- Equipment
- Bookings
- Equipment Images
- Reviews

This structure matches the current ORM models and the ER design artifact in the docs directory.

Password reset tokens are stored separately in an authentication-only table; they do not change the rental-domain entities.

## API Documentation

- Swagger UI: https://agrirent-ai-backend-yrxg.onrender.com/docs
- OpenAPI JSON: https://agrirent-ai-backend-yrxg.onrender.com/openapi.json
- Health check: https://agrirent-ai-backend-yrxg.onrender.com/health

The API exposes the current Review-II flow for authentication, equipment management, booking workflows, and equipment relations.

Public registration requires a Farmer or Owner selection. The login screen also
provides a password-reset flow: reset tokens are time-limited, stored only as
hashes, and are invalidated after use. In development or demo environments, set
`APP_ENV=development` or `APP_ENV=demo` to log the generated reset URL; production
responses never expose the raw token.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/harisshchathriya/agrirent-ai.git
cd agrirent-ai
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python -m app.database.init_db
uvicorn app.main:app --reload
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a local backend environment file from the project template and keep real secrets out of git-tracked files.

```bash
cp .env.example .env
```

Required backend variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` (optional; defaults to 30)
- `FRONTEND_URL`
- `APP_ENV` (set to `development` or `demo` only when reset URLs may be logged)

Frontend runtime configuration:

- `VITE_API_URL`

## Running Backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Running Frontend

```bash
cd frontend
npm run dev
```

## Testing

```bash
cd backend
python -m pytest -v --cov=app --cov-report=term-missing --cov-fail-under=40

cd ../frontend
npm run lint
npm run build
```

## CI/CD

GitHub Actions validates the project on pushes to `main` and pull requests targeting `main`.

The workflow installs backend dependencies, runs the backend test suite with coverage enforcement, installs frontend dependencies, runs ESLint, and builds the frontend. Deployment is triggered through the existing Render and Vercel repository integrations after success on the main branch.

## Deployment

The project uses:

- Render for the FastAPI API backend
- Vercel for the frontend
- Cloud PostgreSQL for persistence

Configured production links:

- Frontend: https://agrirent-ai-teal.vercel.app
- Backend: https://agrirent-ai-backend-yrxg.onrender.com

The backend must receive `DATABASE_URL` and `SECRET_KEY` from the deployment environment, and the frontend build must include the production `VITE_API_URL` before deployment.

## Live Demo URLs

- Frontend: https://agrirent-ai-teal.vercel.app
- Backend: https://agrirent-ai-backend-yrxg.onrender.com
- Swagger: https://agrirent-ai-backend-yrxg.onrender.com/docs

## Security Notes

- JWT tokens are used for authenticated API access.
- Passwords are hashed with bcrypt.
- Sensitive values are stored in environment variables, not committed to the repository.
- CORS is limited to the configured frontend origin and credentials remain enabled for the auth flow.
- Public registration cannot create administrator accounts.
- Password-reset tokens are generated securely, stored as hashes, expire, and are single-use.

## Out-of-Scope Items / Limitations

The current Review-II scope intentionally excludes AI recommendation enhancements, automated parsing features, price-insight analysis, and any later SmartMatch functionality.

## System Architecture

![System Architecture](docs/diagrams/System_Architecture.png)

## Database ER Diagram

![ER Diagram](docs/diagrams/ER_Diagram.svg)

## Module Diagram

![Module Diagram](docs/diagrams/Module_Diagram.png)

## Class Diagram

![Class Diagram](docs/diagrams/Class_Diagram.png)

## Application Screenshots

### Login

![Login](docs/screenshots/login.png)

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

### Equipment List

![Equipment List](docs/screenshots/equipment-list.png)

### Equipment Details

![Equipment Details](docs/screenshots/equipment-details.png)

### Book Equipment

![Book Equipment](docs/screenshots/booking.png)

### My Bookings

![My Bookings](docs/screenshots/my-bookings.png)

### Owner Panel

![Owner Panel](docs/screenshots/owner-panel.png)

## Local Setup

Before starting the backend, ensure PostgreSQL is running and create a database named `agrirent_ai` (or use a different database name in `DATABASE_URL`).

### 1. Clone the Repository

```bash
git clone https://github.com/harisshchathriya/agrirent-ai.git
cd agrirent-ai
```

### 2. Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Create the backend environment file from the repository template.
# Windows PowerShell
Copy-Item ..\.env.example .env

# Linux/macOS
cp ../.env.example .env

pip install -r requirements.txt
# Create any missing database tables.
python -m app.database.init_db
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

### 4. Environment Notes

The backend requires:

- A valid PostgreSQL database connection in `.env`
- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `FRONTEND_URL` (defaults to `http://localhost:5173` for local development)

The frontend reads its API base URL from `VITE_API_URL`. For local development, copy
`frontend/.env.example` to `frontend/.env` or use the built-in local fallback.

## API Documentation

- Swagger UI: https://agrirent-ai-backend-yrxg.onrender.com/docs
- OpenAPI JSON: https://agrirent-ai-backend-yrxg.onrender.com/openapi.json
- Health check: https://agrirent-ai-backend-yrxg.onrender.com/health

## Deployment

The Review-II deployment uses Vercel for the frontend, Render for the FastAPI
backend, and Render PostgreSQL for persistence.

- Frontend: https://agrirent-ai-teal.vercel.app
- Backend: https://agrirent-ai-backend-yrxg.onrender.com

Configure these backend environment variables in the hosting platform; never commit
their real values:

- `DATABASE_URL` — cloud PostgreSQL SQLAlchemy connection string
- `SECRET_KEY` — long random JWT signing secret
- `ALGORITHM` — JWT algorithm (currently `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` — JWT lifetime in minutes
- `FRONTEND_URL` — `https://agrirent-ai-teal.vercel.app`

Configure `VITE_API_URL` in the frontend hosting platform as
`https://agrirent-ai-backend-yrxg.onrender.com`. Vite embeds this build-time value in
the frontend bundle, so it must be set before each production build.

The backend exposes `GET /health` for platform health checks. Start the backend from
the `backend` directory with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

On Windows PowerShell, set the port first (for example,
`$env:PORT=8000`) and run `uvicorn app.main:app --host 0.0.0.0 --port $env:PORT`.
The database tables are initialized manually with `python -m app.database.init_db`;
the deployed service must receive its cloud `DATABASE_URL` before that command runs.

## Continuous Integration

GitHub Actions runs validation on pushes to `main` and on pull requests targeting `main`.
The backend job runs the pytest suite with coverage enforcement, while the frontend job
installs dependencies with `npm ci`, runs ESLint, and creates a production build with
Vite. Any test, coverage, lint, or build failure returns a non-zero exit code and fails
the workflow.

Run the same checks locally before opening a pull request:

```bash
cd backend
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=40

cd ../frontend
npm run lint
npm run build
npm ci
npm run lint
npm run build
```

## Scope and Future Enhancements

The current MVP scope is registration, login, JWT authentication, equipment browsing
and creation, booking creation, renter bookings, owner booking management, validation,
and PostgreSQL persistence. Notifications, payments, maps, weather,
AI recommendations, and analytics are outside the current Problem Statement scope.

- AI equipment recommendation
- Google Maps integration
- Weather API
- Payment gateway
- Ratings and reviews
- Real-time notifications
- Analytics dashboard

## Author

Harissh Chathriya

B.Tech Artificial Intelligence and Data Science

J.J. College of Engineering and Technology

## License

This project is developed for academic and educational purposes.
