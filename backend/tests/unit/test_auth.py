"""
Unit tests for the authentication module.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest

from backend.app.core.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_current_user_payload,
    get_password_hash,
    verify_password,
)
from backend.app.core.exceptions import TokenError


def test_password_hashing():
    """Test that password hashes are generated correctly and verify successfully."""
    plain_password = "super_secret_passowrd_123"

    hashed = get_password_hash(plain_password)

    assert hashed != plain_password
    assert verify_password(plain_password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


@patch("auth.bcrypt.hashpw")
@patch("auth.bcrypt.gensalt")
def test_password_hash_data_transofrmations(mock_gensalt, mock_hashpw):
    mock_gensalt.return_value = b"fake_salt_bytes"
    mock_hashpw.return_value = b"fake_hashed_password_bytes"

    plain_password = "super_password"
    result = get_password_hash(plain_password)
    mock_hashpw.assert_called_once_with(
        password=b"super_password", salt=b"fake_salt_bytes"
    )

    assert result == "fake_hashed_password_bytes"
    assert isinstance(result, str)


@pytest.mark.jwt
def test_create_access_token():
    """Test that the JWT token is created with the correct payload and expiration."""
    data = {"sub": "user_id_123", "role": "admin"}
    token = create_access_token(data)

    assert isinstance(token, str)

    decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded_payload["sub"] == "user_id_123"
    assert decoded_payload["role"] == "admin"
    assert decoded_payload["iss"] == "pulsecheck"
    assert "exp" in decoded_payload
    assert "iat" in decoded_payload


@pytest.mark.jwt
def test_get_current_user_payload():
    """Test the FastAPI dependency successfully extract payload from a valid cookie."""

    # arrange
    valid_token = create_access_token({"sub": "user_id_123"})
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = valid_token

    # act
    payload = get_current_user_payload(mock_request)

    # assert
    assert payload["sub"] == "user_id_123"


@pytest.mark.jwt
def test_get_current_user_payload_no_token():
    """Test the dependency raises TokenError when cookie is missing."""
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = None

    with pytest.raises(TokenError, match="No token provided."):
        get_current_user_payload(mock_request)


@pytest.mark.jwt
def test_get_current_user_payload_invalid_token():
    """Test the dependency raises TokenError when token is tampered/invalid."""
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = "invalid.cookie.token.string"

    with pytest.raises(TokenError, match="Invalid token"):
        get_current_user_payload(mock_request)


@pytest.mark.jwt
def test_get_current_user_payload_expired_token():
    """Test the dependency raises TokenError when token is expired."""
    expired_payload = {"sub": "user_id_123", "exp": datetime.now(timezone.utc)}
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    mock_request = MagicMock()
    mock_request.cookies.get.return_value = expired_token

    with pytest.raises(TokenError, match="Token has expired"):
        get_current_user_payload(mock_request)
