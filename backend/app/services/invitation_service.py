# invitation_service.py
"""
Workspace invitation service module.

This module contains the business logic required for handling workspace
invitation related (db) operations.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    InvitationAlreadyExistsError,
    InvitationNotFoundError,
    InvitationNotPendingError,
    InvitationPermissionError,
    UserAlreadyInWorkspaceError,
    UserNotFoundError,
)
from backend.app.models.invitation import InvitationStatus, WorkspaceInvitation
from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceUser
from backend.app.schemas.invitation import InvitationCreate
from backend.app.services.workspace_service import _ensure_user_has_access

logger = logging.getLogger("fastapi_app")


def _get_invitation_or_404(
    db: Session, invitation_id: uuid.UUID
) -> WorkspaceInvitation:
    """Checks if invitation with 'invitation_id' exists, otherwise raise InvitationNotFoundError"""
    invitation: WorkspaceInvitation = db.get(WorkspaceInvitation, invitation_id)
    if not invitation:
        logger.warning(
            "Invitation does not exist.", extra={"invitation_id": invitation_id}
        )
        raise InvitationNotFoundError("The requested invitation does not exist.")
    return invitation


def create_invitation(
    workspace_id: uuid.UUID,
    invitation_data: InvitationCreate,
    db: Session,
    current_user_id: uuid.UUID,
) -> WorkspaceInvitation:
    _ensure_user_has_access(
        db,
        workspace_id,
        current_user_id,
        require_admin=True,
        log_msg="User is not authorized to invite members to workspace",
        error_msg="You are not authorized to invite members to this workspace.",
    )

    stmt_target_user = select(User).where(User.email == invitation_data.email)
    target_user = db.execute(stmt_target_user).scalar_one_or_none()
    if not target_user:
        logger.warning(
            "Attempted to invite a non-existing user",
            extra={"user_id": current_user_id, "invited_email": invitation_data.email},
        )
        raise UserNotFoundError("No user with this email was found.")

    stmt_check_member = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == target_user.id,
    )
    if db.execute(stmt_check_member).scalar_one_or_none():
        logger.warning(
            "Attempted to invite a user already in workspace",
            extra={"target_user_id": target_user.id, "workspace_id": workspace_id},
        )
        raise UserAlreadyInWorkspaceError(
            "The user you are trying to invite is already part of workspace."
        )

    stmt_check_pending = select(WorkspaceInvitation).where(
        WorkspaceInvitation.workspace_id == workspace_id,
        WorkspaceInvitation.invited_user_id == target_user.id,
        WorkspaceInvitation.status == InvitationStatus.pending,
    )
    if db.execute(stmt_check_pending).scalar_one_or_none():
        logger.warning(
            "Attempted to create a duplicate pending invitation",
            extra={"target_user_id": target_user.id, "workspace_id": workspace_id},
        )
        raise InvitationAlreadyExistsError()

    new_invitation = WorkspaceInvitation(
        workspace_id=workspace_id,
        invited_user_id=target_user.id,
        invited_by_user_id=current_user_id,
        role=invitation_data.role,
    )
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)

    logger.info(
        "User successfully invited to workspace",
        extra={
            "user_id": current_user_id,
            "target_user_id": target_user.id,
            "workspace_id": workspace_id,
        },
    )
    return new_invitation


def get_my_pending_invitations(
    db: Session, current_user_id: uuid.UUID
) -> list[WorkspaceInvitation]:
    stmt = select(WorkspaceInvitation).where(
        WorkspaceInvitation.invited_user_id == current_user_id,
        WorkspaceInvitation.status == InvitationStatus.pending,
    )
    invitations = list(db.execute(stmt).scalars().all())
    logger.info(
        "User successfully retrieved pending invitations",
        extra={"user_id": current_user_id, "invitation_count": len(invitations)},
    )
    return invitations


def _respond_to_invitation(
    invitation_id: uuid.UUID,
    db: Session,
    current_user_id: uuid.UUID,
    new_status: InvitationStatus,
) -> WorkspaceInvitation:
    invitation = _get_invitation_or_404(db, invitation_id)

    if invitation.invited_user_id != current_user_id:
        logger.warning(
            "User attempted to respond to an invitation not addressed to them",
            extra={"user_id": current_user_id, "invitation_id": invitation_id},
        )
        raise InvitationPermissionError()

    if invitation.status != InvitationStatus.pending:
        logger.warning(
            "User attempted to respond to a non-pending invitation",
            extra={"user_id": current_user_id, "invitation_id": invitation_id},
        )
        raise InvitationNotPendingError()

    invitation.status = new_status
    invitation.responded_at = datetime.now(timezone.utc)

    if new_status == InvitationStatus.accepted:
        new_member_link = WorkspaceUser(
            user_id=invitation.invited_user_id,
            workspace_id=invitation.workspace_id,
            role=invitation.role,
        )
        db.add(new_member_link)

    db.commit()
    db.refresh(invitation)

    logger.info(
        f"User successfully {new_status.value} invitation",
        extra={"user_id": current_user_id, "invitation_id": invitation_id},
    )
    return invitation


def accept_invitation(
    invitation_id: uuid.UUID, db: Session, current_user_id: uuid.UUID
) -> WorkspaceInvitation:
    return _respond_to_invitation(
        invitation_id, db, current_user_id, InvitationStatus.accepted
    )


def decline_invitation(
    invitation_id: uuid.UUID, db: Session, current_user_id: uuid.UUID
) -> WorkspaceInvitation:
    return _respond_to_invitation(
        invitation_id, db, current_user_id, InvitationStatus.declined
    )
