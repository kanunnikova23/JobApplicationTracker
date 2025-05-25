from app.db.database import SessionLocal, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


def get_db():
    """
        Sync DB session dependency.
        Yields a normal Session, then closes it.
        Use in `def` endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """
        Async DB session dependency.
        Yields an AsyncSession, then closes it.
        Use in `async def` endpoints.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # ensure all cleanup is done
            await session.close()
