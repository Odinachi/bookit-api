from typing import List, Optional
from models.booking import Booking, BookingStatus
from database import get_database
from datetime import datetime

class BookingRepository:
    def __init__(self):
        self.collection_name = "bookings"
    
    def get_collection(self):
        db = get_database()
        return db[self.collection_name]
    
    async def create(self, booking_data: dict) -> Booking:
        """Create a new booking in MongoDB"""
        collection = self.get_collection()
        
        booking_data["created_at"] = datetime.utcnow()
        booking_data["id"] = await self._get_next_id()
        booking_data["status"] = booking_data["status"].value
        
        result = await collection.insert_one(booking_data)
        created_booking = await collection.find_one({"_id": result.inserted_id})
        return Booking(**created_booking)
    
    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID from MongoDB"""
        collection = self.get_collection()
        booking_doc = await collection.find_one({"id": booking_id})
        
        if booking_doc:
            return Booking(**booking_doc)
        return None
    
    async def get_by_user_id(self, user_id: int) -> List[Booking]:
        """Get bookings by user ID from MongoDB"""
        collection = self.get_collection()
        cursor = collection.find({"user_id": user_id})
        bookings = []
        async for doc in cursor:
            bookings.append(Booking(**doc))
        return bookings
    
    async def get_by_service_id(self, service_id: int) -> List[Booking]:
        """Get bookings by service ID from MongoDB"""
        collection = self.get_collection()
        cursor = collection.find({"service_id": service_id})
        bookings = []
        async for doc in cursor:
            bookings.append(Booking(**doc))
        return bookings
    
    async def update_status(self, booking_id: int, status: BookingStatus) -> Optional[Booking]:
        """Update booking status in MongoDB"""
        collection = self.get_collection()
        
        result = await collection.update_one(
            {"id": booking_id},
            {"$set": {"status": status.value}}
        )
        
        if result.modified_count:
            return await self.get_by_id(booking_id)
        return None
    
    async def get_conflicting_bookings(self, service_id: int, start_time: datetime, end_time: datetime) -> List[Booking]:
        """Get bookings that conflict with the given time range"""
        collection = self.get_collection()
        
        cursor = collection.find({
            "service_id": service_id,
            "status": {"$in": [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]},
            "$or": [
                {
                    "start_time": {"$lt": end_time},
                    "end_time": {"$gt": start_time}
                }
            ]
        })
        
        bookings = []
        async for doc in cursor:
            bookings.append(Booking(**doc))
        return bookings
    
    async def _get_next_id(self) -> int:
        """Get next auto-increment ID"""
        db = get_database()
        counter = await db.counters.find_one_and_update(
            {"_id": "booking_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return counter["seq"] if counter else 1