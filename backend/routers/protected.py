# protected_routes.py
"""
Protected Routes Module.

This module contains FastAPI endpoints that require a valid authentication token to access.
"""

import logging

from auth import get_current_user_payload
from database import get_db
from fastapi import APIRouter, Depends
from models import User
from schemas import UserResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger("fastapi_app")

router_protected = APIRouter()


@router_protected.get("/me")
def get_protected_profile(payload: dict = Depends(get_current_user_payload)):
    logger.info(f"User {payload.get('sub')} accessed protected profile route.")
    return {
        "message": "Acessed secure data",
        "your_id": payload.get("sub"),
        "your_role": payload.get("role"),
    }


@router_protected.get("/users", response_model=list[UserResponse])
def get_protected_users(
    payload: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)
):
    logger.info(f"User {payload.get('sub')} fetched the complete users list.")
    db_users = db.scalars(select(User)).all()
    return db_users
