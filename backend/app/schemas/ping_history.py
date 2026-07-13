# ping_history.py
"""
Pydantic PingHistory Schemas Module.

This module defines data validation models for PingHistory module."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PingHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: uuid.UUID
    pinged_at: datetime
    status_code: int
    latency_ms: float


class PingHistoryListResponse(BaseModel):
    pings: list[PingHistoryResponse]


# NOTE: a create model should include only fields that are given by frontend
# for the creation. if id and other fields are generated they do not need
# to be included
# however if there is a FK id, it is needed to be delivered from the frontend
# so it can be included in a Create Model
# but if its already in endpoint it becomes redundant in Create Model
