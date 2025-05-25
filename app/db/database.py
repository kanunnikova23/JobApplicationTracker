# Connects to the DB and manages sessions.
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env
load_dotenv()

# Grab the DB URL from the environment
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")

# Derive your sync & async URLs - declare as constants
SYNC_DB_URL = SQLALCHEMY_DATABASE_URL
ASYNC_DB_URL = SYNC_DB_URL.replace("sqlite://", "sqlite+aiosqlite://")

# Create the engine — with special SQLite handling
engine = create_engine(
    SYNC_DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SYNC_DB_URL else {}
)

# Create the async engine
async_engine = create_async_engine(
    ASYNC_DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DB_URL else {},
)

# Session makers
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

# AsyncSession factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
