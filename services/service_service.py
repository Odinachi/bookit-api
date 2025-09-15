from repositories.service_repository import ServiceRepository
from models.service import Service
from typing import List, Optional
from datetime import datetime

class ServiceService:
    def __init__(self, service_repo: ServiceRepository):
        self.service_repo = service_repo
    
    async def create_service(self, title: str, description: str, price: float, duration_minutes: int) -> Service:
        """Create a new service"""
        # Validate input
        if price <= 0:
            raise ValueError("Price must be greater than 0")
        
        if duration_minutes <= 0:
            raise ValueError("Duration must be greater than 0")
        
        if len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        service_data = {
            "title": title.strip(),
            "description": description.strip(),
            "price": price,
            "duration_minutes": duration_minutes,
            "is_active": True
        }
        
        return await self.service_repo.create(service_data)
    
    async def get_service_by_id(self, service_id: int) -> Optional[Service]:
        """Get service by ID"""
        return await self.service_repo.get_by_id(service_id)
    
    async def get_all_active_services(self) -> List[Service]:
        """Get all active services"""
        return await self.service_repo.get_all_active()
    
    async def get_all_services(self) -> List[Service]:
        """Get all services (admin only)"""
        return await self.service_repo.get_all()
    
    async def update_service(self, service_id: int, update_data: dict) -> Optional[Service]:
        """Update service information"""
        # Validate update data
        if "price" in update_data and update_data["price"] <= 0:
            raise ValueError("Price must be greater than 0")
        
        if "duration_minutes" in update_data and update_data["duration_minutes"] <= 0:
            raise ValueError("Duration must be greater than 0")
        
        if "title" in update_data and len(update_data["title"].strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        # Remove sensitive fields
        update_data.pop("id", None)
        update_data.pop("created_at", None)
        
        return await self.service_repo.update(service_id, update_data)
    
    async def activate_service(self, service_id: int) -> Optional[Service]:
        """Activate a service"""
        return await self.service_repo.update(service_id, {"is_active": True})
    
    async def deactivate_service(self, service_id: int) -> Optional[Service]:
        """Deactivate a service"""
        return await self.service_repo.update(service_id, {"is_active": False})
    
    async def delete_service(self, service_id: int) -> bool:
        """Delete service (soft delete by deactivating)"""
        result = await self.service_repo.update(service_id, {"is_active": False})
        return result is not None
    
    async def search_services(self, query: str) -> List[Service]:
        """Search services by title or description"""
        return await self.service_repo.search(query)