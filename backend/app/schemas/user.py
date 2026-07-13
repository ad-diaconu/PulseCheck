# user.py
"""
Pydantic User Schemas Module.

This module defines data validation models for the User module.
"""

import re
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# input schemas
class UserSignup(BaseModel):
    email: EmailStr  # built-in email validators
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a number")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# output schemas ( what api/our server returns )
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
