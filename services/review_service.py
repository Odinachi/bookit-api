from repositories.review_repository import ReviewRepository
from repositories.booking_repository import BookingRepository
from models.review import Review
from models.booking import BookingStatus
from typing import List, Optional
from datetime import datetime

class ReviewService:
    def __init__(self, review_repo: ReviewRepository, booking_repo: BookingRepository):
        self.review_repo = review_repo
        self.booking_repo = booking_repo
    
    async def create_review(self, booking_id: int, user_id: int, rating: int, comment: str) -> Review:
        """Create a new review for a completed booking"""
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Get booking and validate
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        # Check authorization
        if booking.user_id != user_id:
            raise ValueError("Unauthorized to review this booking")
        
        # Check if booking is completed
        if booking.status != BookingStatus.COMPLETED:
            raise ValueError("Can only review completed bookings")
        
        # Check if review already exists
        existing_review = await self.review_repo.get_by_booking_id(booking_id)
        if existing_review:
            raise ValueError("Review already exists for this booking")
        
        review_data = {
            "booking_id": booking_id,
            "rating": rating,
            "comment": comment.strip()
        }
        
        return await self.review_repo.create(review_data)
    
    async def get_review_by_id(self, review_id: int) -> Optional[Review]:
        """Get review by ID"""
        return await self.review_repo.get_by_id(review_id)
    
    async def get_review_by_booking_id(self, booking_id: int) -> Optional[Review]:
        """Get review by booking ID"""
        return await self.review_repo.get_by_booking_id(booking_id)
    
    async def get_service_reviews(self, service_id: int) -> List[Review]:
        """Get all reviews for a service"""
        return await self.review_repo.get_by_service_id(service_id)
    
    async def get_user_reviews(self, user_id: int) -> List[Review]:
        """Get all reviews by a user"""
        return await self.review_repo.get_by_user_id(user_id)
    
    async def update_review(self, review_id: int, user_id: int, rating: int = None, comment: str = None) -> Review:
        """Update an existing review"""
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise ValueError("Review not found")
        
        # Get booking to check authorization
        booking = await self.booking_repo.get_by_id(review.booking_id)
        if not booking or booking.user_id != user_id:
            raise ValueError("Unauthorized to update this review")
        
        update_data = {}
        
        if rating is not None:
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            update_data["rating"] = rating
        
        if comment is not None:
            update_data["comment"] = comment.strip()
        
        if not update_data:
            raise ValueError("No valid fields to update")
        
        updated_review = await self.review_repo.update(review_id, update_data)
        if not updated_review:
            raise ValueError("Failed to update review")
        
        return updated_review
    
    async def delete_review(self, review_id: int, user_id: int) -> bool:
        """Delete a review"""
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise ValueError("Review not found")
        
        # Get booking to check authorization
        booking = await self.booking_repo.get_by_id(review.booking_id)
        if not booking or booking.user_id != user_id:
            raise ValueError("Unauthorized to delete this review")
        
        return await self.review_repo.delete(review_id)
    
    async def get_service_rating_stats(self, service_id: int) -> dict:
        """Get rating statistics for a service"""
        reviews = await self.review_repo.get_by_service_id(service_id)
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        total_reviews = len(reviews)
        total_rating = sum(review.rating for review in reviews)
        average_rating = round(total_rating / total_reviews, 2)
        
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        return {
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "rating_distribution": rating_distribution
        }
    
    async def get_recent_reviews(self, service_id: int, limit: int = 10) -> List[Review]:
        """Get recent reviews for a service"""
        reviews = await self.review_repo.get_by_service_id(service_id)
        # Sort by created_at in descending order and limit
        sorted_reviews = sorted(reviews, key=lambda x: x.created_at, reverse=True)
        return sorted_reviews[:limit]