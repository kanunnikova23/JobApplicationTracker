from app.models import User
from datetime import datetime
from uuid import uuid4

USER_PREFIX = "users"


def test_read_applications_route(client):
    response = client.get("/users/")
    assert response.status_code == 200


def test_register_user(client):
    payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "securepass123"
    }
    response = client.post(f"{USER_PREFIX}/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


def test_register_duplicate_email(client, db):
    existing_user = User(
        id=str(uuid4()),
        email="dupe@example.com",
        username="dupeuser",
        full_name="Dupe User",
        hashed_password="hashed",
        created_at=datetime.now()
    )
    db.add(existing_user)
    db.commit()

    payload = {
        "email": "dupe@example.com",
        "username": "anotheruser",
        "full_name": "Another User",
        "password": "pass"
    }
    response = client.post(f"{USER_PREFIX}/register", json=payload)
    assert response.status_code == 409
    assert "Email" in response.json()["detail"]


def test_get_users(client):
    response = client.get(f"{USER_PREFIX}/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_by_id(client, db):
    user = User(
        id=str(uuid4()),
        email="idtest@example.com",
        username="iduser",
        full_name="ID User",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.get(f"{USER_PREFIX}/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_get_user_by_invalid_uuid(client):
    response = client.get(f"{USER_PREFIX}/invalid-uuid")
    assert response.status_code == 400
    assert "Invalid UUID" in response.json()["detail"]


def test_get_user_by_username(client, db):
    user = User(
        id=str(uuid4()),
        email="usertest@example.com",
        username="usertest",
        full_name="User Test",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()

    response = client.get(f"{USER_PREFIX}/username/{user.username}")
    assert response.status_code == 200
    assert response.json()["username"] == user.username


def test_update_user(client, db):
    user = User(
        id=str(uuid4()),
        email="updateuser@example.com",
        username="updateuser",
        full_name="Update User",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    update_payload = {
        "full_name": "Updated Name",
        "role": "admin"
    }
    response = client.put(f"{USER_PREFIX}/{user.id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    assert response.json()["role"] == "admin"


def test_delete_user(client, db):
    user = User(
        id=str(uuid4()),
        email="delete@example.com",
        username="deleteuser",
        full_name="Delete Me",
        hashed_password="hash",
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.delete(f"{USER_PREFIX}/{user.id}")
    assert response.status_code == 204

    # Confirm it's deleted
    get_response = client.get(f"{USER_PREFIX}/{user.id}")
    assert get_response.status_code == 404