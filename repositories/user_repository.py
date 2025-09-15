from typing import List, Optional
from models.user import User, UserRole
from database import get_database
from datetime import datetime
from bson import ObjectId

class UserRepository:
    def __init__(self):
        self.collection_name = "users"
    
    def get_collection(self):
        db = get_database()
        return db[self.collection_name]
    
    async def create(self, user_data: dict) -> User:
        """Create a new user in MongoDB"""
        collection = self.get_collection()
        
        # Add timestamp
        user_data["created_at"] = datetime.utcnow()
        user_data["id"] = await self._get_next_id()
        
        result = await collection.insert_one(user_data)
        
        # Fetch the created user
        created_user = await collection.find_one({"_id": result.inserted_id})
        return User(**created_user)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID from MongoDB"""
        collection = self.get_collection()
        user_doc = await collection.find_one({"id": user_id})
        
        if user_doc:
            return User(**user_doc)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email from MongoDB"""
        collection = self.get_collection()
        user_doc = await collection.find_one({"email": email})
        
        if user_doc:
            return User(**user_doc)
        return None
    
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user in MongoDB"""
        collection = self.get_collection()
        
        result = await collection.update_one(
            {"id": user_id},
            {"$set": user_data}
        )
        
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None
    
    async def delete(self, user_id: int) -> bool:
        """Delete user from MongoDB"""
        collection = self.get_collection()
        result = await collection.delete_one({"id": user_id})
        return result.deleted_count > 0
    
    async def _get_next_id(self) -> int:
        """Get next auto-increment ID"""
        db = get_database()
        counter = await db.counters.find_one_and_update(
            {"_id": "user_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return counter["seq"] if counter else 1