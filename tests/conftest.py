# Create fresh DB(mock) for testing (Shared Test Setup)
import datetime  # Import Python's date class to pass a date object instead of a string
import pytest  # Pytest framework for writing and managing tests
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.api.deps import get_async_db  # The FastAPI dependency I override in tests
from app.db import Base  # SQLAlchemy models’ Base (used to create/drop tables)
from app.main import app  # The actual FastAPI app object being tested
from app.models import JobApplication, User  # import JobApplication and User DB models

# Use separate SQLite DB for testing separately from prod one
SQLALCHEMY_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# Create engine that connects to the test DB
# "check_same_thread=False" is needed because SQLite is single-threaded by default
engine = create_async_engine(
    SQLALCHEMY_TEST_DB_URL,
    connect_args={"check_same_thread": False}
)
# Create a session factory bound to this test engine (used for test sessions)
# autocommit=False, autoflush=False = better control over transactions
AsyncTestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession)


# anyio_backend: Required by pytest-anyio to work with asyncio
@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'


# 🔁 Override the actual get_async_db dependency with test DB
async def override_get_async_db():
    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="module", autouse=True)
async def set_dependency_override():
    app.dependency_overrides[get_async_db] = override_get_async_db


# 🏗️ Create schema for testing -  Create + Drop tables before/after test session
@pytest.fixture(scope="session", autouse=True)
async def prepare_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Create tables
    yield
    # Optionally tear down
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with AsyncTestingSessionLocal() as session:
        # Clear tables for test isolation
        await session.execute(delete(JobApplication))
        await session.execute(delete(User))
        await session.commit()
        yield session


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def sample_applications(db_session: AsyncSession):
    base_date = datetime.date(2025, 4, 1)

    jobs = [
        JobApplication(
            company="TestCompany",
            position="Backend Developer",
            location="Cork",
            status="applied",
            applied_date=base_date,
            link="https://apple.com/job",
            notes="Excited for this role"
        ),
        JobApplication(
            company="Google",
            position="Frontend Engineer",
            location="Dublin",
            status="rejected",
            applied_date=base_date + datetime.timedelta(days=1),
            link="https://google.com/job",
            notes="Already rejected, oof"
        ),
        JobApplication(
            company="Amazon",
            position="DevOps Specialist",
            location="Remote",
            status="interviewing",
            applied_date=base_date + datetime.timedelta(days=2),
            link="https://amazon.com/job",
            notes="Interviewing next week"
        ),
        JobApplication(
            company="Meta",
            position="Data Analyst",
            location="London",
            status="offered",
            applied_date=base_date + datetime.timedelta(days=3),
            link="https://meta.com/job",
            notes="Offer pending"
        ),
        JobApplication(
            company="Netflix",
            position="SRE",
            location="Berlin",
            status="withdrawn",
            applied_date=base_date + datetime.timedelta(days=4),
            link="https://netflix.com/job",
            notes="Withdrawn after interview"
        ),
    ]

    db_session.add_all(jobs)
    await db_session.commit()
    return jobs


@pytest.fixture(scope="function")
async def sample_user(db_session):
    # Create one fake job application
    user = User(
        email="example@gmail.com",
        username="jared232",
        full_name="Jared Smith",
        role="user",
        hashed_password="12320322dsek#€1",
        created_at=datetime.date(2025, 5, 23),
        last_login=None
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)  # to get the ID
    return [user]  # return it so you can use it in your tests if needed
