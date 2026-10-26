"""
Celery module for auth-related emails (verification, password reset).
Separate from alert_tasks.py, which is specific to monitor up/down alerts.
"""

import logging
import smtplib

from backend.app.core.celery_app import celery_app
from backend.app.services.email_service import send_verification_email

logger = logging.getLogger("fastapi_app")


@celery_app.task(
    bind=True,
    autoretry_for=(smtplib.SMTPException, OSError),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=5,
)
def send_verification_email_task(self, email: str, code: str):
    """
    Sends the email verification code. Runs async so POST /signup doesn't
    have to wait on the SMTP round-trip before responding.
    """
    send_verification_email(to=email, code=code)
    logger.info("Verification email sent", extra={"email": email})
