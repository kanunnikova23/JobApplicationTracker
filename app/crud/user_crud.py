from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models.user_models as models
import app.schemas.user_schemas as schemas
from app.core.logger import logger
from app.exceptions import AppBaseException, UserNotFoundException, DuplicateUsernameException, DuplicateEmailException

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db, user: schemas.UserCreate):
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
        db.commit()
        db.refresh(db_user)
        logger.info(f"✅ Created user: {db_user.username} with ID {db_user.id}")

    except IntegrityError as e:
        db.rollback()
        # Peek into error message string to figure out which unique constraint failed
        err_msg = str(e.orig).lower()
        if "username" in err_msg:
            raise DuplicateUsernameException(db_user.username)
        elif "email" in err_msg:
            raise DuplicateEmailException(db_user.email)
        else:
            raise AppBaseException(status_code=409, detail="Database integrity error.")
    return db_user


def get_user_by_id(db: Session, user_id: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        # invoking custom exception
        raise UserNotFoundException(str(user_id))
    return user


def delete_user(db, user_id):
    user = get_user_by_id(db, user_id)
    try:
        db.delete(user)
        db.commit()
        logger.info(f"🗑️ Deleted user with ID {user_id}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise  # re-raise original error so you don't mask it


def update_user(db, user_id, updated_data: schemas.UserUpdate):
    try:
        #  Fetch the job entry from the database
        user = get_user_by_id(db, user_id)
        #  Update only the fields that were actually passed in the request
        for key, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        #  Save and refresh the changes in the DB
        db.commit()
        db.refresh(user)
        #  Log what got updated
        logger.info(
            f"✏️ Updated user with ID {user_id} with fields: {list(updated_data.model_dump(exclude_unset=True).keys())}")
        #  Return the fully updated model
        return user
    except IntegrityError:
        db.rollback()
        raise AppBaseException(status_code=409, detail="Database integrity error during update.")


def get_user_by_username(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise UserNotFoundException(username)
    return user
