"""
Monitor service module.

This module contains the business logic required for handling montior related (db) operations.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    MonitorNotFoundError,
    MonitorPermissionError,
    UserNotInWorkspaceError,
    WorkspaceNotFoundError,
)
from backend.app.models.workspace import Monitor, Workspace, WorkspaceUser
from backend.app.schemas.monitor import (
    MonitorBulkDelete,
    MonitorCreate,
    MonitorStatus,
    MonitorUpdate,
)

logger = logging.getLogger("fastapi_app")


def get_workspace_monitors(
    workspace_id: uuid.UUID,
    db: Session,
    user_id: uuid.UUID,
    skip: int,
    limit: int,
    status: Optional[MonitorStatus] = None,
    name: Optional[str] = None,
) -> dict[str, list[Monitor]]:
    """
    Business logic needed to fetch all monitors for a given workspace, with optional filtering by status and name, and pagination support.

    Args:
        workspace_id (uuid.UUID): The ID of the workspace to fetch monitors for.
        db (Session): The database session.
        current_user (uuid.UUID): The ID of the current user.
        status (Optional[MonitorStatus], optional): Filter monitors by their status. Defaults to None.
        name (Optional[str], optional): Filter monitors by their name. Defaults to None.
        skip (int, optional): Number of entries to skip for pagination. Defaults to 0
        limit (int, optional): Maximum number of returned entries for pagination. Defaults to 50.

    Returns:
        dict[str, list[Monitor]]: A dictionary containing a list of monitors under the key
    """
    stmt_get_monitors = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(Monitor.workspace_id == workspace_id, WorkspaceUser.user_id == user_id)
    )
    if status:
        stmt_get_monitors = stmt_get_monitors.where(Monitor.status == status)

    if name:
        # use ilike for case-insensitive search (e.g. ?name=AWS | ?name=aws)
        stmt_get_monitors = stmt_get_monitors.where(Monitor.name.ilike(f"%{name}"))

    stmt_get_monitors = stmt_get_monitors.offset(skip).limit(limit)

    monitors: list[Monitor] = db.execute(stmt_get_monitors).scalars().all()
    logger.info(
        "User successfully retrieved workspace monitors",
        extra={
            "user_id": user_id,
            "workspace_id": workspace_id,
            "monitors": len(monitors),
        },
    )

    return list(monitors)


def create_monitor(
    workspace_id: uuid.UUID,
    monitor_data: MonitorCreate,
    db: Session,
    current_user_id: str,
) -> Monitor:
    """
    Business logic needed to create a new monitor in a given workspace.

    Args:
        workspace_id (uuid.UUID): The ID of the workspace to create the monitor in.
        monitor_data (MonitorCreate): The data for the new monitor.
        db (Session): The database session.
        current_user_id (str): The ID of the current user.
    """
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


def bulk_delete_workspace_monitors(
    workspace_id: uuid.UUID,
    payload: MonitorBulkDelete,
    db: Session,
    current_user: uuid.UUID,
) -> int:
    """
    Business logic needed to bulk delete monitors in a given workspace.

    Args:
        workspace_id (uuid.UUID): The ID of the workspace to delete monitors from.
        payload (MonitorBulkDelete): The data containing the list of monitor IDs to delete.
        db (Session): The database session.
        current_user (uuid.UUID): The ID of the current user.

    """
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

    return result.rowcount


# @router_nested.delete(
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


def delete_workspace_monitors(
    workspace_id: uuid.UUID,
    db: Session,
    current_user: uuid.UUID,
    status: Optional[MonitorStatus] = None,
    name: Optional[str] = None,
):
    """
    Business logic needed to delete all monitors in a given workspace, with optional filtering by status and name.

    Args:
        workspace_id (uuid.UUID): The ID of the workspace to delete monitors from.
        db (Session): The database session.
        current_user (uuid.UUID): The ID of the current user.
        status (Optional[MonitorStatus]): The status to filter monitors by.
        name (Optional[str]): The name to filter monitors by.
    """

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


def get_monitor_by_id(
    monitor_id: uuid.UUID,
    db: Session,
    current_user_id: uuid.UUID,
) -> Monitor:
    """
    Buisness logic needed to fetch a specific monitor by its ID, ensuring the user is a member of the associated workspace.

    Args:
        monitor_id (uuid.UUID): The ID of the monitor to fetch.
        db (Session): The database session.
        current_user_id (uuid.UUID): The ID of the current user.

    Returns:
        Monitor: The monitor object if found and the user has access.
    """
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


def update_monitor_by_id(
    monitor_id: uuid.UUID,
    monitor_data: MonitorUpdate,
    db: Session,
    current_user_id: uuid.UUID,
) -> Monitor:
    """
    Business logic needed to update a specific monitor by its ID, ensuring the user is a member of the associated workspace.

    Args:
        monitor_id (uuid.UUID): The ID of the monitor to update.
        monitor_data (MonitorUpdate): The data to update the monitor with.
        db (Session): The database session.
        current_user_id (uuid.UUID): The ID of the current user.

    Returns:
        Monitor: The updated monitor object.

    Raises:
        MonitorNotFoundError: If the monitor does not exist or the user does not have access.
    """
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


def delete_monitor_by_id(
    monitor_id: uuid.UUID,
    db: Session,
    current_user_id: uuid.UUID,
) -> None:
    """
    Business logic needed for deleting a monitor.

    Args:
        monitor_id (uuid.UUID): The ID of the monitor to delete.
        db (Session): The database session.
        current_user_id (uuid.UUID): The ID of the current user.

    Returns:
        None

    Raises:
        MonitorNotFoundError: If the monitor does not exist or the user does not have access
    """
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
