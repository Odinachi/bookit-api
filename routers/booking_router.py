from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import List
from services.booking_service import BookingService
from services.auth_service import AuthService
from repositories.booking_repository import BookingRepository
from repositories.service_repository import ServiceRepository
from repositories.user_repository import UserRepository
from models.booking import Booking, BookingStatus
from models.user import User

router = APIRouter(prefix="/bookings", tags=["bookings"])

# Dependency injection
booking_repo = BookingRepository()
service_repo = ServiceRepository()
user_repo = UserRepository()
booking_service = BookingService(booking_repo, service_repo, user_repo)
auth_service = AuthService(user_repo)

# Request/Response models
class BookingCreate(BaseModel):
    service_id: int
    start_time: datetime

class BookingResponse(BaseModel):
    id: int
    user_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime

class AvailabilityCheck(BaseModel):
    service_id: int
    start_time: datetime

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Create a new booking"""
    try:
        booking = await booking_service.create_booking(
            user_id=current_user.id,
            service_id=booking_data.service_id,
            start_time=booking_data.start_time
        )
        return {
            "status_code": 201,
            "message": "Booking created successfully",
            "data": BookingResponse(**booking.model_dump())
        }
    except ValueError as e:
        # Check if it's a conflict error
        if "already booked" in str(e) or "conflict" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )

@router.get("/")
async def get_user_bookings(current_user: User = Depends(auth_service.get_current_user)):
    """Get all bookings for current user"""
    bookings = await booking_service.get_user_bookings(current_user.id)
    return {
        "status_code": 200,
        "message": "User bookings retrieved successfully",
        "data": [BookingResponse(**booking.model_dump()) for booking in bookings]
    }

@router.get("/upcoming")
async def get_upcoming_bookings(current_user: User = Depends(auth_service.get_current_user)):
    """Get upcoming bookings for current user"""
    bookings = await booking_service.get_upcoming_bookings(current_user.id)
    return {
        "status_code": 200,
        "message": "Upcoming bookings retrieved successfully",
        "data": [BookingResponse(**booking.model_dump()) for booking in bookings]
    }

@router.get("/history")
async def get_booking_history(current_user: User = Depends(auth_service.get_current_user)):
    """Get booking history for current user"""
    bookings = await booking_service.get_booking_history(current_user.id)
    return {
        "status_code": 200,
        "message": "Booking history retrieved successfully",
        "data": [BookingResponse(**booking.model_dump()) for booking in bookings]
    }

@router.get("/{booking_id}")
async def get_booking(
    booking_id: int,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get booking by ID"""
    booking = await booking_service.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user owns the booking or is admin
    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "status_code": 200,
        "message": "Booking retrieved successfully",
        "data": BookingResponse(**booking.model_dump())
    }

@router.patch("/{booking_id}/confirm")
async def confirm_booking(
    booking_id: int,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Confirm a pending booking"""
    try:
        # Allow both user and admin to confirm
        booking = await booking_service.confirm_booking(
            booking_id=booking_id,
            user_id=current_user.id if current_user.role.value != "admin" else None
        )
        return {
            "status_code": 200,
            "message": "Booking confirmed successfully",
            "data": BookingResponse(**booking.model_dump())
        }
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

@router.patch("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Cancel a booking"""
    try:
        booking = await booking_service.cancel_booking(
            booking_id=booking_id,
            user_id=current_user.id
        )
        return {
            "status_code": 200,
            "message": "Booking cancelled successfully",
            "data": BookingResponse(**booking.model_dump())
        }
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

@router.patch("/{booking_id}/complete")
async def complete_booking(
    booking_id: int,
    current_user: User = Depends(auth_service.get_current_admin_user)
):
    """Mark booking as completed (admin only)"""
    try:
        booking = await booking_service.complete_booking(booking_id)
        return {
            "status_code": 200,
            "message": "Booking completed successfully",
            "data": BookingResponse(**booking.model_dump())
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

@router.post("/check-availability")
async def check_availability(
    availability_data: AvailabilityCheck,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Check if a time slot is available"""
    available = await booking_service.check_availability(
        service_id=availability_data.service_id,
        start_time=availability_data.start_time
    )
    return {
        "status_code": 200,
        "message": "Availability checked successfully",
        "data": {"available": available}
    }

# Admin routes
@router.get("/service/{service_id}")
async def get_service_bookings(
    service_id: int,
    current_user: User = Depends(auth_service.get_current_admin_user)
):
    """Get all bookings for a service (admin only)"""
    bookings = await booking_service.get_service_bookings(service_id)
    return {
        "status_code": 200,
        "message": "Service bookings retrieved successfully",
        "data": [BookingResponse(**booking.model_dump()) for booking in bookings]
    }