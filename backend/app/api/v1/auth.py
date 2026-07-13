# auth_routes.py

"""
Authentication Routes Module.

This module contains FastAPI endpoints for user registration and login.
It handles password hashing and sets JWT authentication token securely via HTTP-only cookies.
"""

import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

import backend.app.core.auth as auth
from backend.app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserLogin, UserResponse, UserSignup

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
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {user.email}")
    return new_user


@router_auth.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not auth.verify_password(
        plain_password=user.password, hashed_password=db_user.hashed_password
    ):
        logger.warning(f"Login failed: Invalid credentials for {user.email}.")
        raise InvalidCredentialsError("Invalid credentials")

    # generate jwt token
    jwt_token = auth.create_access_token(
        {"sub": str(db_user.id), "role": db_user.role.value}
    )

    response.set_cookie(
        key="access_token", value=jwt_token, httponly=True, secure=False, samesite="lax"
    )
    logger.info(f"User logged in successfully: {user.email}")
    return {"message": "Login successful"}
