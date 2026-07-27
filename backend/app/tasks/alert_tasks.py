"""
Celery module for managing alert tasks (Emails, Webhooks)
"""

import logging

import httpx

from backend.app.core.celery_app import celery_app

logger = logging.getLogger("fastapi_app")


@celery_app.task(
    bind=True,
    autoretry_for=(httpx.RequestError, httpx.HTTPStatusError),
    retry_backoff=True,
    retry_backoff_max=300,  # 5 minute max between retries
    max_retries=5,
)
def send_email_alert(self, monitor_id: str, website_url: str, status_code: int):
    """
    Alerting email task.
    """
    # XXX: currently ping simulations, in the future implement real email logic (SendGrid, Amazons SES, aiosmtplib)
    reason = (
        "Timeout/Connexion error" if status_code == 0 else f"HTTP Code {status_code}"
    )
    logger.warning(
        "Alert email sent",
        extra={"monitor_id": monitor_id, "url": website_url, "status": status_code},
    )
    # TODO : query db to find the user email within workspace and send the email


@celery_app.task(
    bind=True,
    autoretry_for=(httpx.RequestError, httpx.HTTPStatusError),
    retry_backoff=True,
    retry_backoff_max=300,  # 5 minute max between retries
    max_retries=5,
)
def send_webhook_alert(self, monitor_id: str, website_url: str, status_code: int):
    """
    Send HTTP payload to the client webhook.
    """
    # XXX: simulating requests, real implementation logic needed
    logger.warning(
        "Webhook sent",
        extra={"monitor_id": monitor_id, "url": website_url, "status": status_code},
    )


@celery_app.task(
    bind=True,
    autoretry_for=(httpx.RequestError, httpx.HTTPStatusError),
    retry_backoff=True,
    retry_backoff_max=300,  # 5 minute max between retries
    max_retries=5,
)
def send_recovery_alert(self, monitor_id: str, website_url: str):
    """
    Send alert when a website is back up.
    """
    logger.info(
        "Recovery email sent",
        extra={"monitor_id": monitor_id, "url": website_url},
    )
    # TODO : query db to find the user email within workspace and send the email
