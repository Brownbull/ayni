"""Celery background tasks.

This module contains background task definitions with retry policies and error handling.
Tasks use the @celery_app.task decorator with bind=True for access to task context.
"""
import time
from typing import Any

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.sample_task")
def sample_task(self, param1: str, param2: int) -> dict[str, Any]:
    """Sample background task demonstrating Celery functionality.

    This task simulates processing work and demonstrates:
    - Task binding for retry access
    - Exponential backoff retry policy
    - Result serialization

    Args:
        self: Task instance (available because bind=True)
        param1: Sample string parameter
        param2: Sample integer parameter

    Returns:
        dict: Task result with status and data

    Raises:
        Exception: On failure, triggers retry with exponential backoff
    """
    try:
        # Simulate some work
        time.sleep(2)

        result = {
            "status": "success",
            "message": f"Processed task with param1='{param1}' and param2={param2}",
            "task_id": self.request.id,
            "retries": self.request.retries,
        }

        return result

    except Exception as exc:
        # Exponential backoff: 60s, 120s, 240s
        countdown = 60 * (2**self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
