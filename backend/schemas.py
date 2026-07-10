# schemas.py
"""
Pydantic Schemas Module.

This module defines data validation models for incoming HTTP reqiests and response models used to serialize SQLAlchemy objects into secure JSON payloads.
"""

# TODO: change all id str with uuid ? application breaks ?
import re
import uuid
from datetime import datetime
from typing import Optional

from models.monitor import MonitorStatus
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


# output schemas ( what api/our server returns )
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # pydantic reads sqlalchemy

    id: uuid.UUID
    email: str
    role: str
    is_active: bool


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceUpdate(BaseModel):
    name: str


class MemberCreate(BaseModel):
    id: uuid.UUID
    role: str = "Viewer"


class WorkspaceReturn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class MonitorCreate(BaseModel):
    name: str
    url: str
    interval_minutes: int


class MonitorUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    interval_minutes: int | None = None
    status: MonitorStatus | None = None


class MonitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    url: str
    status: MonitorStatus
    interval_minutes: int
    created_at: datetime
    updated_at: datetime


class MonitorListResponse(BaseModel):
    monitors: list[MonitorResponse]


class MonitorBulkDelete(BaseModel):
    monitor_ids: list[uuid.UUID] = Field(
        ..., min_lenght=1, description="List of monitor ids to be deleted"
    )


# NOTE: a create model should include only fields that are given by frontend
# for the creation. if id and other fields are generated they do not need
# to be included
# however if there is a FK id, it is needed to be delivered from the frontend
# so it can be included in a Create Model
# but if its already in endpoint it becomes redundant in Create Model
