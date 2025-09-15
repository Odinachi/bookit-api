from typing import List, Optional
from models.review import Review
from database import get_database
from datetime import datetime

class ReviewRepository:
    def __init__(self):
        self.collection_name = "reviews"
    
    def get_collection(self):
        db = get_database()
        return db[self.collection_name]
    
    async def create(self, review_data: dict) -> Review:
        """Create a new review in MongoDB"""
        collection = self.get_collection()
        
        review_data["created_at"] = datetime.utcnow()
        review_data["id"] = await self._get_next_id()
        
        result = await collection.insert_one(review_data)
        created_review = await collection.find_one({"_id": result.inserted_id})
        return Review(**created_review)
    
    async def get_by_id(self, review_id: int) -> Optional[Review]:
        """Get review by ID from MongoDB"""
        collection = self.get_collection()
        review_doc = await collection.find_one({"id": review_id})
        
        if review_doc:
            return Review(**review_doc)
        return None
    
    async def get_by_booking_id(self, booking_id: int) -> Optional[Review]:
        """Get review by booking ID from MongoDB"""
        collection = self.get_collection()
        review_doc = await collection.find_one({"booking_id": booking_id})
        
        if review_doc:
            return Review(**review_doc)
        return None
    
    async def get_by_service_id(self, service_id: int) -> List[Review]:
        """Get reviews by service ID from MongoDB (through bookings)"""
        db = get_database()
        
        # Aggregate to join bookings and get reviews for a specific service
        pipeline = [
            {
                "$lookup": {
                    "from": "bookings",
                    "localField": "booking_id",
                    "foreignField": "id",
                    "as": "booking"
                }
            },
            {
                "$unwind": "$booking"
            },
            {
                "$match": {
                    "booking.service_id": service_id
                }
            }
        ]
        
        cursor = self.get_collection().aggregate(pipeline)
        reviews = []
        async for doc in cursor:
            # Remove the booking field from the document
            doc.pop("booking", None)
            reviews.append(Review(**doc))
        return reviews
    
    async def get_by_user_id(self, user_id: int) -> List[Review]:
        """Get reviews by user ID from MongoDB (through bookings)"""
        db = get_database()
        
        # Aggregate to join bookings and get reviews by a specific user
        pipeline = [
            {
                "$lookup": {
                    "from": "bookings",
                    "localField": "booking_id",
                    "foreignField": "id",
                    "as": "booking"
                }
            },
            {
                "$unwind": "$booking"
            },
            {
                "$match": {
                    "booking.user_id": user_id
                }
            }
        ]
        
        cursor = self.get_collection().aggregate(pipeline)
        reviews = []
        async for doc in cursor:
            # Remove the booking field from the document
            doc.pop("booking", None)
            reviews.append(Review(**doc))
        return reviews
    
    async def update(self, review_id: int, review_data: dict) -> Optional[Review]:
        """Update review in MongoDB"""
        collection = self.get_collection()
        
        result = await collection.update_one(
            {"id": review_id},
            {"$set": review_data}
        )
        
        if result.modified_count:
            return await self.get_by_id(review_id)
        return None
    
    async def delete(self, review_id: int) -> bool:
        """Delete review from MongoDB"""
        collection = self.get_collection()
        result = await collection.delete_one({"id": review_id})
        return result.deleted_count > 0
    
    async def _get_next_id(self) -> int:
        """Get next auto-increment ID"""
        db = get_database()
        counter = await db.counters.find_one_and_update(
            {"_id": "review_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return counter["seq"] if counter else 1