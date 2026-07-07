"""
Montiro module.

This module contains FastAPI endpoints for handling workspace related routes.
"""

import logging
import uuid
from typing import Optional

from auth import get_current_user_id
from database import get_db

#  from exceptions import (...)
from fastapi import APIRouter, Depends, Query, status
from models.workspace import Monitor, Workspace, WorkspaceUser
from schemas import MonitorCreate, MonitorListResponse, MonitorStatus
from sqlalchemy import select
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
):
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

    stmt_get_monitors.offset(skip).limit(limit)

    monitors: list[Monitor] = db.execute(stmt_get_monitors).scalars().all()

    return {"monitors": monitors}


@router_nested.post(
    "/{workspace_id}/monitors",
    status_code=status.HTTP_201_CREATED,
    summary="Create a monitor within the workspace",
)
def create_monitor(
    workspace_id: uuid.UUID,
    monitor_data: MonitorCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    pass


router = APIRouter(prefix="/monitors", tags=["Monitors"])

TODO = """
2 types of endpoints
COLLECTIONS - dependent on workspace
- create monitor 
- get monitors ( filter,pagination,etc )
SINGLES - independent of workspace ( once we created a monitor we have its UUID)
- get monitor
- get monitors ( filter, pagination, etc)
- update monitor 
- delete monitor
"""
