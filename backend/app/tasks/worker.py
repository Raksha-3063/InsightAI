import os
from celery import Celery
from backend.app.config import settings

# Initialize Celery app
celery_app = Celery(
    "insightai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Optional configuration
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600, # 1 hour
)

# Autodiscover tasks from app.tasks.jobs
celery_app.autodiscover_tasks(["backend.app.tasks"])
