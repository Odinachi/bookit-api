from typing import List, Optional
from models.service import Service

class ServiceRepository:
    def __init__(self):
        self._services: List[Service] = []
        self._next_id = 1
    
    async def create(self, service_data: dict) -> Service:
        # Database logic for creating service
        pass
    
    async def get_by_id(self, service_id: int) -> Optional[Service]:
        # Database logic for getting service by ID
        pass
    
    async def get_all_active(self) -> List[Service]:
        # Database logic for getting all active services
        pass
    
    async def update(self, service_id: int, service_data: dict) -> Optional[Service]:
        # Database logic for updating service
        pass
    
    async def delete(self, service_id: int) -> bool:
        # Database logic for deleting service
        pass