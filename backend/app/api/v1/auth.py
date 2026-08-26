# auth_routes.py

"""
Authentication Routes Module.

This module contains FastAPI endpoints for user registration and login.
It handles password hashing and sets JWT authentication token securely via HTTP-only cookies.
"""

import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

import backend.app.core.auth as auth
from backend.app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import (
    GoogleTokenRequest,
    OIDCUserProfileGoogle,
    UserLogin,
    UserResponse,
    UserSignup,
)

IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
logger = logging.getLogger("fastapi_app")

router_auth = APIRouter(tags=["Authentication"])


@router_auth.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # existence verification
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"Signup failed: Email {user.email} already registered.")
        raise UserAlreadyExistsError("Email already registered")

    hashed_password = auth.get_password_hash(user.password)
    new_user = User(
        email=user.email, hashed_password=hashed_password, email_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {user.email}")
    return new_user


@router_auth.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    # OIDC user tries to log in using password
    if db_user and db_user.hashed_password is None:
        logger.warning(
            f"Login failed: {user.email} is an OIDC account attemtping password login",
        )
        raise InvalidCredentialsError(
            "Invalid Credentials. Log in using third party app."
        )

    if not db_user or not auth.verify_password(
        plain_password=user.password, hashed_password=db_user.hashed_password
    ):
        logger.warning(
            f"Login failed: Invalid credentials for {user.email}",
        )
        raise InvalidCredentialsError("Invalid credentials")

    db_user.last_login = datetime.now(timezone.utc)
    db.commit()

    # generate jwt token
    jwt_token = auth.create_access_token(
        {"sub": str(db_user.id), "role": db_user.role.value}
    )

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
    )
    logger.info(f"User logged in successfully: {user.email}")
    return {"message": "Login successful"}


@router_auth.post("/google")
def login_with_google(
    request_data: GoogleTokenRequest, response: Response, db: Session = Depends(get_db)
):
    try:
        # validate token against google servers
        idinfo = id_token.verify_oauth2_token(
            request_data.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )

        google_user = OIDCUserProfileGoogle(**idinfo)
    except ValueError:
        logger.warning("Google login failed: Invalid or expired Google token.")
        raise InvalidCredentialsError("Invalid or expired Google Token")

    # search if user already exists
    db_user = db.query(User).filter(User.email == google_user.email).first()

    if db_user:
        # if not db_user.is_active:
        #     raise InvalidCredentialsError("Account suspended")

        # --- ACCOUNT LINKING LOGIC ---
        if not db_user.oauth_id:
            db_user.oauth_provider = "google"
            db_user.oauth_id = google_user.oauth_id
            db_user.email_verified = google_user.email_verified
            logger.info(f"Linked Google account to existing user: {db_user.email}")

        if not db_user.avatar_url and google_user.avatar_url:
            db_user.avatar_url = google_user.avatar_url
        if not db_user.full_name and google_user.full_name:
            db_user.full_name = google_user.full_name
    else:
        # create new user via Google
        db_user = User(
            email=google_user.email,
            full_name=google_user.full_name,
            avatar_url=google_user.avatar_url,
            oauth_provider="google",
            oauth_id=google_user.oauth_id,
            email_verified=google_user.email_verified,
            hashed_password=None,
        )
        db.add(db_user)
        logger.info(f"New OIDC user registered: {db_user.email}")

    db_user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_user)

    jwt_token = auth.create_access_token(
        {"sub": str(db_user.id), "role": db_user.role.value}
    )

    response.set_cookie(
        key="access_token", value=jwt_token, httponly=True, secure=False, samesite="lax"
    )
    logger.info(f"OIDC User logged in successfully: {db_user.email}")
    return {"message": "Google Login successful"}
