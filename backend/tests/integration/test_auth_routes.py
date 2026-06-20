# test_auth_routes.py
"""
Integration tests for authentication routes.
"""

import pytest
from models import User
from schemas import UserSignup

@pytest.mark.integration
@pytest.mark.auth
def test_signup_success(client,db_session,user_signup_payload):
   
    response = client.post("/signup",json=user_signup_payload)
    if response.status_code != 201:
        print(response.json())
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_signup_payload["email"]
    assert "id" in data
    assert "hashed_password" not in data
    
    user_in_db = db_session.query(User).filter(User.id == data["id"]).first()
    assert user_in_db is not None, "User not saved in database."
    assert user_in_db.email == user_signup_payload["email"]
    assert user_in_db.hashed_password != user_signup_payload["password"]
    assert user_in_db.hashed_password is not None


@pytest.mark.integration
@pytest.mark.auth
def test_signup_duplicate_email(client,user_signup_payload):
    """Tests reserving an already existing email to only one user."""
    client.post("/signup",json=user_signup_payload)
    response = client.post("/signup",json=user_signup_payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

# @pytest.mark.integration
# @pytest.mark.auth
# def test_login_success_sets_cookie(client,user_signup_payload):
#     client.post("/signup",json=user_signup_payload)
#     response = client.post("/login",json=user_signup_payload)
#     assert response.status_code == 200
#     assert "access_token" in response.cookies

@pytest.mark.integration
@pytest.mark.auth
def test_login_success(client,user_signup_payload):
    """Tests complete flow of successful login."""
    client.post("/signup",json=user_signup_payload)
    response = client.post("/login",json=user_signup_payload)
    data = response.json()
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    assert data["message"] == "Login successful"
    assert "access_token" in response.cookies

@pytest.mark.integration
@pytest.mark.auth
def test_login_invalid_credentials(client):
    """Tests if login rejects a wrong password."""
    client.post("/signup", json={"email": "wrongpass@example.com", "password": "correct_pass"})
    response = client.post("/login", json={"email": "wrongpass@example.com", "password": "WRONG"})
    
    if response.status_code != 401:
        print(response.json())
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"