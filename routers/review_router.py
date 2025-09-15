from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.review_service import ReviewService
from services.auth_service import AuthService
from repositories.review_repository import ReviewRepository
from repositories.booking_repository import BookingRepository
from repositories.user_repository import UserRepository
from models.review import Review
from models.user import User

router = APIRouter(prefix="/reviews", tags=["reviews"])

# Dependency injection
review_repo = ReviewRepository()
booking_repo = BookingRepository()
user_repo = UserRepository()
review_service = ReviewService(review_repo, booking_repo)
auth_service = AuthService(user_repo)

# Request/Response models
class ReviewCreate(BaseModel):
    booking_id: int
    rating: int
    comment: str

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    rating: int
    comment: str
    created_at: str

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Create a new review for a completed booking"""
    try:
        review = await review_service.create_review(
            booking_id=review_data.booking_id,
            user_id=current_user.id,
            rating=review_data.rating,
            comment=review_data.comment
        )
        return ReviewResponse(
            id=review.id,
            booking_id=review.booking_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat()
        )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "unauthorized" in str(e).lower() or "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(current_user: User = Depends(auth_service.get_current_user)):
    """Get all reviews by current user"""
    reviews = await review_service.get_user_reviews(current_user.id)
    return [
        ReviewResponse(
            id=review.id,
            booking_id=review.booking_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat()
        )
        for review in reviews
    ]

@router.get("/service/{service_id}", response_model=List[ReviewResponse])
async def get_service_reviews(service_id: int):
    """Get all reviews for a service (public endpoint)"""
    reviews = await review_service.get_service_reviews(service_id)
    return [
        ReviewResponse(
            id=review.id,
            booking_id=review.booking_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat()
        )
        for review in reviews
    ]

@router.get("/service/{service_id}/stats")
async def get_service_rating_stats(service_id: int):
    """Get rating statistics for a service"""
    stats = await review_service.get_service_rating_stats(service_id)
    return stats

@router.get("/service/{service_id}/recent")
async def get_recent_service_reviews(service_id: int, limit: int = 10):
    """Get recent reviews for a service"""
    if limit > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 50"
        )
    
    reviews = await review_service.get_recent_reviews(service_id, limit)
    return [
        ReviewResponse(
            id=review.id,
            booking_id=review.booking_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat()
        )
        for review in reviews
    ]

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int):
    """Get review by ID (public endpoint)"""
    review = await review_service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return ReviewResponse(
        id=review.id,
        booking_id=review.booking_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at.isoformat()
    )

@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Update review (only by review author)"""
    try:
        review = await review_service.update_review(
            review_id=review_id,
            user_id=current_user.id,
            rating=review_data.rating,
            comment=review_data.comment
        )
        return ReviewResponse(
            id=review.id,
            booking_id=review.booking_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat()
        )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Delete review (only by review author)"""
    try:
        success = await review_service.delete_review(review_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )