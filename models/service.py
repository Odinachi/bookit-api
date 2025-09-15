from pydantic import BaseModel
from datetime import datetime

class Service(BaseModel):
    id: int
    title: str
    description: str
    price: float
    duration_minutes: int
    is_active: bool
    created_at: datetime