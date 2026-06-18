# auth.py
"""
Authentication Utilities and Dependencies.

This module handles core security operations: bcrypt password hashing, JWT token encoding/decoding, JWT validation FastAPI dependency.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from exceptions import TokenError
from fastapi import Request

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM = "HS256"  # symmetric key


def get_password_hash(password: str) -> str:
    """Generates password hash using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=password.encode("utf-8"), salt=salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if user password corresponds with hashed password from database."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    """Creates a valid 1 hour duration JWT token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=1)
    to_encode.update({"exp": expire, "iat": now, "iss": "pulsecheck"})
    return jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)


# verify JWT
def get_current_user_payload(request: Request) -> None:
    """
    FastAPI Dependency used for extracting and validating JWT from cookie.
    Throws business logic errors (TokenError) in case of abnormalities.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise TokenError("No token provided.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise TokenError("Invalid token")
