# Auction Marketplace API

A RESTful Auction Marketplace API built with Django REST Framework.

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone <https://github.com/AcexDev/auction-marketplace.git>
cd auction

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your DJANGO_SECRET_KEY to .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### API Documentation
- Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- ReDoc: `http://127.0.0.1:8000/api/schema/redoc/`

---

## Database Design Overview

### User
- UUID primary key
- Email-based authentication (no username)
- Role field: `user` or `admin`
- Custom manager handling email-only user creation

### Auction
- UUID primary key
- Owner (ForeignKey → User)
- Winner (ForeignKey → User, nullable)
- Fields: title, description, starting_price, current_price, end_time, status
- Status choices: `active`, `completed`, `cancelled`
- `is_expired` property — computed on access, drives completion logic

### Bid
- UUID primary key
- ForeignKey to Auction and User (bidder)
- Ordered by amount descending by default
- Full bid history preserved — no deletions

---

## Authentication Approach

JWT Authentication via `djangorestframework-simplejwt`.

- **Register:** `POST /api/auth/register/`
- **Login:** `POST /api/auth/login/` → returns access + refresh tokens
- **Logout:** `POST /api/auth/logout/` → blacklists refresh token

Token lifetimes:
- Access token: 60 minutes
- Refresh token: 7 days

All protected endpoints require `Authorization: Bearer <access_token>` header.

---

## Permission Model

### Custom `IsOwnerOrAdmin` permission class:

| Action | Permission |
|---|---|
| List auctions | Any authenticated user |
| Create auction | Any authenticated user |
| View single auction | Any authenticated user |
| Update auction | Owner or Admin only |
| Delete/Cancel auction | Owner or Admin only |
| Place bid | Any authenticated user (except auction owner) |
| View bid history | Any authenticated user |
| View own bids | Authenticated user (own bids only) |

Admins have full access to all resources regardless of ownership.

---

## Auction Completion

Auction completion uses a **check-on-read** approach:
- When an auction is retrieved or listed, `is_expired` is checked
- If expired, status flips to `completed` and the highest bidder is set as winner
- If no bids exist, auction completes with no winner

A management command is also available as an admin safety net:
```bash
python manage.py close_expired_auctions
```

This catches auctions that have expired but haven't been accessed since expiry.

In production, this command would be scheduled via Celery beat to run periodically, ensuring auction statuses are always accurate regardless of traffic.

---

## Assumptions Made

- Cancelled auctions cannot be reactivated — bid history and timeline integrity would be compromised
- Auction owners cannot bid on their own listings
- `current_price` is seeded from `starting_price` on creation and only updated via valid bids
- Deleting an auction performs a soft cancel, not a hard delete — preserves bid history
- Default auction listing returns active auctions only; use `?status=` query param for filtering
- Times are stored in UTC internally; clients should send ISO 8601 format with explicit timezone offset

---

## What I Would Improve With Another Week

- **Celery beat** — replace check-on-read with a scheduled background task for real-time auction completion
- **Notifications** — email or websocket notifications to winner and auction owner on completion
- **Pagination** — add cursor-based pagination to auction and bid list endpoints
- **Rate limiting** — prevent bid spamming on active auctions
- **Filtering** — filter auctions by price range, end time, category
- **Tests** — unit and integration tests for all business logic, especially bidding rules
- **Deployment** — containerize with Docker, deploy on Render with Neon PostgreSQL
- **Refresh token rotation endpoint** — expose `/api/auth/token/refresh/` for clients to renew access tokens