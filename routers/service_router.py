from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.service_service import ServiceService
from services.auth_service import AuthService
from repositories.service_repository import ServiceRepository
from repositories.user_repository import UserRepository
from models.service import Service
from models.user import User

router = APIRouter(prefix="/services", tags=["services"])

# Dependency injection
service_repo = ServiceRepository()
user_repo = UserRepository()
service_service = ServiceService(service_repo)
auth_service = AuthService(user_repo)

# Dependency functions
async def get_current_admin_user(current_user: User = Depends(auth_service.get_current_admin_user)) -> User:
    """Dependency to get current admin user"""
    return current_user

# Request/Response models
class ServiceCreate(BaseModel):
    title: str
    description: str
    price: float
    duration_minutes: int

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class ServiceResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    duration_minutes: int
    is_active: bool
    created_at: str

@router.get("/")
async def get_services():
    """Get all active services (public endpoint)"""
    services = await service_service.get_all_active_services()
    return {
        "status_code": 200,
        "message": "Active services retrieved successfully",
        "data": [
            ServiceResponse(
                id=service.id,
                title=service.title,
                description=service.description,
                price=service.price,
                duration_minutes=service.duration_minutes,
                is_active=service.is_active,
                created_at=service.created_at.isoformat()
            )
            for service in services
        ]
    }

@router.get("/all")
async def get_all_services(current_user: User = Depends(get_current_admin_user)):
    """Get all services including inactive ones (admin only)"""
    services = await service_service.get_all_services()
    return {
        "status_code": 200,
        "message": "All services retrieved successfully",
        "data": [
            ServiceResponse(
                id=service.id,
                title=service.title,
                description=service.description,
                price=service.price,
                duration_minutes=service.duration_minutes,
                is_active=service.is_active,
                created_at=service.created_at.isoformat()
            )
            for service in services
        ]
    }

@router.get("/search")
async def search_services(q: str):
    """Search services by title or description"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    services = await service_service.search_services(q.strip())
    return {
        "status_code": 200,
        "message": f"Search results for '{q}'",
        "data": [
            ServiceResponse(
                id=service.id,
                title=service.title,
                description=service.description,
                price=service.price,
                duration_minutes=service.duration_minutes,
                is_active=service.is_active,
                created_at=service.created_at.isoformat()
            )
            for service in services
        ]
    }

@router.get("/{service_id}")
async def get_service(service_id: int):
    """Get service by ID"""
    service = await service_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return {
        "status_code": 200,
        "message": "Service retrieved successfully",
        "data": ServiceResponse(
            id=service.id,
            title=service.title,
            description=service.description,
            price=service.price,
            duration_minutes=service.duration_minutes,
            is_active=service.is_active,
            created_at=service.created_at.isoformat()
        )
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new service (admin only)"""
    try:
        service = await service_service.create_service(
            title=service_data.title,
            description=service_data.description,
            price=service_data.price,
            duration_minutes=service_data.duration_minutes
        )
        return {
            "status_code": 201,
            "message": "Service created successfully",
            "data": ServiceResponse(
                id=service.id,
                title=service.title,
                description=service.description,
                price=service.price,
                duration_minutes=service.duration_minutes,
                is_active=service.is_active,
                created_at=service.created_at.isoformat()
            )
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{service_id}")
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """Update service (admin only)"""
    try:
        # Convert to dict and remove None values
        update_data = {k: v for k, v in service_data.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        service = await service_service.update_service(service_id, update_data)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        return {
            "status_code": 200,
            "message": "Service updated successfully",
            "data": ServiceResponse(
                id=service.id,
                title=service.title,
                description=service.description,
                price=service.price,
                duration_minutes=service.duration_minutes,
                is_active=service.is_active,
                created_at=service.created_at.isoformat()
            )
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{service_id}/activate")
async def activate_service(
    service_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    """Activate service (admin only)"""
    service = await service_service.activate_service(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return {
        "status_code": 200,
        "message": "Service activated successfully",
        "data": ServiceResponse(
            id=service.id,
            title=service.title,
            description=service.description,
            price=service.price,
            duration_minutes=service.duration_minutes,
            is_active=service.is_active,
            created_at=service.created_at.isoformat()
        )
    }

@router.patch("/{service_id}/deactivate")
async def deactivate_service(
    service_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    """Deactivate service (admin only)"""
    service = await service_service.deactivate_service(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return {
        "status_code": 200,
        "message": "Service deactivated successfully",
        "data": ServiceResponse(
            id=service.id,
            title=service.title,
            description=service.description,
            price=service.price,
            duration_minutes=service.duration_minutes,
            is_active=service.is_active,
            created_at=service.created_at.isoformat()
        )
    }

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    """Delete service (admin only) - soft delete by deactivating"""
    success = await service_service.delete_service(service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return {
        "status_code": 204,
        "message": "Service deleted successfully",
        "data": None
    }