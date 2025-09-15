from typing import List, Optional
from models.review import Review

class ReviewRepository:
    def __init__(self):
        self._reviews: List[Review] = []
        self._next_id = 1
    
    async def create(self, review_data: dict) -> Review:
        # Database logic for creating review
        pass
    
    async def get_by_booking_id(self, booking_id: int) -> Optional[Review]:
        # Database logic for getting review by booking
        pass
    
    async def get_by_service_id(self, service_id: int) -> List[Review]:
        # Database logic for getting reviews by service
        pass