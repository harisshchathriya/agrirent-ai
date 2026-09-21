# API Contract / OpenAPI Summary

This document summarizes the current Review-II API surface implemented in the FastAPI backend.

The canonical API contract is generated at runtime by FastAPI and is available through Swagger UI and the OpenAPI JSON specification.

## Base URL

### Production

https://agrirent-ai-backend-yrxg.onrender.com

### Local

http://127.0.0.1:8000

---

# Authentication

## POST /auth/register

Creates a new farmer account.

### Request Body

- name
- email
- password
- phone

### Response

User profile payload.

---

## POST /auth/login

Authenticates a registered user.

### Request

OAuth2 form fields:

- username
- password

### Response

- access_token
- token_type

Authentication uses JWT bearer tokens.

---

## GET /auth/users/me

Returns the currently authenticated user's profile.

### Authentication

Bearer JWT required.

---

## POST /auth/forgot-password

Accepts an email address and always returns the same generic response, whether
or not the account exists. For a matching account, the backend creates a
single-use, time-limited password-reset token. The raw token is never returned
by the production API response.

---

## POST /auth/reset-password

Accepts a password-reset token and a new password. The token must exist, be
unused, and be within its expiry period. On success, the password is bcrypt
hashed and the token is invalidated. This endpoint does not issue a JWT.

---

# Equipment

## GET /equipment

Returns all available equipment records.

---

## POST /equipment

Creates a new equipment listing.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

The authenticated owner becomes the equipment owner.

---

## GET /equipment/{equipment_id}

Returns equipment details for the specified equipment UUID.

---

## PUT /equipment/{equipment_id}

Updates an equipment listing.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

The authenticated user must own the equipment.

---

## DELETE /equipment/{equipment_id}

Deletes an equipment listing.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

The authenticated user must own the equipment.

Equipment with blocking booking history cannot be deleted.

---

# Equipment Relationships

## GET /equipment/{equipment_id}/images

Returns images associated with the equipment.

---

## POST /equipment/{equipment_id}/images

Adds an image to an equipment listing.

### Authentication

Bearer JWT required.

### Authorization

The authenticated user must be the equipment owner.

---

## GET /equipment/{equipment_id}/reviews

Returns reviews associated with the equipment.

---

## POST /equipment/{equipment_id}/reviews

Creates a review for equipment.

### Authentication

Bearer JWT required.

### Authorization

The authenticated renter must have a completed booking for the equipment.

---

# Bookings

## POST /bookings

Creates a booking request for equipment.

### Authentication

Bearer JWT required.

### Business Rules

The request validates:

- Equipment existence
- Equipment availability
- Equipment ownership
- Start date
- End date
- Date ordering
- Booking overlap
- Own-equipment booking prevention

The total price is calculated from the equipment daily price and rental duration.

---

## GET /bookings

Returns bookings for the authenticated renter.

### Authentication

Bearer JWT required.

---

## GET /bookings/{booking_id}

Returns a booking when the authenticated user is:

- The renter, or
- The owner of the booked equipment

### Authentication

Bearer JWT required.

---

## PUT /bookings/{booking_id}/status

Updates the booking status according to the implemented renter status rules.

A renter can cancel a pending booking.

### Authentication

Bearer JWT required.

---

## DELETE /bookings/{booking_id}

Deletes a pending booking created by the authenticated renter.

### Authentication

Bearer JWT required.

---

# Owner Booking Management

## GET /bookings/owner/bookings

Returns bookings associated with equipment owned by the authenticated owner.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

---

## GET /bookings/owner/bookings/pending

Returns pending booking requests for the authenticated owner's equipment.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

---

## PUT /bookings/owner/bookings/{booking_id}/approve

Approves a pending booking.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

The authenticated user must own the equipment.

The system prevents overlapping approved bookings.

---

## PUT /bookings/owner/bookings/{booking_id}/reject

Rejects a pending booking.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

The authenticated user must own the equipment.

---

## PUT /bookings/owner/bookings/{booking_id}/complete

Completes an approved booking.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

The authenticated user must own the equipment.

---

## PUT /bookings/owner/bookings/{booking_id}/cancel

Cancels a pending or approved booking.

### Authentication

Bearer JWT required.

### Authorization

Owner role required.

The authenticated user must own the equipment.

---

# Health and Metadata

## GET /

Returns the backend service welcome response.

---

## GET /health

Confirms that the backend service is running.

---

## GET /docs

Provides the interactive Swagger UI generated by FastAPI.

---

## GET /openapi.json

Provides the machine-readable OpenAPI specification generated by FastAPI.

---

# Authentication and Authorization

The API uses JWT bearer authentication.

Supported application roles:

- FARMER
- OWNER
- ADMIN

Public registration accepts only the FARMER and OWNER roles. ADMIN accounts
cannot be created through the public registration endpoint.

Role-based authorization is applied to protected operations.

Owner-specific equipment and booking operations additionally verify ownership of the relevant equipment.

---

# Validation

Request validation is handled using Pydantic schemas.

Invalid request data is rejected by the API validation layer.

---

# Common HTTP Responses

The API may return the following HTTP status codes depending on the operation:

- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Validation Error
- 500 Internal Server Error

---

# OpenAPI Documentation

FastAPI automatically generates the API specification.

Swagger UI:

`/docs`

OpenAPI JSON:

`/openapi.json`

The generated OpenAPI specification is the canonical source for the implemented API contract.

---

# Review-II Scope

The API contract covers the implemented Review-II rental workflow:

Registration → Authentication → Equipment Management → Equipment Browsing → Booking → Owner Booking Management → Equipment Images and Reviews.

AI recommendation, SmartMatch, payment integration, maps, weather integration, notifications, and other future enhancements are outside the current Review-II API scope.
