# models/workspace.py
"""
SQLAlchemy Workspace & WorkspaceUsers Database Models.

Contains the declarative base definitions for the workspace and workspace_users database tables.
"""

import uuid
from datetime import datetime, timezone

from database import Base
from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship


class WorkspaceUser(Base):
    __tablename__ = "workspace_users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("workspace.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(50), default="Viewer", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # relationship definitions
    # NOTE: use "User" and "Workspace" strings to avoid circular imports
    workspace: Mapped["Workspace"] = relationship(back_populates="user_associations")
    user: Mapped["User"] = relationship(back_populates="workspace_associations")


class Workspace(Base):
    __tablename__ = "workspace"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(
            timezone.utc
        ),  # onupdate takes the 'current' update time
    )
    user_associations: Mapped[list["WorkspaceUser"]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
