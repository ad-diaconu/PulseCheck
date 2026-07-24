"""
Celery module for managing alert tasks (Emails, Webhooks)
"""

import logging

from app.core.celery_app import celery_app

logger = logging.getLogger("fastapi_app")


@celery_app.task
def send_email_alert(monitor_id: str, website_url: str, status_code: int):
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


@celery_app.task
def send_webhook_alert(monitor_id: str, webiste_url: str, status_code: int):
    """
    Send HTTP payload to the client webhook.
    """
    # XXX: simulating requests, real implementation logic needed
    logger.warning(
        "Webhook sent",
        extra={"monitor_id": monitor_id, "url": webiste_url, "status": status_code},
    )
