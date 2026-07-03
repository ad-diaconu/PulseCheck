# conftest.py
"""
Global pyest fixtures and test database setup.
"""

import auth
import pytest
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models.user import User
from models.workspace import Workspace, WorkspaceUser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # RAM

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # same conexion for the test suite
)

TestingSessionLocal = sessionmaker(autocommit=False, bind=engine)


# --- AUTH ---
@pytest.fixture(scope="function")
def user_signup_payload():
    return {"email": "examplesfa23@example.com", "password": "MyPssword123"}


@pytest.fixture(scope="function")
def seed_users(db_session):
    """Inserts 5 users in test database."""
    users = []
    for i in range(5):
        hashed_pw = auth.get_password_hash("ParolaTest123!")
        user = User(email=f"testuser{i}@example.com", hashed_password=hashed_pw)
        users.append(user)
    db_session.add_all(users)
    db_session.commit()

    return users


# --- WORKSPACE ---
@pytest.fixture
def test_user(db_session):
    """
    Creates a standard user in test db.
    """
    hashed_password = auth.get_password_hash("Password1234!")
    user = User(email="owner@example.com", hashed_password=hashed_password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session):
    hashed_password = auth.get_password_hash("Password1234!")
    user = User(email="other_user@example.com", hashed_password=hashed_password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_client(client, test_user):
    """
    Authenticates 'test_user' which is saved in database.
    Token stored in TestClient's cookies.
    Returns an authenticated FastAPI TestClient.
    """
    payload = {"email": test_user.email, "password": "Password1234!"}
    client.post("/login", json=payload)
    return client


@pytest.fixture
def owned_workspace(db_session, test_user):
    """Creates an workspace where current user (test_user) is ADMIN."""
    workspace = Workspace(name="My Workspace")
    db_session.add(workspace)
    db_session.flush()

    link = WorkspaceUser(user_id=test_user.id, workspace_id=workspace.id, role="Admin")
    db_session.add(link)
    db_session.commit()
    db_session.refresh(workspace)
    return workspace


@pytest.fixture
def member_workspace(db_session, test_user, other_user):
    """Creates an workspace where test_user is ADMIN and other_user is member of workspace (VIEWER)."""
    workspace = Workspace(name="Shared Workspace (Member)")
    db_session.add(workspace)
    db_session.flush()

    link_admin = WorkspaceUser(
        user_id=test_user.id, workspace_id=workspace.id, role="Admin"
    )
    link_member = WorkspaceUser(
        user_id=other_user.id, workspace_id=workspace.id, role="Viewer"
    )
    db_session.add_all([link_admin, link_member])
    db_session.commit()
    db_session.refresh(workspace)
    return workspace


@pytest.fixture
def unauthorized_workspace(db_session, other_user):
    """
    Creates an workspace owned by other_user, where the current user does not have authorization for read/write operations.
    """
    workspace = Workspace(name="Forbidden Workspace")
    db_session.add(workspace)
    db_session.flush()

    link = WorkspaceUser(user_id=other_user.id, workspace_id=workspace.id, role="Admin")
    db_session.add(link)
    db_session.commit()
    db_session.refresh(workspace)
    return workspace


# --- CONFIG ---
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
