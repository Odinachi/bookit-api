from repositories.booking_repository import BookingRepository
from repositories.service_repository import ServiceRepository
from repositories.user_repository import UserRepository
from models.booking import Booking, BookingStatus
from datetime import datetime, timedelta
from typing import List, Optional

class BookingService:
    def __init__(self, booking_repo: BookingRepository, service_repo: ServiceRepository, user_repo: UserRepository):
        self.booking_repo = booking_repo
        self.service_repo = service_repo
        self.user_repo = user_repo
    
    async def create_booking(self, user_id: int, service_id: int, start_time: datetime) -> Booking:
        """Create a new booking with validation"""
        # Validate user exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Validate service exists and is active
        service = await self.service_repo.get_by_id(service_id)
        if not service:
            raise ValueError("Service not found")
        
        if not service.is_active:
            raise ValueError("Service is not available")
        
        # Validate start time is in the future
        if start_time <= datetime.utcnow():
            raise ValueError("Booking start time must be in the future")
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=service.duration_minutes)
        
        # Check for conflicting bookings
        conflicts = await self.booking_repo.get_conflicting_bookings(service_id, start_time, end_time)
        if conflicts:
            raise ValueError("Time slot is already booked")
        
        booking_data = {
            "user_id": user_id,
            "service_id": service_id,
            "start_time": start_time,
            "end_time": end_time,
            "status": BookingStatus.PENDING
        }
        
        return await self.booking_repo.create(booking_data)
    
    async def get_booking_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        return await self.booking_repo.get_by_id(booking_id)
    
    async def get_user_bookings(self, user_id: int) -> List[Booking]:
        """Get all bookings for a user"""
        return await self.booking_repo.get_by_user_id(user_id)
    
    async def get_service_bookings(self, service_id: int) -> List[Booking]:
        """Get all bookings for a service"""
        return await self.booking_repo.get_by_service_id(service_id)
    
    async def confirm_booking(self, booking_id: int, user_id: int = None) -> Booking:
        """Confirm a pending booking"""
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        # If user_id is provided, check authorization
        if user_id and booking.user_id != user_id:
            raise ValueError("Unauthorized to confirm this booking")
        
        if booking.status != BookingStatus.PENDING:
            raise ValueError("Only pending bookings can be confirmed")
        
        # Check if booking time has not passed
        if booking.start_time <= datetime.utcnow():
            raise ValueError("Cannot confirm past bookings")
        
        updated_booking = await self.booking_repo.update_status(booking_id, BookingStatus.CONFIRMED)
        if not updated_booking:
            raise ValueError("Failed to confirm booking")
        
        return updated_booking
    
    async def cancel_booking(self, booking_id: int, user_id: int) -> Booking:
        """Cancel a booking"""
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        # Check authorization
        if booking.user_id != user_id:
            raise ValueError("Unauthorized to cancel this booking")
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            raise ValueError(f"Cannot cancel {booking.status.value} booking")
        
        # Check cancellation policy (e.g., can't cancel within 24 hours)
        hours_until_booking = (booking.start_time - datetime.utcnow()).total_seconds() / 3600
        if hours_until_booking < 24:
            raise ValueError("Cannot cancel booking within 24 hours of start time")
        
        updated_booking = await self.booking_repo.update_status(booking_id, BookingStatus.CANCELLED)
        if not updated_booking:
            raise ValueError("Failed to cancel booking")
        
        return updated_booking
    
    async def complete_booking(self, booking_id: int) -> Booking:
        """Mark booking as completed (admin only)"""
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError("Only confirmed bookings can be completed")
        
        # Check if booking end time has passed
        if booking.end_time > datetime.utcnow():
            raise ValueError("Cannot complete booking before end time")
        
        updated_booking = await self.booking_repo.update_status(booking_id, BookingStatus.COMPLETED)
        if not updated_booking:
            raise ValueError("Failed to complete booking")
        
        return updated_booking
    
    async def get_upcoming_bookings(self, user_id: int) -> List[Booking]:
        """Get upcoming bookings for a user"""
        user_bookings = await self.booking_repo.get_by_user_id(user_id)
        now = datetime.utcnow()
        
        return [
            booking for booking in user_bookings 
            if booking.start_time > now and booking.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ]
    
    async def get_booking_history(self, user_id: int) -> List[Booking]:
        """Get booking history for a user"""
        user_bookings = await self.booking_repo.get_by_user_id(user_id)
        now = datetime.utcnow()
        
        return [
            booking for booking in user_bookings 
            if booking.end_time <= now or booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]
        ]
    
    async def check_availability(self, service_id: int, start_time: datetime) -> bool:
        """Check if a time slot is available for booking"""
        service = await self.service_repo.get_by_id(service_id)
        if not service or not service.is_active:
            return False
        
        end_time = start_time + timedelta(minutes=service.duration_minutes)
        conflicts = await self.booking_repo.get_conflicting_bookings(service_id, start_time, end_time)
        
        return len(conflicts) == 0