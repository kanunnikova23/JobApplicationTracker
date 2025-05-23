# unit tests for database logic
# CRUD Logic (No FastAPI involved)
import pytest
from sqlalchemy.exc import IntegrityError

from app.crud import user_crud
from app.schemas import user_schemas
from app.exceptions import (UserNotFoundException, DuplicateEmailException,
                            DuplicateUsernameException, AppBaseException, ValidationError)

from unittest.mock import patch, MagicMock


def test_create_user(db):
    user = user_schemas.UserCreate(
        email="example@gmail.com",
        username="jared232",
        full_name="Jared Smith",
        role="user",
        password="12320322dsek#€1"
    )
    result = user_crud.create_user(db, user)
    assert result.email == "example@gmail.com"
    assert result.username == "jared232"


def create_invalid_user(db):
    user = user_schemas.UserCreate(
        email="example@gmail.com",
        username="",
        full_name="Jared Smith",
        role="user",
        password="12320322dsek#€1"
    )
    result = user_crud.create_user(db, user)
    assert result.email == "example@gmail.com"


def test_create_user_with_duplicate_email(db):
    user1 = user_schemas.UserCreate(
        email="duplicate@gmail.com",
        username="userone",
        full_name="User One",
        role="user",
        password="password123"
    )
    user_crud.create_user(db, user1)

    user2 = user_schemas.UserCreate(
        email="duplicate@gmail.com",  # same email!
        username="usertwo",
        full_name="User Two",
        role="user",
        password="password456"
    )
    with pytest.raises(DuplicateEmailException):
        user_crud.create_user(db, user2)
        db.commit()  # commit triggers the integrity error in SQLAlchemy


def test_create_user_with_duplicate_username(db):
    user1 = user_schemas.UserCreate(
        email="unique1@gmail.com",
        username="sameusername",
        full_name="User One",
        role="user",
        password="password123"
    )
    user_crud.create_user(db, user1)

    user2 = user_schemas.UserCreate(
        email="unique2@gmail.com",
        username="sameusername",  # same username!
        full_name="User Two",
        role="user",
        password="password456"
    )
    with pytest.raises(DuplicateUsernameException):
        user_crud.create_user(db, user2)
        db.commit()


def test_get_user_with_username(db):
    user_create = user_schemas.UserCreate(
        email="usernamegurl@gmail.com",
        username="usernamegurl",
        full_name="UUID User",
        role="user",
        password="securepass"
    )
    created_user = user_crud.create_user(db, user_create)

    fetched_user = user_crud.get_user_by_username(db, username=created_user.username)
    assert fetched_user
    assert fetched_user.email == "usernamegurl@gmail.com"


def test_create_user_with_invalid_username(db):
    invalid_username = "wwwww"

    with pytest.raises(UserNotFoundException):
        user_crud.get_user_by_username(db, username=invalid_username)  # get_user validates UUID format


def test_get_user_with_uuid(db):
    user_create = user_schemas.UserCreate(
        email="uuiduser@gmail.com",
        username="uuidgurl",
        full_name="UUID User",
        role="user",
        password="securepass"
    )
    created_user = user_crud.create_user(db, user_create)

    fetched_user = user_crud.get_user_by_id(db, user_id=created_user.id)
    assert fetched_user
    assert fetched_user.email == "uuiduser@gmail.com"


def test_create_user_with_invalid_uuid(db):
    invalid_uuid = "not-a-valid-uuid"

    with pytest.raises(UserNotFoundException):
        user_crud.get_user_by_id(db, user_id=invalid_uuid)  # get_user validates UUID format


def test_update_user(db):
    user_create = user_schemas.UserCreate(
        email="updateuser@gmail.com",
        username="updategurl",
        full_name="Update User",
        role="user",
        password="oldpass"
    )
    user = user_crud.create_user(db, user_create)

    update_data = user_schemas.UserUpdate(
        full_name="Updated User",
        password="newpass123"
    )
    updated_user = user_crud.update_user(db, user.id, update_data)
    assert updated_user.full_name == "Updated User"


def test_delete_user(db):
    user_create = user_schemas.UserCreate(
        email="deleteuser@gmail.com",
        username="deletegurl",
        full_name="Delete User",
        role="user",
        password="tobedeleted"
    )
    user = user_crud.create_user(db, user_create)

    user_crud.delete_user(db, user.id)
    with pytest.raises(UserNotFoundException):
        user_crud.get_user_by_id(db, user.id)


def test_update_user_integrity_error():
    db = MagicMock()
    user_id = 1
    mock_user = MagicMock()

    with patch('app.crud.user_crud.get_user_by_id', return_value=mock_user):
        # Make commit raise IntegrityError to test rollback and exception
        db.commit.side_effect = IntegrityError('mock', 'mock', 'mock')

        updated_data = user_schemas.UserUpdate(email="duplicate@example.com")

        with pytest.raises(AppBaseException) as excinfo:
            user_crud.update_user(db, user_id, updated_data)

        db.rollback.assert_called_once()
        assert excinfo.value.status_code == 409
        assert "Database integrity error" in excinfo.value.detail


def test_create_user_with_duplicate_data(db):
    user = user_schemas.UserCreate(
        email="duplicate@example.com",
        username="uniqueusername",
        full_name="Test User",
        role="user",
        password="password123"
    )

    # Create user once (should succeed)
    user_crud.create_user(db, user)

    # Mock db.commit() on the session instance passed as 'db'
    db_mock = MagicMock(wraps=db)
    db_mock.commit.side_effect = IntegrityError("duplicate key", None, None)

    with pytest.raises(AppBaseException) as exc_info:
        user_crud.create_user(db_mock, user)

    assert exc_info.value.status_code == 409
    assert "Database integrity error" in exc_info.value.detail
