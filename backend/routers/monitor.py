"""
Monitor module.

This module contains FastAPI endpoints for handling workspace related routes.
"""

import logging
import uuid
from typing import Optional

import routers.ping_history as ping_history
from auth import get_current_user_id
from database import get_db

#  from exceptions import (...)
from fastapi import APIRouter, Depends, Query, status
from models.workspace import Monitor, Workspace, WorkspaceUser
from schemas import (
    MonitorBulkDelete,
    MonitorCreate,
    MonitorListResponse,
    MonitorResponse,
    MonitorStatus,
    MonitorUpdate,
)
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

logger = logging.getLogger("fastapi_app")

router_nested = APIRouter()


@router_nested.get(
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
        stmt_get_monitors = stmt_get_monitors.where(Monitor.name.ilike(f"%{name}"))

    stmt_get_monitors = stmt_get_monitors.offset(skip).limit(limit)

    monitors: list[Monitor] = db.execute(stmt_get_monitors).scalars().all()

    return {"monitors": monitors}


@router_nested.get(
    "/{workspace_id}/monitors/{monitor_id}",
    response_model=MonitorResponse,
    summary="Get monitor by ID",
)
def get_monitor_by_id(
    workspace_id: uuid.UUID,
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> Monitor:

    # NOTE : JOIN ON needs to contain only the linking tables condition ( PK = external key )
    # in WHERE we put the filtering conditions imposed by the route ( business logic )
    # it might work to put some other things in the .join as well but this is the standard
    # way to do it
    # stmt = (
    #     select(Monitor)
    #     .join(
    #         WorkspaceUser,
    #         WorkspaceUser.workspace_id == Monitor.workspace_id,
    #     )
    #     .where(
    #         Monitor.id == monitor_id,
    #         Monitor.workspace_id == workspace_id,
    #         WorkspaceUser.user_id == current_user_id,
    #     )
    # )
    workspace: Workspace = db.get(Workspace, workspace_id)
    if not workspace:
        logger.warning(
            f"User '{current_user_id}' tried to fetch a monitor from a non-existent workspace '{workspace_id}'."
        )
        raise WorkspaceNotFound("The specified workspace does not exist.")

    # user must be a member of workspace to fetch a specific monitor
    workspace_user: WorkspaceUser = db.get(
        WorkspaceUser, {"workspace_id": workspace_id, "user_id": current_user_id}
    )
    if not workspace_user:
        logger.warning(
            f"User '{current_user_id}' tried to fetch a monitor in workspace '{workspace.id} - {workspace.name}' without being a member."
        )
        raise UserNotInWorkspace(
            "You are not a member of this workspace and cannot fetch monitors."
        )

    monitor: Monitor = db.get(Monitor, monitor_id)
    if not monitor:
        logger.warning(
            f"User '{current_user_id}' tried to fetch a non-existing a monitor in workspace '{workspace.id} - {workspace.name}"
        )
        raise MonitorNotFound("Monitor does not exist")

    if monitor.workspace_id != workspace.id:
        logger.warning(
            f"User '{current_user_id}' tried to fetch monitor '{monitor_id}' which belongs to another workspace, using workspace '{workspace.id}' in URL."
        )
        raise MonitorNotFound("Monitor does not exist in this workspace")

    return monitor


@router_nested.patch(
    "/{workspace_id}/monitors/{monitor_id}",
    response_model=MonitorResponse,
    summary="Update monitor's fields.",
)
def update_monitor_by_id(
    workspace_id: uuid.UUID,
    monitor_id: uuid.UUID,
    monitor_data: MonitorUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Monitor:
    stmt = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(
            Monitor.id == monitor_id,
            Monitor.workspace_id == workspace_id,
            WorkspaceUser.user_id == current_user_id,
        )
    )
    monitor: Monitor = db.execute(stmt).scalar_one_or_none()
    if not monitor:
        logger.warning(
            f"User '{current_user_id}' tried to update a non-existing monitor '{monitor_id}' in workspace '{workspace_id}'."
        )
        raise MonitorNotFound("Monitor does not exist")
    if monitor_data.status is not None:
        allowed_user_statuses = [MonitorStatus.paused, MonitorStatus.pending]

        if monitor_data.status not in allowed_user_statuses:
            raise Exception("no perimissions")

    update_dict = monitor_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(monitor, key, value)
    db.commit()
    db.refresh(monitor)
    logger.info("success message")
    return monitor


@router_nested.post(
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
            f"User '{current_user_id}' tried to create a monitor in non-existent workspace '{workspace_id}'."
        )
        raise WorkspaceNotFound("The specified workspace does not exist.")

    # user must be a member of the workspace to create a monitor
    membership: WorkspaceUser = db.get(
        WorkspaceUser, {"workspace_id": workspace_id, "user_id": current_user_id}
    )

    if not membership:
        logger.warning(
            f"User '{current_user_id}' tried to create a monitor in workspace '{workspace.id} - {workspace.name}' without being a member."
        )
        raise UserNotInWorkspace(
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
        f"User '{current_user_id}' created monitor '{new_monitor.id} - {new_monitor.name}' in workspace '{workspace.id} - {workspace.name}'."
    )

    return new_monitor


@router_nested.post(
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
            f"User '{current_user}' tried to bulk-delete monitors in workspace '{workspace_id}' without access."
        )

        raise Exception(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or you do not have permission.",
        )

    stmt_delete = delete(Monitor).where(
        Monitor.workspace_id == workspace_id,
        Monitor.id.in_(payload.monitor_ids),
    )

    result = db.execute(stmt_delete)

    db.commit()

    logger.info(
        f"User '{current_user}' executed bulk-delete in workspace '{workspace_id}'. "
        f"Requested: {len(payload.monitor_ids)} | Actually deleted: {result.rowcount} monitors."
    )

    return None


@router_nested.delete(
    "/{workspace_id}/monitors/{monitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a monitor",
)
def delete_monitor_by_id(
    workspace_id: uuid.UUID,
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    stmt = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(
            Monitor.id == monitor_id,
            Monitor.workspace_id == workspace_id,
            WorkspaceUser.user_id == current_user_id,
        )
    )
    monitor: Monitor = db.execute(stmt).scalar_one_or_none()
    if not monitor:
        logger.warning("user tried to delete a montior that does not exist")
        raise MonitorNotFound("Non-existent monitor")
    db.delete(monitor)
    db.commit()

    return None


@router_nested.delete(
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

    logger.info(f"Deleted {result.rowcount} monitors.")

    return None


router = APIRouter(prefix="/monitors", tags=["Monitors"])
router.include_router(router=ping_history.router)


@router.get(
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
            f"User '{current_user_id}' tried to fetch monitor '{monitor_id}' "
            "without access or it does not exist."
        )
        raise MonitorNotFound("Monitor not found or access denied.")

    return monitor


@router.patch(
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
            f"User '{current_user_id}' tried to update monitor '{monitor_id}' "
            "without access or it does not exist."
        )
        raise MonitorNotFound("Monitor not found or access denied.")

    if monitor_data.status is not None:
        allowed_user_statuses = [MonitorStatus.paused, MonitorStatus.pending]

        if monitor_data.status not in allowed_user_statuses:
            # TODO: change exception into 403 Forbidden
            raise Exception("No permissions to set this status")

    update_dict = monitor_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(monitor, key, value)

    db.commit()
    db.refresh(monitor)

    logger.info(
        f"Monitor '{monitor_id}' successfully updated by user '{current_user_id}'."
    )
    return monitor


@router.delete(
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
            f"User '{current_user_id}' tried to delete monitor '{monitor_id}' "
            "without access or it does not exist."
        )
        raise MonitorNotFound("Monitor not found or access denied.")

    db.delete(monitor)
    db.commit()

    logger.info(
        f"Monitor '{monitor_id}' successfully deleted by user '{current_user_id}'."
    )
    return None
