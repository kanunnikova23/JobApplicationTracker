from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy import Enum as SQLEnum

from app.db import Base
from app.schemas import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole, name="user_role"), nullable=False, default="user")
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
