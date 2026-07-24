"""
Celery module for managing pinging tasks.
"""

import time
from datetime import datetime, timezone

import httpx
from app.core.celery_app import celery_app
from app.core.logger_setup import logging
from app.db.database import SessionLocal
from app.models.monitor import Monitor, MonitorStatus
from app.models.ping_history import PingHistory
from app.tasks.alert_tasks import send_email_alert

logger = logging.getLogger("fastapi_app")


@celery_app.task
def schedule_active_monitors():
    """

    Called by Celery Beat every minute.
    """
    current_minute = datetime.now(timezone.utc).minute

    with SessionLocal() as db:  # context manager automatically closes db instance
        active_monitors = (
            db.query(Monitor).filter(Monitor.status != MonitorStatus.paused).all()
        )

        for monitor in active_monitors:
            if current_minute % monitor.interval_minutes == 0:
                logger.info(
                    "Queuing ping task",
                    extra={"monitor_id": str(monitor.id), "url": monitor.url},
                )
                ping_website.delay(str(monitor.id), monitor.url)


@celery_app.task
def ping_website(monitor_id: str, website_url: str):
    """
    Task called by Celery Worker that makes HTTP requests.
    """
    start_time = time.time()
    status_code = None

    try:
        response = httpx.get(website_url, timeout=10.0)
        status_code = response.status_code
    except httpx.RequestError as error:
        status_code = 0
        logger.warning(
            "HTTP request timeout or network error",
            extra={"monitor_id": monitor_id, "url": website_url, "error": str(error)},
        )

    latency_ms = int((time.time() - start_time) * 1000)
    current_state_is_up = status_code > 0 and status_code < 400

    try:
        with SessionLocal() as db:
            monitor = db.query(Monitor).filetr(Monitor.id == monitor_id).first()
            if not monitor or monitor.status == "paused":
                return  # cant do anything if monitor was deleted or put on hold

            # save history: happens every minute
            new_ping = PingHistory(
                monitor_id=monitor_id,
                status_code=status_code,
                latency_ms=latency_ms,
                pinged_at=datetime.now(timezone.utc),
            )
            db.add(new_ping)

            previous_state_is_up = monitor.status == "up"

            if current_state_is_up and not previous_state_is_up:
                # website is up again ( DOWN -> UP )
                monitor.status = "up"
                logger.info(
                    "Website RECOVERED",
                    extra={"monitor_id": monitor_id, "url": website_url},
                )
                # TODO: send_recovery_alert.delay() - notify client that website is back up

            elif not current_state_is_up and previous_state_is_up:
                # website crashed ( UP -> DOWN )
                monitor.status = "down"
                logger.warning(
                    "Website WENT DOWN - Queueing alert",
                    extra={"monitor_id": monitor_id, "url": website_url},
                )
                send_email_alert.delay(
                    monitor_id=monitor_id,
                    website_url=website_url,
                    status_code=status_code,
                )
            else:
                logger.info(
                    "Ping successful. State unchanged ({monitor.status})",
                    extra={
                        "monitor_id": monitor_id,
                        "status": status_code,
                        "latency_ms": latency_ms,
                    },
                )

            db.commit()
    except Exception as db_error:
        logger.error(
            "Failed to save ping history to database",
            extra={
                "monitor_id": monitor_id,
                "url": website_url,
                "error": str(db_error),
            },
        )
        raise
