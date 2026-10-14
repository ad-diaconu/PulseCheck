"""
Celery module for managing email alert tasks.
"""

import logging
import smtplib

from sqlalchemy import select

from backend.app.core.celery_app import celery_app
from backend.app.db.database import SessionLocal
from backend.app.models.monitor import Monitor
from backend.app.models.user import User
from backend.app.models.workspace import WorkspaceUser
from backend.app.services.email_service import (
    send_alert_down_email,
    send_alert_recovery_email,
)

logger = logging.getLogger("fastapi_app")


def _get_workspace_admin_emails(db, workspace_id) -> list[str]:
    """Looks up the email of every Admin member of a workspace. Only admins
    get alert emails - they have edit permissions."""
    stmt = (
        select(User.email)
        .join(WorkspaceUser, WorkspaceUser.user_id == User.id)
        .where(
            WorkspaceUser.workspace_id == workspace_id,
            WorkspaceUser.role == "Admin",
        )
    )
    return list(db.execute(stmt).scalars().all())


@celery_app.task(
    bind=True,
    autoretry_for=(smtplib.SMTPException, OSError),
    retry_backoff=True,
    retry_backoff_max=300,  # 5 minute max between retries
    max_retries=5,
)
def send_email_alert(self, monitor_id: str, website_url: str, status_code: int):
    """
    Alerting email task.
    """
    with SessionLocal() as db:
        monitor = db.get(Monitor, monitor_id)
        if not monitor:
            # Monitor was deleted between the ping and this task running —
            # nothing to alert about anymore.
            logger.warning(
                "Alert skipped: monitor no longer exists",
                extra={"monitor_id": monitor_id},
            )
            return

        admin_emails = _get_workspace_admin_emails(db, monitor.workspace_id)

        for admin_email in admin_emails:
            send_alert_down_email(
                to=admin_email,
                monitor_name=monitor.name,
                monitor_url=website_url,
                status_code=status_code,
            )

        logger.warning(
            "Alert email sent",
            extra={
                "monitor_id": monitor_id,
                "url": website_url,
                "status": status_code,
                "recipients": len(admin_emails),
            },
        )


@celery_app.task(
    bind=True,
    autoretry_for=(smtplib.SMTPException, OSError),
    retry_backoff=True,
    retry_backoff_max=300,  # 5 minute max between retries
    max_retries=5,
)
def send_recovery_alert(self, monitor_id: str, website_url: str):
    """
    Notify workspace admins by email when a website is back up.
    """
    with SessionLocal() as db:
        monitor = db.get(Monitor, monitor_id)
        if not monitor:
            logger.warning(
                "Recovery alert skipped: monitor no longer exists",
                extra={"monitor_id": monitor_id},
            )
            return

        admin_emails = _get_workspace_admin_emails(db, monitor.workspace_id)

        for admin_email in admin_emails:
            send_alert_recovery_email(
                to=admin_email,
                monitor_name=monitor.name,
                monitor_url=website_url,
            )

        logger.info(
            "Recovery alert email sent",
            extra={
                "monitor_id": monitor_id,
                "url": website_url,
                "recipients": len(admin_emails),
            },
        )
