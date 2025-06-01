# unit tests for database logic
# CRUD Logic (No FastAPI involved)
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.crud import user_crud
from app.exceptions import (UserNotFoundException, DuplicateEmailException,
                            DuplicateUsernameException, AppBaseException)
from app.models import user_models
from app.schemas import user_schemas
from tests.conftest import AsyncTestingSessionLocal


@pytest.mark.anyio
async def test_create_user(db_session):
    user = user_schemas.UserCreate(
        email="example@gmail.com",
        username="jared232",
        full_name="Jared Smith",
        role="user",
        password="12320322dsek#€1"
    )
    result = await user_crud.create_user(db_session, user)
    assert result.email == "example@gmail.com"
    assert result.username == "jared232"


@pytest.mark.anyio
async def create_invalid_user(db_session):
    user = user_schemas.UserCreate(
        email="example@gmail.com",
        username="",
        full_name="Jared Smith",
        role="user",
        password="12320322dsek#€1"
    )
    result = await user_crud.create_user(db_session, user)
    assert result.email == "example@gmail.com"


@pytest.mark.anyio
async def test_create_user_with_duplicate_email(db_session):
    user1 = user_schemas.UserCreate(
        email="duplicate@gmail.com",
        username="userone",
        full_name="User One",
        role="user",
        password="password123"
    )
    await user_crud.create_user(db_session, user1)

    user2 = user_schemas.UserCreate(
        email="duplicate@gmail.com",  # same email!
        username="usertwo",
        full_name="User Two",
        role="user",
        password="password456"
    )
    with pytest.raises(DuplicateEmailException):
        await user_crud.create_user(db_session, user2)
        await db_session.commit()  # commit triggers the integrity error in SQLAlchemy


@pytest.mark.anyio
async def test_create_user_with_duplicate_username(db_session):
    user1 = user_schemas.UserCreate(
        email="unique1@gmail.com",
        username="sameusername",
        full_name="User One",
        role="user",
        password="password123"
    )
    await user_crud.create_user(db_session, user1)

    user2 = user_schemas.UserCreate(
        email="unique2@gmail.com",
        username="sameusername",  # same username!
        full_name="User Two",
        role="user",
        password="password456"
    )
    with pytest.raises(DuplicateUsernameException):
        await user_crud.create_user(db_session, user2)
        await db_session.commit()


@pytest.mark.anyio
async def test_get_user_with_username(db_session):
    user_create = user_schemas.UserCreate(
        email="usernamegurl@gmail.com",
        username="usernamegurl",
        full_name="UUID User",
        role="user",
        password="securepass"
    )
    created_user = await user_crud.create_user(db_session, user_create)

    fetched_user = await user_crud.get_user_by_username(db_session, username=created_user.username)
    assert fetched_user
    assert fetched_user.email == "usernamegurl@gmail.com"


@pytest.mark.anyio
async def test_create_user_with_invalid_username(db_session):
    invalid_username = "wwwww"

    with pytest.raises(UserNotFoundException):
        await user_crud.get_user_by_username(db_session, username=invalid_username)  # get_user validates UUID format


@pytest.mark.anyio
async def test_get_user_with_uuid(db_session):
    user_create = user_schemas.UserCreate(
        email="uuiduser@gmail.com",
        username="uuidgurl",
        full_name="UUID User",
        role="user",
        password="securepass"
    )
    created_user = await user_crud.create_user(db_session, user_create)

    fetched_user = await user_crud.get_user_by_id(db_session, user_id=created_user.id)
    assert fetched_user
    assert fetched_user.email == "uuiduser@gmail.com"


@pytest.mark.anyio
async def test_create_user_with_invalid_uuid(db_session):
    invalid_uuid = "not-a-valid-uuid"

    with pytest.raises(UserNotFoundException):
        await user_crud.get_user_by_id(db_session, user_id=invalid_uuid)  # get_user validates UUID format


@pytest.mark.anyio
async def test_update_user(db_session):
    user_create = user_schemas.UserCreate(
        email="updateuser@gmail.com",
        username="updategurl",
        full_name="Update User",
        role="user",
        password="oldpass"
    )
    user = await user_crud.create_user(db_session, user_create)

    update_data = user_schemas.UserUpdate(
        full_name="Updated User",
        password="newpass123"
    )
    updated_user = await user_crud.update_user(db_session, user.id, update_data)
    assert updated_user.full_name == "Updated User"


@pytest.mark.anyio
async def test_delete_user(db_session):
    user_create = user_schemas.UserCreate(
        email="deleteuser@gmail.com",
        username="deletegurl",
        full_name="Delete User",
        role="user",
        password="tobedeleted"
    )
    user = await user_crud.create_user(db_session, user_create)

    await user_crud.delete_user(db_session, user.id)

    # Fresh session to check true DB state
    async with AsyncTestingSessionLocal() as verify_session:
        result = await verify_session.execute(
            select(user_models.User).where(user_models.User.id == user.id)
        )
        user_in_db = result.scalar_one_or_none()
        assert user_in_db is None


@pytest.mark.anyio
async def test_raw_delete_verification():
    async with AsyncTestingSessionLocal() as session:
        user = user_models.User(
            email="rawdelete@gmail.com",
            username="rawtest",
            full_name="Raw Tester",
            role="user",
            hashed_password="hashed123"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        user_id = user.id

        await session.delete(user)
        await session.commit()

    # Re-check with fresh session
    async with AsyncTestingSessionLocal() as verify_session:
        result = await verify_session.execute(
            select(user_models.User).where(user_models.User.id == user_id)
        )
        user_in_db = result.scalar_one_or_none()
        assert user_in_db is None


@pytest.mark.anyio
async def test_update_user_integrity_error():
    # db session needs async-mocking
    db = MagicMock()
    db.commit = AsyncMock(side_effect=IntegrityError('mock', 'mock', 'mock'))
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()

    user_id = "some-id"
    mock_user = MagicMock()

    with patch('app.crud.user_crud.get_user_by_id', return_value=mock_user):
        updated_data = user_schemas.UserUpdate(email="duplicate@example.com")

        with pytest.raises(AppBaseException) as excinfo:
            await user_crud.update_user(db, user_id, updated_data)

        db.rollback.assert_called_once()
        assert excinfo.value.status_code == 409
        assert "Database integrity error" in excinfo.value.detail


@pytest.mark.anyio
async def test_create_user_with_duplicate_data(db_session):
    user = user_schemas.UserCreate(
        email="duplicate@example.com",
        username="uniqueusername",
        full_name="Test User",
        role="user",
        password="password123"
    )

    # Create user once (should succeed)
    await user_crud.create_user(db_session, user)

    # Mock db_session.commit() on the session instance passed as 'db_session'
    db_mock = MagicMock(wraps=db_session)
    db_mock.commit.side_effect = IntegrityError("duplicate key", None, None)

    with pytest.raises(AppBaseException) as exc_info:
        await user_crud.create_user(db_mock, user)

    assert exc_info.value.status_code == 409
    assert "Database integrity error" in exc_info.value.detail
