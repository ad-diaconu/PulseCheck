# workspace.py
"""
Workspace module.

This module contains FastAPI endpoints for handling workspace related routes.
"""

import logging
import uuid
from typing import Optional

from auth import get_current_user_id
from database import get_db
from exceptions import (
    AdminCantBeRemoved,
    UserAlreadyInWorkspace,
    UserNotFound,
    WorkspaceCreationError,
    WorkspaceNoAuthorization,
    WorkspaceNotFound,
)
from fastapi import APIRouter, Depends, Query, status
from models.user import User
from models.workspace import Workspace, WorkspaceUser
from schemas import MemberCreate, WorkspaceCreate, WorkspaceReturn, WorkspaceUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger("fastapi_app")

workspace_router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@workspace_router.get("", summary="Get all user workspaces")
def get_user_workspaces(
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    stmt_get_workspaces = (
        select(Workspace, WorkspaceUser.role)
        .join(WorkspaceUser, Workspace.id == WorkspaceUser.workspace_id)
        .where(WorkspaceUser.user_id == current_user_id)
    )
    workspaces: list[Workspace] = db.execute(stmt_get_workspaces).all()
    logger.info(
        f"User with ID '{current_user_id}' successfully retrieved {len(workspaces)} workspaces."
    )
    return [
        {"id": workspace.id, "name": workspace.name, "role": role}
        for workspace, role in workspaces
    ]


@workspace_router.get(
    "/{workspace_id}",
    response_model=WorkspaceReturn,
    summary="Get workspace details by ID",
)
def get_workspace_by_id(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    stmt_check_access = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )
    workspace_user: WorkspaceUser = db.execute(stmt_check_access).scalar_one_or_none()
    if not workspace_user:
        logger.warning(
            f"User '{current_user_id}' is unauthorized or workspace '{workspace_id}' does not exist."
        )
        raise WorkspaceNoAuthorization("You do not have access to this workspace.")
    workspace = db.get(Workspace, workspace_id)
    logger.info(
        f"User with ID '{current_user_id}' successfully retrieved workspace '{workspace.id} - {workspace.name}'."
    )
    return workspace


@workspace_router.get("/{workspace_id}/members", summary="List workspace members")
def get_workspace_members(
    workspace_id: uuid.UUID,
    limit: int = Query(
        50, ge=1, le=100, description="Number of fetched users (max 100)"
    ),
    offset: int = Query(
        0, ge=0, description="How many users to skip starting from beggining"
    ),
    search: Optional[str] = Query(None, description="Filter users by email"),
    role: Optional[str] = Query(None, description="Filter users by role"),
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    stmt_check_access = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )
    if not db.execute(stmt_check_access).scalar_one_or_none():
        raise WorkspaceNoAuthorization("You do not have access to this workspace.")

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

    results = db.execute(stmt_members).all()

    return [
        {"user_id": user_id, "email": email, "role": user_role}
        for user_role, email, user_id in results
    ]


@workspace_router.post(
    "", status_code=status.HTTP_201_CREATED, summary="Create a new workspace"
)
def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    try:
        new_worskpace = Workspace(name=workspace_data.name)
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
            f"User {current_user_id} successfully created workspace '{new_worskpace.id} - {new_worskpace.name}'"
        )
        return {
            "message": "Workspace created successfully",
            "workspace": {
                "id": new_worskpace.id,
                "name": new_worskpace.name,
                "created_at": new_worskpace.created_at,
            },
        }
    except Exception as e:
        # for any critical errors, cancel every transation
        db.rollback()
        logger.exception(
            f"Faield to create workspace for user {current_user_id}. Error:{str(e)}",
            exc_info=True,
        )
        raise WorkspaceCreationError(
            "Could not create workspace due to an internal server error."
        )


@workspace_router.post(
    "/{workspace_id}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to an existing workspace.",
)
def add_member_to_workspace(
    workspace_id: uuid.UUID,
    member_data: MemberCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(f"Workspace with ID'{workspace_id}' does not exist.")
        raise WorkspaceNotFound("The requested workspace does not exist.")

    stmt_check_admin = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
        WorkspaceUser.role == "Admin",
    )
    current_user_link = db.execute(stmt_check_admin).scalar_one_or_none()

    # NOTE: might change this exception name into a more 'logical' one
    if not current_user_link:
        logger.warning(
            f"User '{current_user_id}' (Admin check failed) is unauthorized to add members to workspace."
        )
        raise WorkspaceNoAuthorization(
            "You are not authorized to add members to this workspace."
        )

    target_user = db.get(User, member_data.id)
    if not target_user:
        logger.warning(
            f"User '{current_user_id}' tried to add non-existent user '{member_data.user_id}' into workspace '{workspace.id} - {workspace.name}'."
        )
        raise UserNotFound("The user you are trying to add does not exist.")

    stmt_check_member = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == member_data.id,
    )
    existing_member = db.execute(stmt_check_member).scalar_one_or_none()
    if existing_member:
        logger.warning(
            f"User '{target_user.id} - {target_user.email}' is already part of '{workspace.id} - {workspace.name}' workspace."
        )
        raise UserAlreadyInWorkspace(
            "The user you are trying to add is already part of workspace."
        )

    new_member_link = WorkspaceUser(
        user_id=member_data.id, workspace_id=workspace_id, role=member_data.role
    )
    db.add(new_member_link)
    db.commit()

    logger.info(
        f"Member with ID '{get_current_user_id}' successfully added user '{target_user.id} - {target_user.email}' into workspace '{workspace.id} - {workspace.name}."
    )
    return {"message": "Member successfully added."}


@workspace_router.patch("/{workspace_id}", summary="Update workspace details")
def edit_workspace_name_by_workspace_id(
    workspace_id: uuid.UUID,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    # workspace exists
    workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(f"Workspace with ID'{workspace_id}' does not exist.")
        raise WorkspaceNotFound("The requested workspace does not exist.")

    # user has role
    stmt_check_admin = select(WorkspaceUser).where(
        WorkspaceUser.user_id == current_user_id,
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.role == "Admin",
    )
    current_user_link = db.execute(stmt_check_admin).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            f"User '{current_user_id}' (Admin check failed) is unauthorized to edit workspace."
        )
        raise WorkspaceNoAuthorization("You are not authorized to edit this workspace.")

    # workspace_user(s) are linked by id so no junction table logic needed.
    workspace.name = workspace_data.name
    db.commit()
    db.refresh(workspace)
    return {
        "message": "Workspace name changed successfully.",
        "new_name": workspace.name,
    }


@workspace_router.delete("/{workspace_id}", summary="Delete a workspace")
def delete_workspace_by_id(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(f"Workspace with ID'{workspace_id}' does not exist.")
        raise WorkspaceNotFound("The requested workspace does not exist.")

    stmt_check_admin = select(WorkspaceUser).where(
        WorkspaceUser.role == "Admin",
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user_id,
    )
    current_user_link = db.execute(stmt_check_admin).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            f"User '{current_user_id}' (Admin check failed) is unauthorized to delete workspaces."
        )
        raise WorkspaceNoAuthorization(
            "You are not authorized to delete this workspace."
        )
    db.delete(workspace)
    db.commit()
    logger.info(
        f"User with ID '{current_user_id}' successfully deleted workspace with ID '{workspace_id}'."
    )
    return {"message": "Workspace successfully deleted."}


@workspace_router.delete("/{workspace_id}/leave", summary="Leave a workspace")
def leave_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(f"Workspace with ID'{workspace_id}' does not exist.")
        raise WorkspaceNotFound("The requested workspace does not exist.")

    stmt_retrieve_user = select(WorkspaceUser).where(
        WorkspaceUser.user_id == current_user_id,
        WorkspaceUser.workspace_id == workspace_id,
    )
    current_user_link = db.execute(stmt_retrieve_user).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            f"User 'with ID {current_user_id}' is not in workspace with ID '{workspace_id}'."
        )
        raise UserNotFound("You are not a member of this workspace.")

    if current_user_link.role == "Admin":
        logger.warning(f"User '{current_user_id}' attempted to remove an Admin.")
        raise AdminCantBeRemoved("Admins cannot leave the workspace.")

    db.delete(current_user_link)
    db.commit()
    logger.info(
        f"User with ID '{current_user_id}' successfully left workspace with ID '{workspace_id}'."
    )
    return {"message": "You have successfully left the workspace."}


@workspace_router.delete(
    "/{workspace_id}/{member_id}", summary="Remove a member from workspace"
)
def delete_member_from_workspace(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(f"Workspace with ID'{workspace_id}' does not exist.")
        raise WorkspaceNotFound("The requested workspace does not exist.")
    stmt_check_admin = select(WorkspaceUser).where(
        WorkspaceUser.user_id == current_user_id,
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.role == "Admin",
    )
    current_user_link = db.execute(stmt_check_admin).scalar_one_or_none()
    if not current_user_link:
        logger.warning(
            f"User '{current_user_id}' (Admin check failed) is unauthorized to delete workspaces."
        )
        raise WorkspaceNoAuthorization(
            "You are not authorized to delete this workspace."
        )
    stmt_target_member = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == member_id,
    )
    target_member_link = db.execute(stmt_target_member).scalar_one_or_none()
    if not target_member_link:
        logger.warning(
            f"Failed to remove member: User '{member_id}' is not in workspace '{workspace_id}'."
        )
        raise UserNotFound("The specified user is not a member of this workspace.")
    if target_member_link.role == "Admin":
        logger.warning(
            f"User {current_user_id} attempted to remove an Admin ({member_id})."
        )
        raise AdminCantBeRemoved("Admins cannot be removed from the workspace.")

    db.delete(target_member_link)
    db.commit()
    logger.info(
        f"User with ID '{current_user_id}' successfully deleted user with ID '{member_id}' from workspace with ID '{workspace_id}'."
    )
    return {"message": "Member successfully removed from workspace."}
