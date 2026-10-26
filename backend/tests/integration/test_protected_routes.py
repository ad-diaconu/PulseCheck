# test_protected_routes.py
"""
Integration tests for protected routes.
"""

import pytest

from backend.app.models.user import User
from backend.app.services.verification_service import generate_and_store_code


def _signup_and_verify(client, db_session, payload):
    """Signs a user up and immediately verifies their email, the same way
    test_login_success in test_auth_routes.py does — login rejects
    unverified accounts, and most of these tests only care about what
    happens AFTER login, not about the verification flow itself."""
    client.post("/signup", json=payload)
    db_user = db_session.query(User).filter_by(email=payload["email"]).first()
    code = generate_and_store_code(db_user.id)
    client.post("/verify-email", json={"email": payload["email"], "code": code})


@pytest.mark.integration
@pytest.mark.protected
def test_protected_route_me_success(client, db_session, user_signup_payload):
    """Test /me route with cookie."""
    _signup_and_verify(client, db_session, user_signup_payload)
    client.post("/login", json=user_signup_payload)
    response = client.get("/me")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_signup_payload["email"]
    assert data["role"] == "standard_user"
    assert "id" in data


@pytest.mark.integration
@pytest.mark.protected
def test_protected_route_unauthorized(client):
    """Tests /me route with no cookie."""
    response = client.get("/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.integration
@pytest.mark.protected
def test_get_protected_users_success(
    client, db_session, user_signup_payload, seed_users
):
    _signup_and_verify(client, db_session, user_signup_payload)
    client.post("/login", json=user_signup_payload)
    response = client.get("/users")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 6

    assert "email" in data[2]
    assert "hashed_password" not in data[0]


@pytest.mark.integration
@pytest.mark.protected
def test_get_protected_users_unauthorized(client):
    response = client.get("/users")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.integration
@pytest.mark.protected
def test_logout_remove_cookie(client, db_session, user_signup_payload):
    """Tests if /login route successfully removes cookie."""
    _signup_and_verify(client, db_session, user_signup_payload)
    client.post("/login", json=user_signup_payload)

    response = client.post("/logout")
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Logged out"
    assert "access_token" not in response.cookies

    response_after_logout = client.get("/me")
    assert response_after_logout.status_code == 401
