from repositories.user_repository import UserRepository
from models.user import User, UserRole
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    async def create_user(self, name: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """Create a new user with hashed password"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = self._hash_password(password)
        
        # Create user data
        user_data = {
            "name": name,
            "email": email,
            "password_hash": hashed_password,
            "role": role.value
        }
        
        return await self.user_repo.create(user_data)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        if not self._verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def login_user(self, email: str, password: str) -> dict:
        """Login user and return access token"""
        user = await self.authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid email or password")
        
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self._create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.user_repo.get_by_email(email)
    
    async def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update user information"""
        # Remove sensitive fields that shouldn't be updated directly
        sensitive_fields = ["password_hash", "created_at", "id"]
        for field in sensitive_fields:
            update_data.pop(field, None)
        
        return await self.user_repo.update(user_id, update_data)
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not self._verify_password(old_password, user.password_hash):
            raise ValueError("Invalid current password")
        
        new_hashed_password = self._hash_password(new_password)
        update_result = await self.user_repo.update(user_id, {"password_hash": new_hashed_password})
        
        return update_result is not None
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        return await self.user_repo.delete(user_id)