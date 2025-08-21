from app import models
from app.auth.hashing import Hasher



def create_admin_and_get_token(client, db_session):
    hashed_pw = Hasher.get_password_hash("adminpass")
    admin = models.User(
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        password=hashed_pw,
        user_type="admin"
    )
    db_session.add(admin)
    db_session.commit()

    login_res = client.post("/login", json={
        "email": "admin@example.com",
        "password": "adminpass"
    })
    assert login_res.status_code == 200
    return login_res.json()["access_token"]


def test_create_product(client, db_session):
    token = create_admin_and_get_token(client, db_session)

    with open("tests/test_image.jpg", "wb") as f:
        f.write(b"fake image content")

    with open("tests/test_image.jpg", "rb") as img_file:
        res = client.post(
            "/products/",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "name": "Bottle",
                "description": "Steel bottle",
                "price": "99.99"
            },
            files={"image": ("test.jpg", img_file, "image/jpeg")}
        )

    assert res.status_code == 200
    assert res.json()["name"] == "Bottle"



def test_get_all_products(client, db_session):
    # Create a normal user
    hashed_pw = Hasher.get_password_hash("userpass")
    user = models.User(
        first_name="Normal",
        last_name="User",
        email="user@example.com",
        password=hashed_pw,
        user_type="normal"
    )
    db_session.add(user)
    db_session.commit()

    # Login
    login_res = client.post("/login", json={
        "email": "user@example.com",
        "password": "userpass"
    })
    token = login_res.json()["access_token"]

    res = client.get(
        "/products/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)



def test_register_user(client, db_session):
    # First create an admin
    token = create_admin_and_get_token(client, db_session)

    # Register a new normal user
    res = client.post(
        "/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "password123",
            "user_type": "normal"
        }
    )
    assert res.status_code in (200, 201)
    assert res.json()["email"] == "test@example.com"


def test_get_current_user(client, db_session):
    # Create normal user
    hashed_pw = Hasher.get_password_hash("password123")
    user = models.User(
        first_name="Me",
        last_name="User",
        email="me@example.com",
        password=hashed_pw,
        user_type="normal"
    )
    db_session.add(user)
    db_session.commit()

    # Login
    login_res = client.post("/login", json={
        "email": "me@example.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    # Get current user
    res = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"
