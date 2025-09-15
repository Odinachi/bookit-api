# Booking Service API

A FastAPI booking system I built for managing service appointments with user authentication and admin controls.

## Why I Built It This Way

### Technology Choices

I went with **FastAPI** because it gives you automatic API docs and handles async operations really well. Coming from other frameworks, the type hints and automatic validation were game-changers for catching bugs early.

**MongoDB** was my database choice, and here's why that made sense:

- Booking data isn't super relational - you've got users, services, bookings, and reviews that don't need complex joins
- The async MongoDB driver (Motor) plays nicely with FastAPI's async nature
- When you're dealing with different types of services (haircuts vs dental appointments), the flexible schema helps
- Scaling horizontally is easier when you inevitably get more traffic

I structured the code using clean architecture because I've been burned by spaghetti code before:

- Models handle data validation (Pydantic does the heavy lifting)
- Repositories talk to the database
- Services contain all the business rules
- Routers just handle HTTP stuff

### Security Decisions

For authentication, I implemented JWT tokens because they're stateless and work well for APIs. Password hashing uses bcrypt because it's battle-tested. The role system is simple - just users and admins - but you could easily extend it.

## Getting This Running Locally

### What You'll Need

- Python 3.9 or newer
- Either Docker (easiest) or MongoDB installed locally
- About 10 minutes

### The Easy Way (Docker)

First, grab the code and get into the directory:

```bash
git clone <your-repo-url>
cd alt-assignment
```

Start up MongoDB with the included Docker setup:

```bash
docker-compose up -d
```

This spins up MongoDB on port 27017 and gives you a web admin interface at http://localhost:8081 (no login required).

Set up your Python environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows folks: .venv\Scripts\activate
pip install -r requirements-fixed.txt
```

Create your environment file:

```bash
cp .env .env.local
# Edit .env.local if you want to change anything
```

Fire it up:

```bash
python main.py
```

You should see it connect to MongoDB and start serving on http://localhost:8000. The interactive API docs are at http://localhost:8000/docs.

### If You Don't Want Docker

Install MongoDB however you prefer:

```bash
# Mac users
brew install mongodb/brew/mongodb-community
brew services start mongodb/brew/mongodb-community

# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongod
```

Then follow the Python setup steps above.

### Quick Test

Once it's running, you can create a test admin user:

```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Admin",
    "email": "admin@test.com",
    "password": "password123",
    "role": "admin"
  }'
```

Then head to http://localhost:8000/docs to play around with the API.

## Running Tests

I've included a comprehensive test suite that covers the core business logic without requiring a database. The tests focus on validation, authentication logic, and business rules.

### Quick Test Run

```bash
# Make the test script executable and run
chmod +x run_tests.sh
./run_tests.sh
```

### Manual Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
PYTHONPATH="$(pwd)" pytest tests/ -v

# Run specific test categories
PYTHONPATH="$(pwd)" pytest tests/test_models.py -v      # Model validation
PYTHONPATH="$(pwd)" pytest tests/test_services.py -v   # Business logic
PYTHONPATH="$(pwd)" pytest tests/test_repositories.py -v # Core algorithms
PYTHONPATH="$(pwd)" pytest tests/test_api.py -v        # Error handling
```

### What's Tested

- **Password hashing and JWT creation** - Security components work correctly
- **Booking conflict detection** - Time slot validation algorithms
- **User authorization** - Role-based access control logic
- **Input validation** - Email, price, rating validation rules
- **Error scenarios** - Edge cases and business rule violations

The tests run quickly since they don't require MongoDB or external services - perfect for development and CI/CD pipelines.

## Environment Variables

Here's what you can configure:

| Variable                      | What It Does                         | Default Value               | Must Set? |
| ----------------------------- | ------------------------------------ | --------------------------- | --------- |
| `MONGODB_URL`                 | Where to find MongoDB                | `mongodb://localhost:27017` | No        |
| `SECRET_KEY`                  | Signs your JWT tokens (CHANGE THIS!) | `your-secret-key-here...`   | **YES**   |
| `ALGORITHM`                   | JWT signing algorithm                | `HS256`                     | No        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | How long tokens last                 | `30`                        | No        |
| `DB_NAME`                     | Database name                        | `booking_service`           | No        |

### Sample Configurations

**For development (.env):**

```env
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=some-long-random-string-for-development
ACCESS_TOKEN_EXPIRE_MINUTES=60
DB_NAME=booking_dev
```

**For production (.env.production):**

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/booking_service
SECRET_KEY=super-secure-256-bit-key-generated-properly
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_NAME=booking_service
```

The secret key is crucial - it signs your JWT tokens. In production, generate a proper random key and keep it safe.
