# Testing Guide

## Overview

This project includes basic unit tests covering core functionality:

- **Model Tests**: Pydantic model validation and business logic
- **Service Tests**: Business logic with mocked dependencies
- **Logic Tests**: Core algorithms and validation rules
- **Error Handling**: Edge cases and error scenarios

## Quick Start

```bash
# Make test script executable
chmod +x run_tests.sh

# Run all tests
./run_tests.sh
```

## Manual Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Set Python path and run tests
PYTHONPATH="$(pwd)" pytest tests/ -v

# Run specific test files
PYTHONPATH="$(pwd)" pytest tests/test_models.py -v
PYTHONPATH="$(pwd)" pytest tests/test_services.py -v
PYTHONPATH="$(pwd)" pytest tests/test_repositories.py -v
PYTHONPATH="$(pwd)" pytest tests/test_api.py -v
```

## Alternative Method

If you're having import issues, run from the project root:

```bash
# From project root directory
python -m pytest tests/ -v
python -m pytest tests/test_services.py -v
```

## Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_models.py       # Pydantic model validation tests
├── test_services.py     # Service layer unit tests with mocks
├── test_repositories.py # Business logic and validation tests
└── test_api.py         # Core algorithm and error handling tests
```

## What's Tested

### Model Validation

- User, Service, Booking, Review model creation
- Enum validation (UserRole, BookingStatus)
- Data type validation

### Service Logic (with mocks)

- Password hashing and verification
- JWT token creation and validation
- User creation with duplicate email prevention
- Booking time validation (no past bookings)
- Booking conflict detection logic
- Review authorization and rating validation

### Business Rules

- Booking time calculations
- Conflict detection algorithms
- Authorization logic (user vs admin)
- Input validation (email, price, rating)

### Error Scenarios

- Invalid inputs and edge cases
- Unauthorized access attempts
- Business rule violations
- Data validation failures

## Coverage

After running tests, view the coverage report:

```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Key Features

- **No Database Dependencies**: All tests run without MongoDB
- **Mocked External Dependencies**: Services tested in isolation
- **Business Logic Focus**: Tests core algorithms and validation
- **Error Handling**: Comprehensive edge case coverage
- **Fast Execution**: No I/O operations, quick feedback

## Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_models.py       # Unit tests for Pydantic models
├── test_services.py     # Service layer tests with mocks
├── test_repositories.py # Database integration tests
└── test_api.py         # API endpoint tests
```

## Test Database

Tests use a separate MongoDB database (`booking_service_test`) that is automatically:

- Created before tests run
- Cleaned between individual tests
- Dropped after all tests complete

## Coverage

After running tests, view the coverage report:

```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Key Test Features

- **Async Testing**: All tests support async/await
- **Database Isolation**: Each test gets a clean database
- **JWT Authentication**: Tests include token-based auth
- **Conflict Testing**: Booking conflicts and 409 responses
- **Role-Based Access**: Admin vs user permission testing
- **Error Scenarios**: Invalid inputs and edge cases
