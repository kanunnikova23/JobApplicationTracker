from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., max_length=100, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    role: Optional[UserRole] = Field(default="user", description="User role")


class User(UserBase):
    id: UUID
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class UserCreate(UserBase):
    # plain password from frontend, will get hashed before saving into the DB as hashed_password
    password: str = Field(..., max_length=255, description="Password")


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None  # will re-hash if provided
