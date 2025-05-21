from uuid import UUID

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import user_schemas
from app.crud import user_crud

router = APIRouter()


# Register a user
@router.post("/register", response_model=user_schemas.User)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db, user)


# Get user by ID
@router.get("/{id}", response_model=user_schemas.User)
def get_user_by_id(id: UUID, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, id)
    return user


# Update user
@router.put("/{id}", response_model=user_schemas.User)
def update_user(id: UUID, user_update: user_schemas.UserUpdate, db: Session = Depends(get_db)):
    return user_crud.update_user(db, id, user_update)


# Delete user
@router.delete("/{id}", status_code=204)
def delete_user(id: UUID, db: Session = Depends(get_db)):
    user_crud.delete_user(db, id)
