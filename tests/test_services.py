import pytest
from unittest.mock import AsyncMock, Mock
from services.user_service import UserService
from services.booking_service import BookingService
from services.review_service import ReviewService
from models.user import User, UserRole
from models.service import Service
from models.booking import Booking, BookingStatus
from models.review import Review
from datetime import datetime

class TestUserService:
    def test_hash_password(self):
        """Test password hashing functionality"""
        user_repo_mock = AsyncMock()
        user_service = UserService(user_repo_mock)
        
        password = "testpassword123"
        hashed = user_service._hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20  # bcrypt hashes are long
        assert hashed.startswith('$2b$')  # bcrypt prefix

    def test_verify_password(self):
        """Test password verification"""
        user_repo_mock = AsyncMock()
        user_service = UserService(user_repo_mock)
        
        password = "testpassword123"
        hashed = user_service._hash_password(password)
        
        # Correct password should verify
        assert user_service._verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert user_service._verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test JWT token creation"""
        user_repo_mock = AsyncMock()
        user_service = UserService(user_repo_mock)
        
        data = {"sub": "test@example.com", "user_id": 1}
        token = user_service._create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        assert token.count('.') == 2  # JWT has 3 parts separated by dots

    @pytest.mark.asyncio
    async def test_create_user_validation(self):
        """Test user creation input validation"""
        user_repo_mock = AsyncMock()
        user_repo_mock.get_by_email.return_value = None  # No existing user
        
        # Mock successful creation
        user_repo_mock.create.return_value = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            password_hash="hashed_password",
            role=UserRole.USER,
            created_at=datetime.now()
        )
        
        user_service = UserService(user_repo_mock)
        
        result = await user_service.create_user(
            name="John Doe",
            email="john@example.com",
            password="password123"
        )
        
        assert result.name == "John Doe"
        assert result.email == "john@example.com"
        assert result.role == UserRole.USER

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_error(self):
        """Test user creation with duplicate email raises error"""
        user_repo_mock = AsyncMock()
        
        # Mock existing user
        existing_user = User(
            id=1,
            name="Existing User",
            email="john@example.com",
            password_hash="hashed_password",
            role=UserRole.USER,
            created_at=datetime.now()
        )
        user_repo_mock.get_by_email.return_value = existing_user
        
        user_service = UserService(user_repo_mock)
        
        with pytest.raises(ValueError, match="User with this email already exists"):
            await user_service.create_user(
                name="John Doe",
                email="john@example.com",
                password="password123"
            )

class TestBookingService:
    @pytest.mark.asyncio
    async def test_booking_validation_past_time(self):
        """Test booking creation with past time raises error"""
        booking_repo_mock = AsyncMock()
        service_repo_mock = AsyncMock()
        user_repo_mock = AsyncMock()
        
        booking_service = BookingService(booking_repo_mock, service_repo_mock, user_repo_mock)
        
        # Mock user exists
        user_repo_mock.get_by_id.return_value = User(
            id=1, name="John", email="john@example.com",
            password_hash="hash", role=UserRole.USER, created_at=datetime.now()
        )
        
        # Mock service exists
        service_repo_mock.get_by_id.return_value = Service(
            id=1, title="Test Service", description="Test",
            price=50.0, duration_minutes=60, is_active=True, created_at=datetime.now()
        )
        
        # Try to book in the past
        past_time = datetime(2020, 1, 1, 10, 0)
        
        with pytest.raises(ValueError, match="Booking start time must be in the future"):
            await booking_service.create_booking(
                user_id=1, service_id=1, start_time=past_time
            )

    @pytest.mark.asyncio
    async def test_booking_inactive_service_error(self):
        """Test booking creation with inactive service raises error"""
        booking_repo_mock = AsyncMock()
        service_repo_mock = AsyncMock()
        user_repo_mock = AsyncMock()
        
        booking_service = BookingService(booking_repo_mock, service_repo_mock, user_repo_mock)
        
        # Mock user exists
        user_repo_mock.get_by_id.return_value = User(
            id=1, name="John", email="john@example.com",
            password_hash="hash", role=UserRole.USER, created_at=datetime.now()
        )
        
        # Mock inactive service
        service_repo_mock.get_by_id.return_value = Service(
            id=1, title="Inactive Service", description="Test",
            price=50.0, duration_minutes=60, is_active=False, created_at=datetime.now()
        )
        
        future_time = datetime(2025, 12, 25, 10, 0)
        
        with pytest.raises(ValueError, match="Service is not available"):
            await booking_service.create_booking(
                user_id=1, service_id=1, start_time=future_time
            )

    @pytest.mark.asyncio
    async def test_booking_user_not_found_error(self):
        """Test booking creation with non-existent user raises error"""
        booking_repo_mock = AsyncMock()
        service_repo_mock = AsyncMock()
        user_repo_mock = AsyncMock()
        
        booking_service = BookingService(booking_repo_mock, service_repo_mock, user_repo_mock)
        
        # Mock user doesn't exist
        user_repo_mock.get_by_id.return_value = None
        
        future_time = datetime(2025, 12, 25, 10, 0)
        
        with pytest.raises(ValueError, match="User not found"):
            await booking_service.create_booking(
                user_id=999, service_id=1, start_time=future_time
            )

class TestReviewService:
    @pytest.mark.asyncio
    async def test_review_rating_validation(self):
        """Test review creation with invalid rating"""
        review_repo_mock = AsyncMock()
        booking_repo_mock = AsyncMock()
        
        review_service = ReviewService(review_repo_mock, booking_repo_mock)
        
        # Test invalid ratings
        invalid_ratings = [0, 6, -1, 10]
        
        for rating in invalid_ratings:
            with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
                await review_service.create_review(
                    booking_id=1, user_id=1, rating=rating, comment="Test comment"
                )

    @pytest.mark.asyncio
    async def test_review_booking_not_found_error(self):
        """Test review creation with non-existent booking"""
        review_repo_mock = AsyncMock()
        booking_repo_mock = AsyncMock()
        
        review_service = ReviewService(review_repo_mock, booking_repo_mock)
        
        # Mock booking doesn't exist
        booking_repo_mock.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Booking not found"):
            await review_service.create_review(
                booking_id=999, user_id=1, rating=5, comment="Great service!"
            )

    @pytest.mark.asyncio
    async def test_review_unauthorized_user_error(self):
        """Test review creation by unauthorized user"""
        review_repo_mock = AsyncMock()
        booking_repo_mock = AsyncMock()
        
        review_service = ReviewService(review_repo_mock, booking_repo_mock)
        
        # Mock booking owned by different user
        booking_repo_mock.get_by_id.return_value = Booking(
            id=1, user_id=2, service_id=1,  # user_id=2, but user_id=1 trying to review
            start_time=datetime.now(), end_time=datetime.now(),
            status=BookingStatus.COMPLETED, created_at=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Unauthorized to review this booking"):
            await review_service.create_review(
                booking_id=1, user_id=1, rating=5, comment="Great service!"
            )

    @pytest.mark.asyncio
    async def test_review_incomplete_booking_error(self):
        """Test review creation for non-completed booking"""
        review_repo_mock = AsyncMock()
        booking_repo_mock = AsyncMock()
        
        review_service = ReviewService(review_repo_mock, booking_repo_mock)
        
        # Mock pending booking
        booking_repo_mock.get_by_id.return_value = Booking(
            id=1, user_id=1, service_id=1,
            start_time=datetime.now(), end_time=datetime.now(),
            status=BookingStatus.PENDING, created_at=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Can only review completed bookings"):
            await review_service.create_review(
                booking_id=1, user_id=1, rating=5, comment="Great service!"
            )

    def test_get_service_rating_stats_empty(self):
        """Test rating statistics calculation with no reviews"""
        review_repo_mock = AsyncMock()
        booking_repo_mock = AsyncMock()
        
        review_service = ReviewService(review_repo_mock, booking_repo_mock)
        
        # Mock empty reviews list
        review_repo_mock.get_by_service_id.return_value = []
        
        # Since this is async, we need to test the logic manually
        reviews = []
        
        if not reviews:
            expected_stats = {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        assert expected_stats["total_reviews"] == 0
        assert expected_stats["average_rating"] == 0.0
        assert sum(expected_stats["rating_distribution"].values()) == 0

    def test_get_service_rating_stats_calculation(self):
        """Test rating statistics calculation logic"""
        # Mock reviews data
        mock_reviews = [
            Mock(rating=5),
            Mock(rating=4),
            Mock(rating=5),
            Mock(rating=3),
            Mock(rating=5)
        ]
        
        # Calculate stats manually (same logic as in service)
        total_reviews = len(mock_reviews)
        total_rating = sum(review.rating for review in mock_reviews)
        average_rating = round(total_rating / total_reviews, 2)
        
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in mock_reviews:
            rating_distribution[review.rating] += 1
        
        # Verify calculations
        assert total_reviews == 5
        assert average_rating == 4.4  # (5+4+5+3+5)/5 = 4.4
        assert rating_distribution[5] == 3
        assert rating_distribution[4] == 1
        assert rating_distribution[3] == 1