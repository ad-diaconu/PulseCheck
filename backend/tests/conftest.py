# conftest.py
"""
Global pyest fixtures and test database setup.
"""
import auth
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

from models import User

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" # RAM

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool # same conexion for the test suite
)

TestingSessionLocal = sessionmaker(autocommit=False, bind=engine)

@pytest.fixture(scope="function")
def user_signup_payload():
    return {"email":"examplesfa23@example.com","password":"MyPssword123"}

@pytest.fixture(scope="function")
def seed_users(db_session):
    """Inserts 5 users in test database."""
    users = []
    for i in range(5):
        hashed_pw = auth.get_password_hash("ParolaTest123!")
        user = User(email=f"testuser{i}@example.com",hashed_password=hashed_pw)
        users.append(user)
    db_session.add_all(users)
    db_session.commit()

    return users

@pytest.fixture(scope="function")
def db_session():
    """Creates tables before test and delete them afterwards."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Test client that mimics test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

   