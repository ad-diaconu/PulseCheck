# invitation.py
"""
Pydantic WorkspaceInvitation Schemas Module.

This module defines data validation models for the WorkspaceInvitation module.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "Viewer"


class InvitationReturn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    invited_user_id: uuid.UUID
    invited_by_user_id: uuid.UUID
    role: str
    status: str
    created_at: datetime
    responded_at: datetime | None = None


class InvitationWithEmail(InvitationReturn):
    invited_email: str


class InvitationWithContext(InvitationReturn):
    workspace_name: str
    invited_by_email: str
