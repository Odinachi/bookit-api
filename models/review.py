from pydantic import BaseModel
from datetime import datetime

class Review(BaseModel):
    id: int
    booking_id: int
    rating: int  # 1-5
    comment: str
    created_at: datetime

    class Config:
        # Validate rating is between 1-5
        schema_extra = {
            "example": {
                "id": 1,
                "booking_id": 1,
                "rating": 5,
                "comment": "Excellent service!",
                "created_at": "2024-01-01T10:00:00"
            }
        }