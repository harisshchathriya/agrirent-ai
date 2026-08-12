# 🚜 AgriRent AI

## AI-Powered Agricultural Equipment Rental Platform

AgriRent AI is a full-stack agricultural equipment rental platform designed to connect **farmers/renters with agricultural equipment owners** through a secure and structured digital rental workflow.

The platform addresses a practical problem in agricultural equipment rental: farmers may need expensive machinery only for a limited period, while equipment owners may have machinery sitting unused. Traditional rental processes can depend heavily on phone calls, personal contacts, manual availability checking, and informal booking arrangements.

AgriRent AI brings equipment discovery, availability, booking, owner approval, and rental management into a single platform.

> **Review-I Scope:** The current implementation focuses on a functional MVP containing authentication, equipment management, booking workflows, validation, owner management, and PostgreSQL persistence. AI recommendations and external integrations are documented as future enhancements and are not represented as implemented features.

---

# 🎯 Problem Statement

Agricultural machinery such as tractors, harvesters, tillers, and other equipment can require a significant investment to purchase and maintain.

At the same time, many equipment owners may have machinery that remains unused for periods of time, while farmers may need that equipment only for a few days or weeks.

The challenge is not simply finding equipment. The larger problem is coordinating:

- Equipment discovery
- Availability
- Rental dates
- Booking requests
- Owner approval
- Rental status
- Booking conflicts
- Rental price calculation

Traditional rental processes may involve phone calls, personal contacts, local intermediaries, and manual record keeping.

This can result in:

- Difficulty finding suitable equipment
- Unclear equipment availability
- Multiple requests for the same equipment
- Overlapping rental periods
- Manual booking management
- Lack of centralized rental records
- Increased communication between renters and owners

### Proposed Solution

AgriRent AI provides a centralized platform where farmers/renters can discover and book agricultural equipment while equipment owners can manage their equipment and rental requests.

The system establishes a structured workflow:

```text
Discover Equipment
       ↓
View Equipment Details
       ↓
Check Availability
       ↓
Select Rental Dates
       ↓
Create Booking
       ↓
Owner Approval
       ↓
Rental
       ↓
Completion / Cancellation

✨ Key Features
🔐 Authentication
User registration
Secure login
JWT-based authentication
Password hashing
Protected routes
Authenticated API requests
Logout functionality
🚜 Equipment Management

Equipment owners can:

Add equipment
Update equipment
Delete equipment
Manage equipment information

Renters can:

Browse equipment
View equipment details
Check availability information
📅 Booking Management

Renters can:

Select equipment
Select rental dates
Create bookings
View their bookings
Cancel eligible bookings

Equipment owners can:

View incoming booking requests
Approve bookings
Reject bookings
Complete rentals
Cancel eligible rentals
🛡️ Booking Business Logic

The backend validates bookings before they are created.

The system prevents:

Booking one's own equipment
Past rental dates
Invalid date ranges
Booking unavailable equipment
Overlapping rental periods
Invalid booking status transitions
💰 Automatic Rental Price Calculation

Rental cost is calculated based on:

Total Rental Price
=
Daily Equipment Rate × Rental Duration

For example:

Daily Rate = ₹1,500
Rental Duration = 3 days

Total = ₹1,500 × 3
      = ₹4,500
📱 Responsive Interface

The frontend provides:

Responsive layouts
Loading states
Empty states
Error handling
Toast notifications
Reusable components
Structured navigation

<img width="1536" height="1024" alt="ChatGPT Image Aug 12, 2026, 10_08_38 AM" src="https://github.com/user-attachments/assets/6b7d6086-e439-4333-95d4-28b7be545010" />
