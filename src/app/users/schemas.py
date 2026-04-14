import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.app.users.models import UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    role: UserRole
    is_active: bool
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
