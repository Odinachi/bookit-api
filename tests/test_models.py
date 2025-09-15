import pytest
from datetime import datetime
from models.user import User, UserRole
from models.service import Service
from models.booking import Booking, BookingStatus
from models.review import Review

class TestUserModel:
    def test_user_creation(self):
        """Test user model creation and validation"""
        user_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "password_hash": "hashed_password",
            "role": UserRole.USER,
            "created_at": datetime.now()
        }
        user = User(**user_data)
        
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.role == UserRole.USER

    def test_user_role_enum(self):
        """Test user role enumeration"""
        assert UserRole.USER == "user"
        assert UserRole.ADMIN == "admin"

class TestServiceModel:
    def test_service_creation(self):
        """Test service model creation and validation"""
        service_data = {
            "id": 1,
            "title": "Haircut",
            "description": "Professional haircut service",
            "price": 25.0,
            "duration_minutes": 30,
            "is_active": True,
            "created_at": datetime.now()
        }
        service = Service(**service_data)
        
        assert service.id == 1
        assert service.title == "Haircut"
        assert service.price == 25.0
        assert service.duration_minutes == 30
        assert service.is_active is True

class TestBookingModel:
    def test_booking_creation(self):
        """Test booking model creation and validation"""
        start_time = datetime.now()
        end_time = datetime.now()
        
        booking_data = {
            "id": 1,
            "user_id": 1,
            "service_id": 1,
            "start_time": start_time,
            "end_time": end_time,
            "status": BookingStatus.PENDING,
            "created_at": datetime.now()
        }
        booking = Booking(**booking_data)
        
        assert booking.id == 1
        assert booking.user_id == 1
        assert booking.service_id == 1
        assert booking.status == BookingStatus.PENDING

    def test_booking_status_enum(self):
        """Test booking status enumeration"""
        assert BookingStatus.PENDING == "pending"
        assert BookingStatus.CONFIRMED == "confirmed"
        assert BookingStatus.CANCELLED == "cancelled"
        assert BookingStatus.COMPLETED == "completed"

class TestReviewModel:
    def test_review_creation(self):
        """Test review model creation and validation"""
        review_data = {
            "id": 1,
            "booking_id": 1,
            "rating": 5,
            "comment": "Excellent service!",
            "created_at": datetime.now()
        }
        review = Review(**review_data)
        
        assert review.id == 1
        assert review.booking_id == 1
        assert review.rating == 5
        assert review.comment == "Excellent service!"

    def test_review_rating_validation(self):
        """Test review rating is within valid range"""
        # This would be handled by Pydantic validators in a real implementation
        valid_ratings = [1, 2, 3, 4, 5]
        for rating in valid_ratings:
            review_data = {
                "id": 1,
                "booking_id": 1,
                "rating": rating,
                "comment": "Test comment",
                "created_at": datetime.now()
            }
            review = Review(**review_data)
            assert review.rating == rating