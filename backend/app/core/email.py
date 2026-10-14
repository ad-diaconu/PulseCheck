"""
Generic email sending via SMTP. Knows nothing about alerts, invitations,
or password resets.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# NOTE: to use a different "from" address than the default, you can set the EMAIL_FROM environment variable
EMAIL_FROM = os.getenv("EMAIL_FROM", "no-reply@pulsecheck.app")


def send_email(to: str, subject: str, html_body: str) -> None:
    """Sends a single email. Raises on failure — let the caller (a celery
    task with autoretry_for) decide how to handle a failed send."""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = to
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)
