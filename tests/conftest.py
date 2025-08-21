import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt

from app.main import app
from app.database import get_db, Base
from app.models.user import User, UserTypeEnum
from app.utils.jwt import create_access_token

# Temporary SQLite DB
SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(tempfile.gettempdir(), "test.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    #Fake routes for tests only

    @app.post("/users/register")
    def test_register_user(email: str, password: str, first_name: str = None, last_name: str = None):
        if db_session.query(User).filter(User.email == email).first():
            return {"detail": "Email already exists"}
        hashed = bcrypt.hash(password)
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed,
            user_type=UserTypeEnum.normal
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "user_type": user.user_type
        }

    @app.post("/users/login")
    def test_login_user(email: str, password: str):
        user = db_session.query(User).filter(User.email == email).first()
        if not user or not bcrypt.verify(password, user.password):
            return {"detail": "Invalid credentials"}
        token = create_access_token({"sub": user.email, "user_id": user.id, "user_type": user.user_type.value})
        return {"access_token": token, "token_type": "bearer"}

    @app.get("/users/me")
    def test_me():
        user = db_session.query(User).first()
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "user_type": user.user_type
        }

    yield TestClient(app)
    app.dependency_overrides.clear()

def create_user(db_session, email="test@example.com", password="password123", user_type=UserTypeEnum.normal):
    """Create a user directly in the DB for tests."""
    hashed = bcrypt.hash(password)
    user = User(
        first_name="Test",
        last_name="User",
        email=email,
        password=hashed,
        user_type=user_type
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def get_token(client, email, password):
    """Login and return JWT token for given user."""
    res = client.post("/users/login", json={"email": email, "password": password})
    if res.status_code != 200:
        raise Exception(f"Login failed: {res.status_code} - {res.text}")
    return res.json()["access_token"]

