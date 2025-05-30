from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_async_db

from app.schemas import user_schemas
from app.crud import user_crud

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Register a user
@router.post("/register", response_model=user_schemas.User, status_code=201)
async def create_user(user: user_schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):
    return await user_crud.create_user(db, user)


@router.get("/", response_model=list[user_schemas.User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_db)):
    return await user_crud.get_users(db, skip=skip, limit=limit)


# GET /users/username/{username} for user-friendly URLs
@router.get("/username/{username}", response_model=user_schemas.UserBase)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_async_db)):
    user = await user_crud.get_user_by_username(db, username)
    return user


# GET /users/{user_id} for internal logic (auth, DB operations)
@router.get("/{user_id}", response_model=user_schemas.User)
async def get_user_by_id(user_id: str, db: AsyncSession = Depends(get_async_db)):
    try:
        _ = UUID(user_id)  # Just to validate the UUID format because SQLite stores uuid as text
        user = await user_crud.get_user_by_id(db, user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format.")
    return user


# Update user
@router.put("/{user_id}", response_model=user_schemas.User, status_code=200)
async def update_user(user_id: str, user_update: user_schemas.UserUpdate, db: AsyncSession = Depends(get_async_db)):
    return await user_crud.update_user(db, user_id, user_update)


# Delete user
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_async_db)):
    await user_crud.delete_user(db, user_id)
    return
