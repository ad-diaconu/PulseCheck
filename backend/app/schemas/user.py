# user.py
"""
Pydantic User Schemas Module.

This module defines data validation models for the User module.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class GoogleTokenRequest(BaseModel):
    credential: str


class OIDCUserProfileGoogle(BaseModel):
    """Pydantic schema for Google OIDC validation"""

    email: EmailStr
    full_name: str | None = Field(default=None, alias="name")
    avatar_url: str | None = Field(default=None, alias="picture")
    oauth_id: str = Field(alias="sub")
    email_verified: bool = False


# output schemas ( what api/our server returns )
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    full_name: str | None = None
    avatar_url: str | None = None
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None
