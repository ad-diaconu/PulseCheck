# monitor.py
"""
Pydantic Monitor Schemas Module.

This module defines data validation models for the Monitor module.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.monitor import MonitorStatus


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
        ..., min_length=1, description="List of monitor ids to be deleted"
    )
