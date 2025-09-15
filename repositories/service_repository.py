from typing import List, Optional
from models.service import Service
from database import get_database
from datetime import datetime

class ServiceRepository:
    def __init__(self):
        self.collection_name = "services"
    
    def get_collection(self):
        db = get_database()
        return db[self.collection_name]
    
    async def create(self, service_data: dict) -> Service:
        """Create a new service in MongoDB"""
        collection = self.get_collection()
        
        service_data["created_at"] = datetime.utcnow()
        service_data["id"] = await self._get_next_id()
        
        result = await collection.insert_one(service_data)
        created_service = await collection.find_one({"_id": result.inserted_id})
        return Service(**created_service)
    
    async def get_by_id(self, service_id: int) -> Optional[Service]:
        """Get service by ID from MongoDB"""
        collection = self.get_collection()
        service_doc = await collection.find_one({"id": service_id})
        
        if service_doc:
            return Service(**service_doc)
        return None
    
    async def get_all_active(self) -> List[Service]:
        """Get all active services from MongoDB"""
        collection = self.get_collection()
        cursor = collection.find({"is_active": True})
        services = []
        async for doc in cursor:
            services.append(Service(**doc))
        return services
    
    async def get_all(self) -> List[Service]:
        """Get all services from MongoDB"""
        collection = self.get_collection()
        cursor = collection.find({})
        services = []
        async for doc in cursor:
            services.append(Service(**doc))
        return services
    
    async def update(self, service_id: int, service_data: dict) -> Optional[Service]:
        """Update service in MongoDB"""
        collection = self.get_collection()
        
        result = await collection.update_one(
            {"id": service_id},
            {"$set": service_data}
        )
        
        if result.modified_count:
            return await self.get_by_id(service_id)
        return None
    
    async def delete(self, service_id: int) -> bool:
        """Delete service from MongoDB"""
        collection = self.get_collection()
        result = await collection.delete_one({"id": service_id})
        return result.deleted_count > 0
    
    async def search(self, query: str) -> List[Service]:
        """Search services by title or description"""
        collection = self.get_collection()
        cursor = collection.find({
            "$and": [
                {"is_active": True},
                {
                    "$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"description": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        })
        services = []
        async for doc in cursor:
            services.append(Service(**doc))
        return services
    
    async def _get_next_id(self) -> int:
        """Get next auto-increment ID"""
        db = get_database()
        counter = await db.counters.find_one_and_update(
            {"_id": "service_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return counter["seq"] if counter else 1