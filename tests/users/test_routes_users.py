import pytest

from app.models import User
from datetime import datetime
from uuid import uuid4

USER_PREFIX = "users"


@pytest.mark.anyio
async def test_read_applications_route(async_client):
    response = await async_client.get("/users/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_register_user(async_client):
    payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "securepass123"
    }
    response = await async_client.post(f"{USER_PREFIX}/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


@pytest.mark.anyio
async def test_register_duplicate_email(async_client, db_session):
    existing_user = User(
        id=str(uuid4()),
        email="dupe@example.com",
        username="dupeuser",
        full_name="Dupe User",
        hashed_password="hashed",
        created_at=datetime.now()
    )
    db_session.add(existing_user)
    await db_session.commit()

    payload = {
        "email": "dupe@example.com",
        "username": "anotheruser",
        "full_name": "Another User",
        "password": "pass"
    }
    response = await async_client.post(f"{USER_PREFIX}/register", json=payload)
    assert response.status_code == 409
    assert "Email" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_users(async_client):
    response = await async_client.get(f"{USER_PREFIX}/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_user_by_id(async_client, db_session):
    user = User(
        id=str(uuid4()),
        email="idtest@example.com",
        username="iduser",
        full_name="ID User",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await async_client.get(f"{USER_PREFIX}/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == user.email


@pytest.mark.anyio
async def test_get_user_by_invalid_uuid(async_client):
    response = await async_client.get(f"{USER_PREFIX}/invalid-uuid")
    assert response.status_code == 400
    assert "Invalid UUID" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_user_by_username(async_client, db_session):
    user = User(
        id=str(uuid4()),
        email="usertest@example.com",
        username="usertest",
        full_name="User Test",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f"{USER_PREFIX}/username/{user.username}")
    assert response.status_code == 200
    assert response.json()["username"] == user.username


@pytest.mark.anyio
async def test_update_user(async_client, db_session):
    user = User(
        id=str(uuid4()),
        email="updateuser@example.com",
        username="updateuser",
        full_name="Update User",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    update_payload = {
        "full_name": "Updated Name",
        "role": "admin"
    }
    response = await async_client.put(f"{USER_PREFIX}/{user.id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    assert response.json()["role"] == "admin"


@pytest.mark.anyio
async def test_delete_user(async_client, db_session):
    user = User(
        id=str(uuid4()),
        email="delete@example.com",
        username="deleteuser",
        full_name="Delete Me",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await async_client.delete(f"{USER_PREFIX}/{user.id}")
    assert response.status_code == 204

    # Confirm it's deleted
    get_response = await async_client.get(f"{USER_PREFIX}/{user.id}")
    assert get_response.status_code == 404
