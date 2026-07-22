# conftest.py
"""
Global pyest fixtures and test database setup.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app.core.auth as auth
from backend.app.db.database import Base, get_db
from backend.app.main import app
from backend.app.models.monitor import Monitor, MonitorStatus
from backend.app.models.ping_history import PingHistory
from backend.app.models.user import User
from backend.app.models.workspace import Workspace, WorkspaceUser

POSTGRESQL_DATABASE_URL = (
    "postgresql://test_user:test_password@localhost:5433/test_db"  # RAM
)

# --- CONFIG ---


@pytest.fixture(scope="session")
def engine():

    engine = create_engine(POSTGRESQL_DATABASE_URL)

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Createst tables before test and delete them afterwards.
    Executed before each test function. Offers isolation through transaction rollback.
    """
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session  # here the test function will run

    # after test function, rollback the transaction and close the session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Test client that mimics test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


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


# --- MONITOR ---
@pytest.fixture
def viewer_client(client, other_user):
    """
    Authenticates 'other_user' which is a Viewer in member_workspace.
    """
    payload = {"email": other_user.email, "password": "Password1234!"}
    client.post("/login", json=payload)
    return client


@pytest.fixture
def sample_monitor(db_session, owned_workspace) -> Monitor:
    """
    Creates a sample monitor in the test_user's owned workspace.
    """
    monitor: Monitor = Monitor(
        workspace_id=owned_workspace.id,
        name="Test API Monitor",
        url="https://api.example.com/health",
        interval_minutes=5,
        status=MonitorStatus.pending.value,
    )
    db_session.add(monitor)
    db_session.commit()
    db_session.refresh(monitor)
    return monitor


@pytest.fixture
def unauthorized_monitor(db_session, unauthorized_workspace) -> Monitor:
    """
    Creates a monitor in a workspace the test_user does not have access to.
    """
    monitor: Monitor = Monitor(
        workspace_id=unauthorized_workspace.id,
        name="Secret Monitor",
        url="https://secret.example.com",
        interval_minutes=10,
        status=MonitorStatus.up.value,
    )
    db_session.add(monitor)
    db_session.commit()
    db_session.refresh(monitor)
    return monitor


# --- PING_HISTORY ---
@pytest.fixture
def sample_ping_history(db_session, sample_monitor):
    """Test History Table Fixture"""
    pings = [
        PingHistory(
            monitor_id=sample_monitor.id,
            status_code=200,
            latency_ms=150,
        ),
        PingHistory(
            monitor_id=sample_monitor.id,
            status_code=500,
            latency_ms=800,
        ),
    ]
    db_session.add_all(pings)
    db_session.commit()
    for ping in pings:
        db_session.refresh(ping)
    return pings
