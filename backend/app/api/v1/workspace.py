# workspace.py
"""
Workspace module.

This module contains FastAPI endpoints for handling workspace related routes.
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.v1.monitor import router_monitor_nested
from backend.app.core.auth import get_current_user_id
from backend.app.db.database import get_db
from backend.app.models.workspace import Workspace
from backend.app.schemas.workspace import (
    MemberCreate,
    WorkspaceCreate,
    WorkspaceReturn,
    WorkspaceUpdate,
)
from backend.app.services import workspace_service

logger = logging.getLogger("fastapi_app")

router_workspace = APIRouter(prefix="/workspaces", tags=["Workspaces"])
router_workspace.include_router(router=router_monitor_nested)


@router_workspace.get("", summary="Get all user workspaces")
def get_user_workspaces(
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspaces: list[tuple[Workspace, str]] = workspace_service.get_user_workspaces(
        db, current_user_id
    )
    return [
        {"id": workspace.id, "name": workspace.name, "role": role}
        for workspace, role in workspaces
    ]


@router_workspace.get(
    "/{workspace_id}",
    response_model=WorkspaceReturn,
    summary="Get workspace details by ID",
)
def get_workspace_by_id(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace: Workspace = workspace_service.get_workspace_by_id(
        workspace_id, db, current_user_id
    )
    return workspace


@router_workspace.get("/{workspace_id}/members", summary="List workspace members")
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
    results: list[tuple[str, str, uuid.UUID]] = workspace_service.get_workspace_members(
        workspace_id, limit, offset, search, role, db, current_user_id
    )
    return [
        {"user_id": user_id, "email": email, "role": user_role}
        for user_role, email, user_id in results
    ]


@router_workspace.post(
    "", status_code=status.HTTP_201_CREATED, summary="Create a new workspace"
)
def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    new_workspace: Workspace = workspace_service.create_workspace(
        workspace_data, db, current_user_id
    )
    return {
        "message": "Workspace created successfully",
        "workspace": {
            "id": new_workspace.id,
            "name": new_workspace.name,
            "created_at": new_workspace.created_at,
        },
    }


@router_workspace.post(
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
    workspace_service.add_member_to_workspace(
        workspace_id, member_data, db, current_user_id
    )
    return {"message": "Member successfully added."}


@router_workspace.patch("/{workspace_id}", summary="Update workspace details")
def edit_workspace_name_by_workspace_id(
    workspace_id: uuid.UUID,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):

    workspace: Workspace = workspace_service.edit_workspace_name_by_workspace_id(
        workspace_id, workspace_data, db, current_user_id
    )
    return workspace


@router_workspace.delete("/{workspace_id}", summary="Delete a workspace")
def delete_workspace_by_id(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace_service.delete_workspace_by_id(workspace_id, db, current_user_id)
    return {"message": "Workspace successfully deleted."}


@router_workspace.delete("/{workspace_id}/leave", summary="Leave a workspace")
def leave_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace_service.leave_workspace(workspace_id, db, current_user_id)
    return {"message": "You have successfully left the workspace."}


@router_workspace.delete(
    "/{workspace_id}/{member_id}", summary="Remove a member from workspace"
)
def delete_member_from_workspace(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    workspace_service.delete_member_from_workspace(
        workspace_id, member_id, db, current_user_id
    )
    return {"message": "Member successfully removed from workspace."}
