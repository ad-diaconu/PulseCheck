import os

from celery import Celery
from celery.schedules import crontab

redis_url = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pulsecheck_worker",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks.ping_tasks", "app.tasks.alert_tasks"],
)

celery_app.conf.beat_schedule = {
    "schedule=pings-every-minute": {
        "task": "app.tasks.ping_tasks.schedule_active_monitors",
        "schedule": crontab(minute="*"),
    }
}
