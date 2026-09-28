# protected_routes.py
"""
Protected Routes Module.

This module contains FastAPI endpoints that require a valid authentication token to access.
"""

import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.auth import get_current_user_payload
from backend.app.core.exceptions import UserNotFoundError
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserResponse

logger = logging.getLogger("fastapi_app")

router_protected = APIRouter(tags=["Protected Routes"])


@router_protected.get("/me", response_model=UserResponse)
def get_protected_profile(
    payload: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)
):
    user_id = uuid.UUID(payload.get("sub"))
    db_user = db.get(User, user_id)
    if not db_user:
        logger.warning(f"User {user_id} not found for /me lookup.")
        raise UserNotFoundError("User not found.")

    logger.info(f"User {user_id} accessed protected profile route.")
    return db_user


@router_protected.get("/users", response_model=list[UserResponse])
def get_protected_users(
    payload: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)
):
    logger.info(f"User {payload.get('sub')} fetched the complete users list.")
    db_users = db.scalars(select(User)).all()
    return db_users
