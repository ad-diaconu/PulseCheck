# workspace.py
"""
Workspace service module.

This module contains the business logic required for handling workspace related (db) operations.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    AdminRemovalError,
    UserAlreadyInWorkspaceError,
    UserNotFoundError,
    WorkspaceCreationError,
    WorkspaceNotFoundError,
    WorkspacePermissionError,
)
from backend.app.models.user import User
from backend.app.models.workspace import Workspace, WorkspaceUser
from backend.app.schemas.workspace import (
    MemberCreate,
    WorkspaceCreate,
    WorkspaceUpdate,
)

logger = logging.getLogger("fastapi_app")


def _get_workspace_or_404(db: Session, workspace_id: uuid.UUID) -> Workspace:
    """Checks if workspace with 'workspace_id' exists, otherwise raise WorkspaceNotFoundError"""
    workspace: Workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(
            "Workspace does not exist.", extra={"workspace_id": workspace_id}
        )
        raise WorkspaceNotFoundError("The requested workspace does not exist.")
    return workspace


def _ensure_user_has_access(
    db: Session,
    workspace_id: uuid.UUID,
    current_user_id: uuid.UUID,
    require_admin: bool = False,
    log_msg: Optional[str] = None,
    error_msg: Optional[str] = None,
) -> WorkspaceUser:
    """Checks if user has access to workspace with 'workspace_id', otherwise raise WorkspacePermissionError"""
    stmt_check_access = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )

    if require_admin:
        stmt_check_access = stmt_check_access.where(WorkspaceUser.role == "Admin")

    workspace_user: WorkspaceUser = db.execute(stmt_check_access).scalar_one_or_none()
    if not workspace_user:
        logger.warning(
            log_msg
            or "Failed to retrieve workspace: user not authorized or workspace does not exist",
            extra={"user_id": current_user_id, "workspace_id": workspace_id},
        )
        raise WorkspacePermissionError(
            error_msg or "You do not have access to this workspace."
        )
    return workspace_user


def get_user_workspaces(
    db: Session,
    current_user_id: uuid.UUID,
):
    stmt_get_workspaces = (
        select(Workspace, WorkspaceUser.role)
        .join(WorkspaceUser, Workspace.id == WorkspaceUser.workspace_id)
        .where(WorkspaceUser.user_id == current_user_id)
    )
    workspaces: list[tuple[Workspace, str]] = db.execute(stmt_get_workspaces).all()
    logger.info(
        "User successfully retrieved workspaces",
        extra={"user_id": current_user_id, "workspace_count": len(workspaces)},
    )
    return workspaces
    # return [
    #     {"id": workspace.id, "name": workspace.name, "role": role}
    #     for workspace, role in workspaces
    # ]


def get_workspace_by_id(
    workspace_id: uuid.UUID,
    db: Session,
    current_user_id: uuid.UUID,
):
    stmt_check_access = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )
    workspace_user: WorkspaceUser = db.execute(stmt_check_access).scalar_one_or_none()
    if not workspace_user:
        logger.warning(
            "Failed to retrieve workspace: user not authorized or workspace does not exist",
            extra={"user_id": current_user_id, "workspace_id": workspace_id},
        )
        raise WorkspacePermissionError("You do not have access to this workspace.")
    workspace = db.get(Workspace, workspace_id)
    logger.info(
        "User successfully retrieved workspace",
        extra={
            "user_id": current_user_id,
            "workspace_name": workspace.name,
            "workspace_id": workspace.id,
        },
    )
    return workspace


def get_workspace_members(
    workspace_id: uuid.UUID,
    limit: int,
    offset: int,
    search: Optional[str],
    role: Optional[str],
    db: Session,
    current_user_id: uuid.UUID,
):
    stmt_check_access = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )
    if not db.execute(stmt_check_access).scalar_one_or_none():
        raise WorkspacePermissionError("You do not have access to this workspace.")

    stmt_members = (
        select(WorkspaceUser.role, User.email, User.id)
        .join(User, WorkspaceUser.user_id == User.id)
        .where(WorkspaceUser.workspace_id == workspace_id)
    )

    # search filtering
    if search:
        stmt_members = stmt_members.where(User.email.ilike(f"%{search}%"))

    # role filtering
    if role:
        stmt_members = stmt_members.where(WorkspaceUser.role == role)

    # offset and limit spagination
    stmt_members = stmt_members.offset(offset=offset).limit(limit=limit)

    results: list[tuple[str, str, uuid.UUID]] = db.execute(stmt_members).all()
    return results


def create_workspace(
    workspace_data: WorkspaceCreate, db: Session, current_user_id: uuid.UUID
):
    try:
        new_worskpace: Workspace = Workspace(name=workspace_data.name)
        db.add(new_worskpace)
        db.flush()

        workspace_link = WorkspaceUser(
            user_id=current_user_id,  # convert str user id into 16 bytes UUID user id
            workspace_id=new_worskpace.id,
            role="Admin",
        )
        db.add(workspace_link)
        db.commit()
        db.refresh(
            new_worskpace
        )  # reload instance to have all attrbiutes ready for return message

        logger.info(
            "User successfully created workspace",
            extra={
                "user_id": current_user_id,
                "workspace_name": new_worskpace.name,
                "workspace_id": new_worskpace.id,
            },
        )
        return new_worskpace
        # return {
        #     "message": "Workspace created successfully",
        #     "workspace": {
        #         "id": new_worskpace.id,
        #         "name": new_worskpace.name,
        #         "created_at": new_worskpace.created_at,
        #     },
        # }
    except Exception as e:
        # for any critical errors, cancel every transation
        db.rollback()
        logger.exception(
            "User failed to create workspace",
            extra={
                "user_id": current_user_id,
                "error": str(e),
            },
            exc_info=True,
        )
        raise WorkspaceCreationError(
            "Could not create workspace due to an internal server error."
        )


def add_member_to_workspace(
    workspace_id: uuid.UUID,
    member_data: MemberCreate,
    db: Session,
    current_user_id: uuid.UUID,
) -> None:
    workspace = _get_workspace_or_404(db, workspace_id)

    _ensure_user_has_access(
        db,
        workspace_id,
        current_user_id,
        require_admin=True,
        log_msg="User is not authorized to add members to workspace",
    )

    target_user = db.get(User, member_data.id)
    if not target_user:
        logger.warning(
            "User failed to add non-existing user into workspace",
            extra={
                "user_id": current_user_id,
                "target_user_id": member_data.id,
                "workspace_name": workspace.name,
                "workspace_id": workspace.id,
            },
        )
        raise UserNotFoundError("The user you are trying to add does not exist.")

    stmt_check_member = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == member_data.id,
    )
    existing_member = db.execute(stmt_check_member).scalar_one_or_none()
    if existing_member:
        logger.warning(
            "Target user is already part of workspace",
            extra={
                "target_user_id": target_user.id,
                "target_user_email": target_user.email,
                "workspace_name": workspace.name,
                "workspace_id": workspace.id,
            },
        )
        raise UserAlreadyInWorkspaceError(
            "The user you are trying to add is already part of workspace."
        )

    new_member_link = WorkspaceUser(
        user_id=member_data.id, workspace_id=workspace_id, role=member_data.role
    )
    db.add(new_member_link)
    db.commit()

    logger.info(
        "Workspace user successfully added new user into workspace.",
        extra={
            "user_id": current_user_id,
            "target_user_id": target_user.id,
            "target_user_email": target_user.email,
            "workspace_name": workspace.name,
            "workspace_id": workspace.id,
        },
    )
    # return {"message": "Member successfully added."}


def edit_workspace_name_by_workspace_id(
    workspace_id: uuid.UUID,
    workspace_data: WorkspaceUpdate,
    db: Session,
    current_user_id: uuid.UUID,
) -> Workspace:

    workspace = _get_workspace_or_404(db, workspace_id)

    stmt_check_admin = select(WorkspaceUser).where(
        WorkspaceUser.role == "Admin",
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )
    current_user_link = db.execute(stmt_check_admin).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            "User is not authorized to edit workspaces.",
            extra={"user_id": current_user_id},
        )
        raise WorkspacePermissionError("You are not authorized to edit this workspace.")

    # workspace_user(s) are linked by id so no junction table logic needed.
    # the industry standard is to return 200 status code along with only the newly created object
    # entirely omitting additional message "Workspace name changed successfully."

    workspace.name = workspace_data.name
    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace_by_id(
    workspace_id: uuid.UUID,
    db: Session,
    current_user_id: uuid.UUID,
) -> None:
    workspace = _get_workspace_or_404(db, workspace_id)

    stmt_check_admin = select(WorkspaceUser).where(
        WorkspaceUser.role == "Admin",
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )
    current_user_link = db.execute(stmt_check_admin).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            "User is not authorized to delete workspaces.",
            extra={"user_id": current_user_id},
        )
        raise WorkspacePermissionError(
            "You are not authorized to delete this workspace."
        )
    db.delete(workspace)
    db.commit()
    logger.info(
        "User successfully deleted workspace.",
        extra={"user_id": current_user_id, "workspace_id": workspace_id},
    )
    # return {"message": "Workspace successfully deleted."}


def leave_workspace(
    workspace_id: uuid.UUID,
    db: Session,
    current_user_id: uuid.UUID,
):
    workspace: Workspace = _get_workspace_or_404(db, workspace_id)

    stmt_retrieve_user = select(WorkspaceUser).where(
        WorkspaceUser.user_id == current_user_id,
        WorkspaceUser.workspace_id == workspace_id,
    )
    current_user_link = db.execute(stmt_retrieve_user).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            "User does not exist in workspace",
            extra={"user_id": current_user_id, "workspace_id": workspace_id},
        )
        raise UserNotFoundError("You are not a member of this workspace.")

    if current_user_link.role == "Admin":
        logger.warning(
            "User attempted to remove an admin", extra={"user_id": current_user_id}
        )
        raise AdminRemovalError("Admins cannot leave the workspace.")

    db.delete(current_user_link)
    db.commit()
    logger.info(
        "User successfully left workspace",
        extra={"user_id": {current_user_id}, "workspace_id": {workspace_id}},
    )
    # return {"message": "You have successfully left the workspace."}


def delete_member_from_workspace(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    db: Session,
    current_user_id: uuid.UUID,
):
    workspace = _get_workspace_or_404(db, workspace_id)
    stmt_check_admin = select(WorkspaceUser).where(
        WorkspaceUser.user_id == current_user_id,
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.role == "Admin",
    )
    current_user_link = db.execute(stmt_check_admin).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            "User not authorized to delete workspaces",
            extra={"user_id": current_user_id},
        )
        raise WorkspacePermissionError(
            "You are not authorized to delete this workspace."
        )
    stmt_target_member = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == member_id,
    )
    target_member_link = db.execute(stmt_target_member).scalar_one_or_none()
    if not target_member_link:
        logger.warning(
            "Failed to remove member user from workspace",
            extra={"target_user_id": member_id, "workspace_id": workspace_id},
        )
        raise UserNotFoundError("The specified user is not a member of this workspace.")
    if target_member_link.role == "Admin":
        logger.warning(
            "User attempted to remove an Admin",
            extra={"user_id": current_user_id, "target_user_id": member_id},
        )
        raise AdminRemovalError("Admins cannot be removed from the workspace.")

    db.delete(target_member_link)
    db.commit()
    logger.info(
        "User successfully deleted member user from workspace",
        extra={
            "user_id": current_user_id,
            "target_user_id": member_id,
            "workspace_id": workspace_id,
        },
    )
    # return {"message": "Member successfully removed from workspace."}
