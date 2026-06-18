# auth_routes.py

"""
Authentication Routes Module.

This module contains FastAPI endpoints for user registration and login.
It handles password hashing and sets JWT authentication token securely via HTTP-only cookies.
"""

import logging

import auth
from database import get_db
from exceptions import InvalidCredentialsError, UserAlreadyExist
from fastapi import APIRouter, Depends, Response, status
from models import User
from schemas import UserLogin, UserResponse, UserSignup
from sqlalchemy.orm import Session

logger = logging.getLogger("fastapi_app")

router_auth = APIRouter()


@router_auth.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # existence verification
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"Signup failed: Email {user.email} already registered.")
        # raise HTTPException(
        #     status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        # )
        raise UserAlreadyExist("Email already registered")

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
