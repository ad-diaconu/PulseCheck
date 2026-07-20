"""
Monitor module.

This module contains FastAPI endpoints for handling workspace related routes.
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.api.v1.ping_history import router_ping_history
from backend.app.core.auth import get_current_user_id
from backend.app.core.exceptions import (
    MonitorNotFoundError,
    MonitorPermissionError,
    UserNotInWorkspaceError,
    WorkspaceNotFoundError,
)
from backend.app.db.database import get_db
from backend.app.models.workspace import Monitor, Workspace, WorkspaceUser
from backend.app.schemas.monitor import (
    MonitorBulkDelete,
    MonitorCreate,
    MonitorListResponse,
    MonitorResponse,
    MonitorStatus,
    MonitorUpdate,
)

logger = logging.getLogger("fastapi_app")

router_monitor_nested = APIRouter(tags=["Monitors"])


@router_monitor_nested.get(
    "/{workspace_id}/monitors",
    response_model=MonitorListResponse,
    summary="Get all workspace monitors.",
)
def list_workspace_monitors(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user_id),
    # filter params
    status: Optional[MonitorStatus] = None,
    name: Optional[str] = None,
    # query params
    skip: int = Query(0, ge=0, description="How many entries to skip"),
    limit: int = Query(50, ge=1, description="Maximum number of returned entries"),
) -> dict[str, list[Monitor]]:
    stmt_get_monitors = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(
            Monitor.workspace_id == workspace_id, WorkspaceUser.user_id == current_user
        )
    )
    if status:
        stmt_get_monitors = stmt_get_monitors.where(Monitor.status == status)

    if name:
        # use ilike for case-insensitive search (e.g. ?name=AWS | ?name=aws)
        stmt_get_monitors = stmt_get_monitors.where(Monitor.name.ilike(f"%{name}%"))

    stmt_get_monitors = stmt_get_monitors.offset(skip).limit(limit)

    monitors: list[Monitor] = db.execute(stmt_get_monitors).scalars().all()

    return {"monitors": monitors}


# @router_monitor_nested.get(
#     "/{workspace_id}/monitors/{monitor_id}",
#     response_model=MonitorResponse,
#     summary="Get monitor by ID",
# )
# def get_monitor_by_id(
#     workspace_id: uuid.UUID,
#     monitor_id: uuid.UUID,
#     db: Session = Depends(get_db),
#     current_user_id: uuid.UUID = Depends(get_current_user_id),
# ) -> Monitor:

#     workspace: Workspace = db.get(Workspace, workspace_id)
#     if not workspace:
#         logger.warning(
#             "User failed to fetch a monitor from a non-existent workspace",
#             extra={
#                 "user_id": current_user_id,
#                 "workspace_id": workspace_id,
#             },
#         )
#         raise WorkspaceNotFoundError("The specified workspace does not exist.")

#     # user must be a member of workspace to fetch a specific monitor
#     workspace_user: WorkspaceUser = db.get(
#         WorkspaceUser, {"workspace_id": workspace_id, "user_id": current_user_id}
#     )
#     if not workspace_user:
#         logger.warning(
#             "User failed to fetch a monitor from workspace (not a member).",
#             extra={
#                 "user_id": current_user_id,
#                 "workspace_name": workspace.name,
#                 "workspace_id": workspace_id,
#             },
#         )
#         raise UserNotInWorkspaceError(
#             "You are not a member of this workspace and cannot fetch monitors."
#         )

#     monitor: Monitor = db.get(Monitor, monitor_id)
#     if not monitor:
#         logger.warning(
#             "User failed to fetch (non-existing) monitor from workspace",
#             extra={
#                 "user_id": current_user_id,
#                 "monitor_id": monitor_id,
#                 "workspace_name": workspace.name,
#                 "workspace_id": workspace_id,
#             },
#         )
#         raise MonitorNotFoundError("Monitor does not exist")

#     if monitor.workspace_id != workspace.id:
#         logger.warning(
#             "User failed to fetch monitor from another workspace",
#             extra={
#                 "user_id": current_user_id,
#                 "monitor_id": monitor_id,
#                 "workspace_id": workspace_id,
#             },
#         )
#         raise MonitorNotFoundError("Monitor does not exist in this workspace")

#     return monitor


# @router_monitor_nested.patch(
#     "/{workspace_id}/monitors/{monitor_id}",
#     response_model=MonitorResponse,
#     summary="Update monitor's fields.",
# )
# def update_monitor_by_id(
#     workspace_id: uuid.UUID,
#     monitor_id: uuid.UUID,
#     monitor_data: MonitorUpdate,
#     db: Session = Depends(get_db),
#     current_user_id: str = Depends(get_current_user_id),
# ) -> Monitor:
#     stmt = (
#         select(Monitor)
#         .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
#         .where(
#             Monitor.id == monitor_id,
#             Monitor.workspace_id == workspace_id,
#             WorkspaceUser.user_id == current_user_id,
#         )
#     )
#     monitor: Monitor = db.execute(stmt).scalar_one_or_none()
#     if not monitor:
#         logger.warning(
#             "User attempted to update non-existing monitor in workspace.",
#             extra={
#                 "user_id": current_user_id,
#                 "workspace_id": workspace_id,
#                 "monitor_id": monitor_id,
#             },
#         )
#         raise MonitorNotFoundError("Monitor does not exist")
#     if monitor_data.status is not None:
#         allowed_user_statuses = [MonitorStatus.paused, MonitorStatus.pending]

#         if monitor_data.status not in allowed_user_statuses:
#             logger.warning(
#                 "User attempted to set monitor status to a value they do not have permission for.",
#                 extra={
#                     "user_id": current_user_id,
#                     "workspace_id": workspace_id,
#                     "monitor_id": monitor_id,
#                     "attempted_status": monitor_data.status,
#                 },
#             )
#             raise MonitorPermissionError("No permissions to set this status")

#     update_dict = monitor_data.model_dump(exclude_unset=True)
#     for key, value in update_dict.items():
#         setattr(monitor, key, value)
#     db.commit()
#     db.refresh(monitor)
#     logger.info(
#         "Monitor updated successfully",
#         extra={
#             "user_id": current_user_id,
#             "workspace_id": workspace_id,
#             "monitor_id": monitor.id,
#         },
#     )
#     return monitor


@router_monitor_nested.post(
    "/{workspace_id}/monitors",
    status_code=status.HTTP_201_CREATED,
    response_model=MonitorResponse,
    summary="Create a monitor within the workspace",
)
def create_monitor(
    workspace_id: uuid.UUID,
    monitor_data: MonitorCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Monitor:
    workspace: Workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(
            "User attempted to create monitor in non-existent workspace.",
            extra={"user_id": current_user_id, "workspace_id": workspace_id},
        )
        raise WorkspaceNotFoundError("The specified workspace does not exist.")

    # user must be a member of the workspace to create a monitor
    membership: WorkspaceUser = db.get(
        WorkspaceUser, {"workspace_id": workspace_id, "user_id": current_user_id}
    )

    if not membership:
        logger.warning(
            "User attempted to create monitor but is not a member of the workspace.",
            extra={
                "user_id": current_user_id,
                "workspace_id": workspace_id,
                "workspace_name": workspace.name,
            },
        )
        raise UserNotInWorkspaceError(
            "You are not a member of this workspace and cannot create monitors."
        )

    new_monitor: Monitor = Monitor(
        workspace_id=workspace_id,
        name=monitor_data.name,
        url=monitor_data.url,
        interval_minutes=monitor_data.interval_minutes,
    )

    db.add(new_monitor)
    db.commit()
    db.refresh(new_monitor)

    logger.info(
        "User created monitor",
        extra={
            "user_id": current_user_id,
            "monitor_id": new_monitor.id,
            "monitor_name": new_monitor.name,
            "workspace_id": workspace.id,
            "workspace_name": workspace.name,
        },
    )

    return new_monitor


@router_monitor_nested.post(
    "/{workspace_id}/monitors/bulk-delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete multiple monitors at once using a list of IDs.",
)
def bulk_delete_workspace_monitors(
    workspace_id: uuid.UUID,
    payload: MonitorBulkDelete,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user_id),
) -> None:

    workspace_access_stmt = select(WorkspaceUser).where(
        WorkspaceUser.workspace_id == workspace_id,
        WorkspaceUser.user_id == current_user,
    )
    membership = db.execute(workspace_access_stmt).scalar_one_or_none()

    if not membership:
        logger.warning(
            "User attempted bulk-delete without workspace access.",
            extra={"user_id": current_user, "workspace_id": workspace_id},
        )

        raise MonitorPermissionError(
            detail="Workspace not found or you do not have permission."
        )

    stmt_delete = delete(Monitor).where(
        Monitor.workspace_id == workspace_id,
        Monitor.id.in_(payload.monitor_ids),
    )

    result = db.execute(stmt_delete)

    db.commit()

    logger.info(
        "User executed bulk-delete",
        extra={
            "user_id": current_user,
            "workspace_id": workspace_id,
            "requested_count": len(payload.monitor_ids),
            "deleted_count": result.rowcount,
        },
    )

    return None


# @router_monitor_nested.delete(
#     "/{workspace_id}/monitors/{monitor_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     summary="Delete a monitor",
# )
# def delete_monitor_by_id(
#     workspace_id: uuid.UUID,
#     monitor_id: uuid.UUID,
#     db: Session = Depends(get_db),
#     current_user_id: uuid.UUID = Depends(get_current_user_id),
# ) -> None:
#     stmt = (
#         select(Monitor)
#         .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
#         .where(
#             Monitor.id == monitor_id,
#             Monitor.workspace_id == workspace_id,
#             WorkspaceUser.user_id == current_user_id,
#         )
#     )
#     monitor: Monitor = db.execute(stmt).scalar_one_or_none()
#     if not monitor:
#         logger.warning(
#             "User tried to delete a monitor that does not exist",
#             extra={
#                 "user_id": current_user_id,
#                 "workspace_id": workspace_id,
#                 "monitor_id": monitor_id,
#             },
#         )
#         raise MonitorNotFoundError("Non-existent monitor")
#     db.delete(monitor)
#     db.commit()

#     return None


@router_monitor_nested.delete(
    "/{workspace_id}/monitors",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workspace_monitors(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user_id),
    status: Optional[MonitorStatus] = None,
    name: Optional[str] = None,
):

    user_workspaces_stmt = (
        select(WorkspaceUser.workspace_id).where(WorkspaceUser.user_id == current_user)
    ).subquery()

    stmt_delete = delete(Monitor).where(
        Monitor.workspace_id == workspace_id,
        Monitor.workspace_id.in_(user_workspaces_stmt),
    )

    if status:
        stmt_delete = stmt_delete.where(Monitor.status == status)

    if name:
        stmt_delete = stmt_delete.where(Monitor.name.ilike(f"%{name}%"))

    result = db.execute(stmt_delete)
    db.commit()

    logger.info(
        "User deleted monitors",
        extra={
            "user_id": current_user,
            "workspace_id": workspace_id,
            "deleted_count": result.rowcount,
        },
    )

    return None


router_monitor = APIRouter(prefix="/monitors", tags=["Monitors"])
router_monitor.include_router(router=router_ping_history)


@router_monitor.get(
    "/{monitor_id}",
    response_model=MonitorResponse,
    summary="Get monitor by ID",
)
def get_monitor_by_id(
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> Monitor:
    """Fetch a specific monitor by ID, ensuring the user has access."""
    stmt = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(
            Monitor.id == monitor_id,
            WorkspaceUser.user_id == current_user_id,
        )
    )
    monitor: Monitor = db.execute(stmt).scalar_one_or_none()

    if not monitor:
        logger.warning(
            "User tried to fetch monitor without access or it does not exist.",
            extra={"user_id": current_user_id, "monitor_id": monitor_id},
        )
        raise MonitorNotFoundError("Monitor not found or access denied.")

    return monitor


@router_monitor.patch(
    "/{monitor_id}",
    response_model=MonitorResponse,
    summary="Update monitor's fields.",
)
def update_monitor_by_id(
    monitor_id: uuid.UUID,
    monitor_data: MonitorUpdate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> Monitor:
    """Update a specific monitor if the user is a member of its workspace."""
    stmt = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(
            Monitor.id == monitor_id,
            WorkspaceUser.user_id == current_user_id,
        )
    )
    monitor: Monitor = db.execute(stmt).scalar_one_or_none()

    if not monitor:
        logger.warning(
            "User tried to update monitor without access or it does not exist.",
            extra={"user_id": current_user_id, "monitor_id": monitor_id},
        )
        raise MonitorNotFoundError("Monitor not found or access denied.")

    if monitor_data.status is not None:
        allowed_user_statuses = [MonitorStatus.paused, MonitorStatus.pending]

        if monitor_data.status not in allowed_user_statuses:
            raise MonitorPermissionError("No permissions to set this status")

    update_dict = monitor_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(monitor, key, value)

    db.commit()
    db.refresh(monitor)

    logger.info(
        "User successfully updated monitor",
        extra={"user_id": current_user_id, "monitor_id": monitor_id},
    )
    return monitor


@router_monitor.delete(
    "/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a monitor",
)
def delete_monitor_by_id(
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    """Delete a specific monitor if the user is a member of its workspace."""
    stmt = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(
            Monitor.id == monitor_id,
            WorkspaceUser.user_id == current_user_id,
        )
    )
    monitor: Monitor = db.execute(stmt).scalar_one_or_none()

    if not monitor:
        logger.warning(
            "User tried to delete monitor without access or it does not exist.",
            extra={"user_id": current_user_id, "monitor_id": monitor_id},
        )
        raise MonitorNotFoundError("Monitor not found or access denied.")

    db.delete(monitor)
    db.commit()

    logger.info(
        "User successfully deleted monitor",
        extra={"user_id": current_user_id, "monitor_id": monitor_id},
    )
    return None
