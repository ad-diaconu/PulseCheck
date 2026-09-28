# invitation.py
"""
Workspace Invitation Routes Module.

This module contains FastAPI endpoints for sending and responding to
workspace invitations.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.auth import get_current_user_id
from backend.app.db.database import get_db
from backend.app.schemas.invitation import InvitationCreate, InvitationReturn
from backend.app.services import invitation_service

logger = logging.getLogger("fastapi_app")

router_workspace_invitation = APIRouter(
    prefix="/workspaces/{workspace_id}/invitations", tags=["Workspace Invitations"]
)
router_invitation = APIRouter(prefix="/invitations", tags=["Workspace Invitations"])


@router_workspace_invitation.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=InvitationReturn,
    summary="Invite an existing user to a workspace",
)
def create_invitation(
    workspace_id: uuid.UUID,
    invitation_data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    return invitation_service.create_invitation(
        workspace_id, invitation_data, db, current_user_id
    )


@router_invitation.get(
    "",
    response_model=list[InvitationReturn],
    summary="List the current user's pending invitations",
)
def get_my_pending_invitations(
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    return invitation_service.get_my_pending_invitations(db, current_user_id)


@router_invitation.post(
    "/{invitation_id}/accept",
    response_model=InvitationReturn,
    summary="Accept a workspace invitation",
)
def accept_invitation(
    invitation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    return invitation_service.accept_invitation(invitation_id, db, current_user_id)


@router_invitation.post(
    "/{invitation_id}/decline",
    response_model=InvitationReturn,
    summary="Decline a workspace invitation",
)
def decline_invitation(
    invitation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    return invitation_service.decline_invitation(invitation_id, db, current_user_id)
