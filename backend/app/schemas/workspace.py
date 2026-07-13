# workspace.py
"""
Pydantic Workspace Schemas Module.

This module defines data validation models for the Workspace module.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
