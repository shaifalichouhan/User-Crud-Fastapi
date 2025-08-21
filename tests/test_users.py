from app import models
from app.auth.hashing import Hasher
from .conftest import create_user, get_token

def test_register_user(client, db_session):
    response = client.post("/",
        json={
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password": "newpass123",
            "user_type": "normal"
        }
    )
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"

def test_login_user(client, db_session):
    create_user(db_session, "login@example.com", "password123")
    response = client.post("/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_current_user(client, db_session):
    user = create_user(db_session, "me@example.com", "password123")
    token = get_token(client, user.email, "password123")
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
