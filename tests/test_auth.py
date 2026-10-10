import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models.user import User


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_register_user_successfully(client):
    response = client.post(
        "/register",
        json={
            "name": "Test Owner",
            "email": "OWNER@example.com",
            "password": "SecurePass123",
            "role": "business_owner",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"
    assert response.json()["role"] == "business_owner"

    db_override = app.dependency_overrides[get_db]
    db = next(db_override())
    try:
        user = db.query(User).filter_by(
            email="owner@example.com"
        ).first()

        assert user is not None
        assert user.hashed_password != "SecurePass123"
        assert bcrypt.checkpw(
            b"SecurePass123",
            user.hashed_password.encode("utf-8"),
        )
    finally:
        db.close()


def test_register_duplicate_email_is_rejected(client):
    payload = {
        "name": "Test Owner",
        "email": "owner@example.com",
        "password": "SecurePass123",
        "role": "business_owner",
    }

    first_response = client.post("/register", json=payload)
    second_response = client.post("/register", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "This profile is already registered."
    )


def test_register_invalid_role_is_rejected(client):
    response = client.post(
        "/register",
        json={
            "name": "Test Owner",
            "email": "owner@example.com",
            "password": "SecurePass123",
            "role": "unsupported_role",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid business role."


def test_login_successfully_returns_token(client):
    client.post(
        "/register",
        json={
            "name": "Test Owner",
            "email": "owner@example.com",
            "password": "SecurePass123",
            "role": "business_owner",
        },
    )

    response = client.post(
        "/login",
        json={
            "email": "OWNER@example.com",
            "password": "SecurePass123",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "business_owner"
    assert response.json()["access_token"]


def test_login_with_wrong_password_is_rejected(client):
    client.post(
        "/register",
        json={
            "name": "Test Owner",
            "email": "owner@example.com",
            "password": "SecurePass123",
            "role": "business_owner",
        },
    )

    response = client.post(
        "/login",
        json={
            "email": "owner@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_unknown_email_is_rejected(client):
    response = client.post(
        "/login",
        json={
            "email": "unknown@example.com",
            "password": "SecurePass123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_inactive_user_cannot_login(client):
    client.post(
        "/register",
        json={
            "name": "Test Owner",
            "email": "owner@example.com",
            "password": "SecurePass123",
            "role": "business_owner",
        },
    )

    db_override = app.dependency_overrides[get_db]
    db = next(db_override())
    try:
        user = db.query(User).filter_by(
            email="owner@example.com"
        ).first()
        assert user is not None
        user.is_active = False
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/login",
        json={
            "email": "owner@example.com",
            "password": "SecurePass123",
        },
    )

    assert response.status_code == 401

@pytest.mark.parametrize(
    "role",
    [
        "business_owner",
        "store_manager",
        "sales_executive",
        "admin",
    ],
)
def test_all_supported_roles_can_register_and_login(client, role):
    email = f"{role}@example.com"
    password = "SecurePass123"

    registration = client.post(
        "/register",
        json={
            "name": role.replace("_", " ").title(),
            "email": email,
            "password": password,
            "role": role,
        },
    )

    assert registration.status_code == 200
    assert registration.json()["role"] == role

    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200
    assert login_response.json()["role"] == role
    assert login_response.json()["access_token"]
