"""
SQL Alchemy Monitor Database Models.

Contains the declarative base definitions for the monitors database tables.
"""

import enum
import uuid
from datetime import datetime, timezone

from database import Base
from models.ping_history import PingHistory
from models.workspace import Workspace
from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship


class MonitorStatus(str, enum.Enum):
    pending = "pending"
    up = "up"
    down = "down"
    paused = "paused"
    degraded = "degraded"


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(MonitorStatus), default=MonitorStatus.pending, nullable=False
    )
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    workspace: Mapped["Workspace"] = relationship(back_populates="monitor_associations")
    ping_history_associations: Mapped[list["PingHistory"]] = relationship(
        back_populates="monitor", cascade="all, delete-orphan"
    )
