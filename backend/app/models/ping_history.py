# models/workspace.py
"""
SQLAlchemy PingHistory Database Models.

Contains the declarative base definitions for the ping_history database table.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from backend.app.models.monitor import Monitor


class PingHistory(Base):
    __tablename__ = "ping_history"

    id: Mapped[uuid.UUID] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    monitor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False
    )
    status_code: Mapped[int] = mapped_column(Integer)
    latency_ms: Mapped[int] = mapped_column(Integer)
    pinged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    monitor: Mapped["Monitor"] = relationship(
        back_populates="ping_history_associations"
    )
