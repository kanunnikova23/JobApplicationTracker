from sqlalchemy import Column, Integer, String, Date, UUID
from app.db import Base
from app.schemas import UserRole
from sqlalchemy import Enum as SQLEnum


class User(Base):
    __tablename__ = "users"
    # primary key column
    id = Column(UUID, primary_key=True, index=True)
    # other columns
    email = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole, name="user_role"), nullable=True, default="user")
    hashed_password = Column(String(100), nullable=False)
    created_at = Column(Date, nullable=False)
    last_login = Column(Date, nullable=True)
