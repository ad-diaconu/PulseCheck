"""
PingHistory module.

This module contains FastAPI endpoints for handling ping_history related routes.
"""

import logging
import uuid
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.auth import get_current_user_id
from backend.app.core.exceptions import (
    MonitorNotFoundError,
)
from backend.app.db.database import get_db
from backend.app.models.ping_history import PingHistory
from backend.app.models.workspace import Monitor, WorkspaceUser
from backend.app.schemas.ping_history import PingHistoryListResponse

logger = logging.getLogger("fastapi_app")

router_ping_history = APIRouter(tags=["Ping History"])


class PingSortField(str, Enum):
    date = "date"
    latency = "latency"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


@router_ping_history.get(
    "/{monitor_id}/pings",
    response_model=PingHistoryListResponse,
    summary="Fetch ping history for a specific monitor",
)
def get_pings(
    monitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    status_code: Optional[int] = None,
    sort_by: PingSortField = Query(PingSortField.date, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort order (asc/desc)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    stmt_check_access = (
        select(Monitor)
        .join(WorkspaceUser, WorkspaceUser.workspace_id == Monitor.workspace_id)
        .where(
            Monitor.id == monitor_id,
            WorkspaceUser.user_id == current_user_id,
        )
    )

    monitor: Monitor = db.execute(stmt_check_access).scalar_one_or_none()
    if not monitor:
        logger.warning(
            "User attempted to access monitor without permission or monitor does not exist.",
            extra={"user_id": current_user_id, "monitor_id": monitor_id},
        )
        raise MonitorNotFoundError("Monitor not found or access denied.")

    stmt_get_pings = select(PingHistory).where(PingHistory.monitor_id == monitor_id)

    if status_code:
        stmt_get_pings = stmt_get_pings.where(PingHistory.status_code == status_code)

    if sort_by == PingSortField.latency:
        sort_column = PingHistory.latency_ms
    else:
        sort_column = PingHistory.pinged_at

    if sort_order == SortOrder.desc:
        stmt_get_pings = stmt_get_pings.order_by(sort_column.desc())
    else:
        stmt_get_pings = stmt_get_pings.order_by(sort_column.asc())

    stmt_get_pings = stmt_get_pings.offset(skip).limit(limit)

    pings = db.execute(stmt_get_pings).scalars().all()

    logger.info(
        "User fetched ping history",
        extra={
            "user_id": current_user_id,
            "monitor_id": monitor_id,
            "returned_count": len(pings),
        },
    )

    return {"pings": pings}


# TODO
def get_pings_stats():
    pass


TODO = """
GET /api/monitors/{monitor_id}/pings
- page
-limit
-cursor
-sort_by( latency date )
- sort_oreder (asc / dsc)
GET /api/monitors/{monitor_id}/stats
- query params time frame ( 24h. 7d, 30d)
- return medium latency and uptime percentage 
"""
