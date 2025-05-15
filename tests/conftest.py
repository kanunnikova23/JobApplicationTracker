# Create fresh DB(mock) for testing (Shared Test Setup)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.db.database import Base
from app.main import app

# # Use in-memory SQLite DB
SQLALCHEMY_TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db():
    # 1. Setup: create all tables fresh in the test DB engine
    Base.metadata.create_all(bind=engine)  # engine is the test engine, not prod

    session = TestingSessionLocal()

    # 2. Yield: hand over the session for test to use
    try:
        yield session
    finally:
        # 3. Teardown: clean up after test
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    #  override get_db to return session fixture
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
