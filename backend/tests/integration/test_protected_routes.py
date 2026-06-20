# test_protected_routes.py
"""
Integration tests for protected routes.
"""

import pytest
from models import User

@pytest.mark.integration
@pytest.mark.protected
def test_protected_route_me_success(client,user_signup_payload):
    """Test /me route with cookie."""
    client.post("/signup",json=user_signup_payload)
    client.post("/login",json=user_signup_payload)
    response = client.get("/me")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Acessed secure data"
    assert "your_id" in data
    assert data["your_role"] == "standard_user"

@pytest.mark.integration
@pytest.mark.protected
def test_protected_route_unauthorized(client):
    """Tests /me route with no cookie."""
    response = client.get("/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.integration
@pytest.mark.protected
def test_get_protected_users_success(client,user_signup_payload,seed_users):
    client.post("/signup",json=user_signup_payload)
    client.post("/login",json=user_signup_payload)
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
def test_logout_remove_cookie(client,user_signup_payload):
    """Tests if /login route successfully removes cookie."""
    client.post("/signup",json=user_signup_payload)
    client.post("/login",json=user_signup_payload)

    response = client.post("/logout")
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Logged out"
    assert "access_token" not in response.cookies

    response_after_logout = client.get("/me")
    assert response_after_logout.status_code == 401