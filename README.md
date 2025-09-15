# Booking Service API

A FastAPI-based booking and service management system with MongoDB backend.

## Features

- 🔐 **JWT Authentication** with role-based access control
- 📅 **Booking System** with conflict prevention
- ⭐ **Review System** with rating statistics
- 🛡️ **Admin Controls** for service and booking management
- 📊 **MongoDB** with async operations
- 🚀 **FastAPI** with automatic API documentation

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Start MongoDB with Docker Compose:**

   ```bash
   docker-compose up -d
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Option 2: Local MongoDB

1. **Install and start MongoDB locally**

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Update .env file** with your MongoDB connection string

4. **Run the application:**
   ```bash
   python main.py
   ```

## API Documentation

Once running, visit:

- **API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **MongoDB Admin (if using Docker):** http://localhost:8081

## API Endpoints

### Authentication

- `POST /users/register` - Register new user
- `POST /users/login` - Login and get JWT token
- `GET /users/me` - Get current user info (protected)

### Services

- `GET /services/` - List active services (public)
- `POST /services/` - Create service (admin only)
- `GET /services/search?q=query` - Search services

### Bookings

- `POST /bookings/` - Create booking (protected)
- `GET /bookings/` - Get user bookings (protected)
- `PATCH /bookings/{id}/confirm` - Confirm booking
- `PATCH /bookings/{id}/cancel` - Cancel booking

### Reviews

- `POST /reviews/` - Create review (protected)
- `GET /reviews/service/{id}` - Get service reviews
- `GET /reviews/service/{id}/stats` - Get rating statistics

## Example Usage

### 1. Register a user

```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### 2. Login and get token

```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### 3. Create a booking (with token)

```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "start_time": "2024-12-25T10:00:00"
  }'
```

## Project Structure

```
/Users/Apple/vscode_projects/alt-assignment/
├── main.py                          # FastAPI app entry point
├── database.py                      # MongoDB connection
├── docker-compose.yml              # MongoDB setup
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables
├── models/                         # Pydantic models
│   ├── user.py
│   ├── service.py
│   ├── booking.py
│   └── review.py
├── repositories/                   # Database access layer
│   ├── user_repository.py
│   ├── service_repository.py
│   ├── booking_repository.py
│   └── review_repository.py
├── services/                       # Business logic layer
│   ├── user_service.py
│   ├── service_service.py
│   ├── booking_service.py
│   ├── review_service.py
│   └── auth_service.py
└── routers/                        # API route handlers
    ├── user_router.py
    ├── service_router.py
    ├── booking_router.py
    └── review_router.py
```

## Environment Variables

Copy `.env` and update the values:

```env
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

The application will gracefully handle MongoDB connection failures and continue running with limited functionality.

**Suggested commit message:** "Fix lifespan events deprecation and add graceful MongoDB connection handling with Docker setup"
