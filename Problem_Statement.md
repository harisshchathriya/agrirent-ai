# Problem Statement

## Project Title

AgriRent AI

## Problem Statement

Small and medium-scale farmers need a simple way to find and rent agricultural equipment. Equipment owners also need a controlled way to list equipment and manage rental requests. Manual coordination creates delays, booking conflicts, and poor visibility for both sides.

## Proposed Solution

AgriRent AI is a web-based rental platform where users can register, log in, browse equipment, view equipment details, and create bookings. Equipment owners can review booking requests and update booking status through an owner panel. The platform uses JWT authentication, PostgreSQL, SQLAlchemy, and FastAPI to support the core rental workflow.

## Objectives

- Allow users to register and log in securely
- Let renters browse equipment and create bookings
- Let equipment owners manage incoming bookings
- Prevent invalid bookings such as past dates, overlapping dates, and renting own equipment
- Store users, equipment, and bookings in PostgreSQL

## Scope

### In Scope

- User registration and login
- JWT authentication
- Equipment list and equipment details
- Add equipment
- Booking creation
- My bookings
- Owner bookings
- Booking approval, rejection, completion, and cancellation
- Booking validation and error handling

### Out of Scope

- AI recommendation engine
- Google Maps integration
- Weather API
- Payment gateway
- Ratings and reviews
- Notifications
- Analytics dashboard

## Technologies Used

- Frontend: React, Vite, Tailwind CSS, Axios, React Router
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT
- Database: PostgreSQL

## Expected Outcome

The system should demonstrate a complete MVP rental flow: a user can register, log in, browse equipment, book equipment, and track bookings, while an equipment owner can approve or reject requests and manage booking status from the owner panel.

## Future Enhancements

- AI equipment recommendations
- Google Maps-based location search
- Weather API integration
- Payment gateway support
- Ratings and reviews
- Notifications
- Analytics dashboard
