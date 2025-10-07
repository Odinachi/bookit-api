from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User, UserRole
from repositories.user_repository import UserRepository
import os

security = HTTPBearer()

# Global instances for dependency injection
user_repo = UserRepository()

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Get current user from JWT token"""
        token = credentials.credentials
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    async def get_current_admin_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Get current user and verify admin role"""
        current_user = await self.get_current_user(credentials)
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Global auth service instance
auth_service = AuthService(user_repo)