# test_auth_routes.py
"""
Integration tests for authentication routes.
"""

import pytest

from backend.app.models.user import User
from backend.app.services.verification_service import generate_and_store_code


@pytest.mark.integration
@pytest.mark.auth
def test_signup_success(client, db_session, user_signup_payload):

    response = client.post("/signup", json=user_signup_payload)
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
def test_signup_duplicate_email(client, user_signup_payload):
    """Tests reserving an already existing email to only one user."""
    client.post("/signup", json=user_signup_payload)
    response = client.post("/signup", json=user_signup_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.integration
@pytest.mark.auth
def test_login_success(client, db_session, user_signup_payload):
    """Tests complete flow of successful login, after email verification."""
    client.post("/signup", json=user_signup_payload)

    # login is blocked until the email is verified
    # verify it the same way a real user would,
    # through the actual service, not by poking the DB.
    db_user = (
        db_session.query(User).filter_by(email=user_signup_payload["email"]).first()
    )
    code = generate_and_store_code(db_user.id)
    client.post(
        "/verify-email", json={"email": user_signup_payload["email"], "code": code}
    )

    response = client.post("/login", json=user_signup_payload)
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
    client.post(
        "/signup", json={"email": "wrongpass@example.com", "password": "correct_pass"}
    )
    response = client.post(
        "/login", json={"email": "wrongpass@example.com", "password": "WRONG"}
    )

    if response.status_code != 401:
        print(response.json())
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.integration
@pytest.mark.auth
def test_login_blocked_until_email_verified(client, user_signup_payload):
    """A freshly signed-up (unverified) user cannot log in, even with the
    correct password."""
    client.post("/signup", json=user_signup_payload)

    response = client.post("/login", json=user_signup_payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "Please verify your email before logging in."
    assert "access_token" not in response.cookies


@pytest.mark.integration
@pytest.mark.auth
def test_verify_email_success(client, db_session, user_signup_payload):
    """A correct, unexpired code marks the account as verified."""
    client.post("/signup", json=user_signup_payload)
    db_user = (
        db_session.query(User).filter_by(email=user_signup_payload["email"]).first()
    )
    code = generate_and_store_code(db_user.id)

    response = client.post(
        "/verify-email", json={"email": user_signup_payload["email"], "code": code}
    )

    assert response.status_code == 200
    db_session.refresh(db_user)
    assert db_user.email_verified is True


@pytest.mark.integration
@pytest.mark.auth
def test_verify_email_wrong_code(client, user_signup_payload):
    """A wrong code is rejected and does not verify the account."""
    client.post("/signup", json=user_signup_payload)

    response = client.post(
        "/verify-email",
        json={"email": user_signup_payload["email"], "code": "000000"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification code."


@pytest.mark.integration
@pytest.mark.auth
def test_verify_email_locks_out_after_max_attempts(
    client, db_session, user_signup_payload
):
    """After 5 wrong guesses, even the correct code is rejected — the code
    is invalidated, forcing a resend instead of allowing more guesses."""
    client.post("/signup", json=user_signup_payload)
    db_user = (
        db_session.query(User).filter_by(email=user_signup_payload["email"]).first()
    )
    code = generate_and_store_code(db_user.id)

    wrong_payload = {"email": user_signup_payload["email"], "code": "000000"}
    for _ in range(5):
        response = client.post("/verify-email", json=wrong_payload)
        assert response.status_code == 400

    # the real code is now locked out too, even though it was never guessed
    response = client.post(
        "/verify-email", json={"email": user_signup_payload["email"], "code": code}
    )
    assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.auth
def test_resend_verification_invalidates_old_code(
    client, db_session, user_signup_payload
):
    """Resending replaces the stored code."""
    client.post("/signup", json=user_signup_payload)
    db_user = (
        db_session.query(User).filter_by(email=user_signup_payload["email"]).first()
    )
    old_code = generate_and_store_code(db_user.id)

    response = client.post(
        "/resend-verification", json={"email": user_signup_payload["email"]}
    )
    assert response.status_code == 200

    response = client.post(
        "/verify-email",
        json={"email": user_signup_payload["email"], "code": old_code},
    )
    assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.auth
def test_resend_verification_unknown_email_does_not_leak(client):
    """An unknown email gets the same generic response, so this endpoint
    can't be used to enumerate registered accounts."""
    response = client.post("/resend-verification", json={"email": "nobody@example.com"})

    assert response.status_code == 200
    assert "registered" in response.json()["message"]
