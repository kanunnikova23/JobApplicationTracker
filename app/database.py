# Connects to the DB and manages sessions.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the connection string to SQLite database file.
SQLALCHEMY_DATABASE_URL = "sqlite:///./job_applications.db"

# Create the engine with SQLALCHEMY_DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Set up a custom session class
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for all models
Base = declarative_base()
