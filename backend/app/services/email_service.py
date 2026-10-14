# email_service.py
"""
Email service module.

This module knows WHAT each application email should say : which template,
which values.
"""

import os

from backend.app.core.email import send_email
from backend.app.core.email_templates import render_template

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def send_alert_down_email(
    to: str, monitor_name: str, monitor_url: str, status_code: int
) -> None:
    """Notifies a workspace admin that one of their monitors went down."""
    html = render_template(
        "alert_down.html",
        monitor_name=monitor_name,
        monitor_url=monitor_url,
        status_code=status_code,
        dashboard_url=f"{FRONTEND_URL}/dashboard",
    )
    send_email(
        to=to,
        subject=f"[PulseCheck] {monitor_name} is down",
        html_body=html,
    )


def send_alert_recovery_email(
    to: str, monitor_name: str, monitor_url: str
) -> None:
    """Notifies a workspace admin that one of their monitors is back up."""
    html = render_template(
        "alert_recovery.html",
        monitor_name=monitor_name,
        monitor_url=monitor_url,
        dashboard_url=f"{FRONTEND_URL}/dashboard",
    )
    send_email(
        to=to,
        subject=f"[PulseCheck] {monitor_name} is back up",
        html_body=html,
    )
