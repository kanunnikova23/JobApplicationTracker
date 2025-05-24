from pydantic import ValidationError
from app.schemas.user_schemas import UserCreate, UserUpdate, UserRole
import pytest


#  Valid user creation
def test_valid_user_create_schema():
    user = UserCreate(
        email="oleksandra@example.com",
        username="oleksandra",
        full_name="Oleksandra Kovalenko",
        role=UserRole.USER,
        password="supersecret123"
    )
    assert user.email == "oleksandra@example.com"
    assert user.role == UserRole.USER


#  Missing required field: email
def test_user_schema_missing_email():
    with pytest.raises(ValidationError):
        UserCreate(username="test", password="secret")  # missing email field!="password123"
        print(ValidationError)


#  Missing required field: password
def test_user_schema_missing_password():
    with pytest.raises(ValidationError):
        UserCreate(
            email="oleksandra@example.com",
            username="oleksandra"
        )


#  Invalid email format
def test_user_schema_invalid_email_format():
    with pytest.raises(ValidationError):
        UserCreate(
            username="oleksandra",
            password="password123"
        )


#  Username too long
def test_user_schema_username_too_long():
    with pytest.raises(ValidationError):
        UserCreate(
            email="oleksandra@example.com",
            username="o" * 101,  # exceeds 100 char limit
            password="password123"
        )


#  Invalid role
def test_user_schema_invalid_role():
    with pytest.raises(ValidationError):
        UserCreate(
            email="oleksandra@example.com",
            username="oleksandra",
            role="superadmin",  # not in Enum
            password="password123"
        )


#  Valid partial update (UserUpdate)
def test_user_update_partial_data():
    update = UserUpdate(
        full_name="O. Kova",
        password="newsecurepassword"
    )
    assert update.full_name == "O. Kova"
    assert update.password == "newsecurepassword"


#  UserUpdate with invalid email format
def test_user_update_invalid_email_format():
    with pytest.raises(ValidationError):
        UserUpdate(
            email="bademail"
        )


#  UserUpdate with invalid role
def test_user_update_invalid_role():
    with pytest.raises(ValidationError):
        UserUpdate(
            role="god-mode"
        )
