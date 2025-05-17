# Create fresh DB(mock) for testing (Shared Test Setup)
import pytest  # 🧪 Pytest framework for writing and managing tests
from fastapi.testclient import TestClient  # 🚀 Used to simulate requests to FastAPI app in tests
from sqlalchemy import create_engine  # ⚙️ To create a DB connection
from sqlalchemy.orm import sessionmaker  # 🧵 For managing sessions to the DB
from app.api.deps import get_db  # 🧩 The FastAPI dependency I override in tests
from app.db.database import Base  # 🧱 SQLAlchemy models’ Base (used to create/drop tables)
from app.main import app  # 🚀 The actual FastAPI app object being tested
from app.models.job_models import JobApplication  # import JobApplication model
import datetime  # Import Python's date class to pass a date object instead of a string

# # Use separate SQLite DB for testing separately from prod one
SQLALCHEMY_TEST_DB_URL = "sqlite:///./test.db"

# Create engine that connects to the test DB
# "check_same_thread=False" is needed because SQLite is single-threaded by default
engine = create_engine(SQLALCHEMY_TEST_DB_URL, connect_args={"check_same_thread": False})

# Create a session factory bound to this test engine
# autocommit=False, autoflush=False = better control over transactions
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db():
    # 1. Setup: create all tables fresh in the test DB engine
    Base.metadata.create_all(bind=engine)  # engine is the test engine, not prod

    # Create a session to talk to this fresh test DB
    session = TestingSessionLocal()

    # 2. Yield: hand over the session for test to use
    try:
        # 🎯 Provide this DB session to tests via yield
        yield session
    finally:
        # 3. Teadrown: close the session and drop all tables (clean state)
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):  # 👈 db fixture is passed in, so every test gets a fresh session
    # This overrides the normal FastAPI DB dependency with the test session
    def override_get_db():
        try:
            yield db  # 🔁 Yield the test session instead of the real one
        finally:
            pass

    # Patch the app so that all routes now use test DB session
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def sample_applications(db):
    # Create one fake job application
    job = JobApplication(
        company="TestCompany",
        position="Python Developer",
        location="Remote",
        status="applied",
        applied_date=datetime.date(2025, 1, 1),
        link="http://example.com",
        notes="FastAPI FTW"
    )
    db.add(job)
    db.commit()
    db.refresh(job)  # to get the ID
    return [job]  # return it so you can use it in your tests if needed
