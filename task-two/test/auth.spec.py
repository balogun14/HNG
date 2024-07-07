from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_client():
    yield client

def test_register_user_success(test_client):
    response = test_client.post("/auth/register", json={
        "firstName": "awwal",
        "lastName": "balogun",
        "email": "awwal.balogun@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    assert response.status_code == 201
    assert response.json()["firstName"] == "awwal"

def test_login_user_success(test_client):
    response = test_client.post("/auth/login", data={
        "username": "awwal.balogun@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register_user_duplicate_email(test_client):
    response = test_client.post("/auth/register", json={
        "firstName": "awwal",
        "lastName": "balogun",
        "email": "awwal.balogun@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    assert response.status_code == 400

def test_get_organisations(test_client):
    response = test_client.get("/api/organisations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
