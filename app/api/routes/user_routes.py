from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db

from app.schemas import user_schemas
from app.crud import user_crud

router = APIRouter()


# Register a user
@router.post("/register", response_model=user_schemas.User)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db, user)


@router.get("/", response_model=list[user_schemas.User])
def read_applications(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return user_crud.get_users(db, skip=skip, limit=limit)


# GET /users/{user_id} for internal logic (auth, DB operations)
@router.get("/{user_id}", response_model=user_schemas.User)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    try:
        _ = UUID(user_id)  # Just to validate the UUID format because SQLite stores uuid as text
        user = user_crud.get_user_by_id(db, user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format.")
    return user


# GET /users/username/{username} for user-friendly URLs
@router.get("/username/{username}", response_model=user_schemas.UserBase)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_username(db, username)
    return user


# Update user
@router.put("/{user_id}", response_model=user_schemas.User)
def update_user(user_id: str, user_update: user_schemas.UserUpdate, db: Session = Depends(get_db)):
    return user_crud.update_user(db, user_id, user_update)


# Delete user
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user_crud.delete_user(db, user_id)
