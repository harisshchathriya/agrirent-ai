# API Contract / OpenAPI Summary

This document summarizes the current Review-II API surface implemented in the FastAPI backend. The canonical contract is generated at runtime by FastAPI and published through Swagger UI and OpenAPI JSON.

## Base URL

- Production: https://agrirent-ai-backend-yrxg.onrender.com
- Local: http://127.0.0.1:8000

## Authentication

### POST /auth/register
- Creates a new farmer account.
- Request body: `name`, `email`, `password`, `phone`.
- Response: user profile payload.

### POST /auth/login
- Accepts OAuth2 form fields: username and password.
- Returns an access token and bearer token type.

### GET /auth/users/me
- Returns the currently authenticated user.

## Equipment

### GET /equipment
- Returns all equipment records.

### POST /equipment
- Requires owner role.
- Creates equipment for the authenticated owner.

### GET /equipment/{equipment_id}
- Returns equipment details by UUID.

### PUT /equipment/{equipment_id}
- Requires owner role and ownership match.
- Updates owned equipment.

### DELETE /equipment/{equipment_id}
- Requires owner role and ownership match.
- Removes owned equipment if no blocking booking history exists.

## Equipment Relationships

### GET /equipment/{equipment_id}/images
- Lists equipment images.

### POST /equipment/{equipment_id}/images
- Requires owner role for the equipment owner.
- Adds an equipment image.

### GET /equipment/{equipment_id}/reviews
- Lists equipment reviews.

### POST /equipment/{equipment_id}/reviews
- Requires an authenticated renter with a completed booking.
- Creates a review for the equipment.

## Bookings

### POST /bookings
- Creates a booking request for equipment.
- Validates equipment ownership, availability, dates, and overlap rules.

### GET /bookings
- Lists all bookings for the authenticated renter.

### GET /bookings/{booking_id}
- Returns a booking if the current user is the renter or the equipment owner.

### PUT /bookings/{booking_id}/status
- Allows the renter to cancel a pending booking only.

### DELETE /bookings/{booking_id}
- Removes a pending booking created by the renter.

### GET /bookings/owner/bookings
- Returns all bookings for equipment owned by the current user.

### GET /bookings/owner/bookings/pending
- Returns pending owner bookings for the current owner.

### PUT /bookings/owner/bookings/{booking_id}/approve
- Requires owner role and ownership of the equipment.
- Approves a pending booking if no overlapping approved booking exists.

### PUT /bookings/owner/bookings/{booking_id}/reject
- Requires owner role and ownership of the equipment.
- Rejects a pending booking.

### PUT /bookings/owner/bookings/{booking_id}/complete
- Requires owner role and ownership of the equipment.
- Completes an approved booking.

### PUT /bookings/owner/bookings/{booking_id}/cancel
- Requires owner role and ownership of the equipment.
- Cancels a pending or approved booking.

## Admin

### GET /admin/overview
- Requires admin role.
- Returns counts for farmers, owners, admins, and booking totals.

### GET /admin/users
- Requires admin role.
- Lists users with optional search and role filtering.

### GET /admin/equipment
- Requires admin role.
- Lists equipment with optional search and availability filtering.

### GET /admin/bookings
- Requires admin role.
- Lists booking records with optional status and search filtering.

## Health and Metadata

### GET /
- Returns the service welcome message.

### GET /health
- Confirms the backend process is running.

### GET /docs
- Swagger UI UI for interactive API exploration.

### GET /openapi.json
- Machine-readable OpenAPI schema for the current FastAPI app.
