from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    password_hash: str
    role: UserRole
    created_at: datetime