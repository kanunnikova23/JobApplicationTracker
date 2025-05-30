from datetime import datetime
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.user_models as models
import app.schemas.user_schemas as schemas
from app.core.logger import logger
from app.exceptions import AppBaseException, UserNotFoundException, DuplicateUsernameException, DuplicateEmailException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    try:
        hashed_pw = pwd_context.hash(user.password)
        db_user = models.User(
            id=str(uuid4()),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role or schemas.UserRole.USER,
            hashed_password=hashed_pw,
            created_at=datetime.now(),
            last_login=None,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"✅ Created user: {db_user.username} with ID {db_user.id}")

    except IntegrityError as e:
        await db.rollback()
        # Peek into error message string to figure out which unique constraint failed
        err_msg = str(e.orig).lower()
        if "username" in err_msg:
            raise DuplicateUsernameException(db_user.username)
        elif "email" in err_msg:
            raise DuplicateEmailException(db_user.email)
        else:
            raise AppBaseException(status_code=409, detail="Database integrity error.")
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: str):
    user = await fetch_user(db, select(models.User).where(models.User.id == user_id))
    if not user:
        # invoking custom exception
        raise UserNotFoundException(str(user_id))
    return user


async def delete_user(db: AsyncSession, user_id: str):
    try:
        user = await fetch_user(db, select(models.User).where(models.User.id == user_id))
        if not user:
            raise UserNotFoundException
        db.delete(user)
        await db.commit()
        logger.info(f"🗑️ Deleted user with ID {user_id}")
        return user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise  # re-raise original error so you don't mask it


async def update_user(db: AsyncSession, user_id, updated_data: schemas.UserUpdate):
    try:
        #  Fetch the user entry from the database
        user = await get_user_by_id(db, user_id)
        update_fields = updated_data.model_dump(exclude_unset=True)

        #  Update only the fields that were actually passed in the request
        for key, value in update_fields.items():
            setattr(user, key, value)
        #  Save and refresh the changes in the DB
        await db.commit()
        await db.refresh(user)
        #  Log what got updated
        logger.info(
            f"✏️ Updated user with ID {user_id} with fields: {list(update_fields.keys())}")
        #  Return the fully updated model
        return user
    except IntegrityError:
        await db.rollback()
        raise AppBaseException(status_code=409, detail="Database integrity error during update.")
    except Exception:
        await db.rollback()
        raise AppBaseException(status_code=500, detail="Unexpected error during update.")


async def get_user_by_username(db: AsyncSession, username: str):
    user = await fetch_user(db, select(models.User).where(models.User.username == username))
    if not user:
        raise UserNotFoundException(username)
    return user


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    try:
        result = await db.execute(
            select(models.User).offset(skip).limit(limit)
        )
        logger.info(f"📄 Fetched users: skip={skip}, limit={limit}")
        return result.scalars().all()
    except Exception:
        raise AppBaseException(status_code=500, detail="Internal server error while fetching users.")


async def fetch_user(db: AsyncSession, stmt) -> models.User | None:
    """
        Executes the provided SQLAlchemy select() statement and returns a single ORM object or None.
    """
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
