"""Celery application configuration with Redis broker and result backend.

This module initializes the Celery app with:
- Redis as message broker (database 0)
- Redis as result backend (database 1)
- Task routing and retry policies
- JSON serialization for security
"""
from celery import Celery

from app.core.config import settings

# Initialize Celery with broker and result backend
celery_app = Celery(
    "ayni",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    # Task serialization (JSON is secure and cross-language compatible)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task routing (default queue for MVP, can add fast/slow queues later)
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    # Result expiration
    result_expires=3600,  # 1 hour
    # Task retry settings (exponential backoff)
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Monitoring and events (enable for Flower and task tracking)
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_track_started=True,
)

# Auto-discover tasks from workers.tasks module
celery_app.autodiscover_tasks(["app.workers"])
