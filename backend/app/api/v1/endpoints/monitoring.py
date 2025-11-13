"""Monitoring and metrics endpoints for observability."""

import logging
import time
from datetime import datetime, timezone

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.cache import cache_result
from app.core.db import async_engine
from app.core.redis import RedisClient
from app.workers.celery_app import celery_app

logger = logging.getLogger("ayni.api.monitoring")
router = APIRouter()

# Application startup time for uptime calculation
APP_START_TIME = time.time()


@router.get("/metrics")
@cache_result(ttl=60, key_prefix="monitoring_metrics")
async def get_monitoring_metrics():
    """
    Get comprehensive monitoring metrics for the application.

    Returns:
        Monitoring metrics including uptime, error rates, API performance,
        Celery task stats, and service health status.

    Returns 503 if critical services (database or Redis) are down.
    """
    try:
        # Calculate uptime
        uptime_seconds = int(time.time() - APP_START_TIME)

        # Check service health
        services_status = await check_services_health()

        # Get Celery metrics
        celery_metrics = await get_celery_metrics()

        # Build metrics response
        metrics = {
            "status": "healthy" if services_status["all_healthy"] else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": uptime_seconds,
            "services": services_status["services"],
            "celery_metrics": celery_metrics,
        }

        # Return 503 if critical services are down
        if not services_status["all_healthy"]:
            raise HTTPException(
                status_code=503,
                detail="Critical services unavailable",
            )

        return metrics

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get monitoring metrics", extra={"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve monitoring metrics",
        ) from e


async def check_services_health() -> dict:
    """Check health status of critical services."""
    services = {}
    all_healthy = True

    # Check database
    try:
        start = time.time()
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start) * 1000, 2)
        services["database"] = {"status": "healthy", "latency_ms": latency_ms}
    except Exception as e:
        logger.error("Database health check failed", extra={"error": str(e)})
        services["database"] = {"status": "unhealthy", "error": str(e)}
        all_healthy = False

    # Check Redis
    try:
        start = time.time()
        redis_client = await RedisClient.get_client()
        await redis_client.ping()
        latency_ms = round((time.time() - start) * 1000, 2)
        services["redis"] = {"status": "healthy", "latency_ms": latency_ms}
    except Exception as e:
        logger.error("Redis health check failed", extra={"error": str(e)})
        services["redis"] = {"status": "unhealthy", "error": str(e)}
        all_healthy = False

    return {"services": services, "all_healthy": all_healthy}


async def get_celery_metrics() -> dict:
    """Get Celery task metrics using inspect API."""
    try:
        # Get Celery inspector
        inspect = celery_app.control.inspect()

        # Get active tasks
        active_tasks = inspect.active() or {}
        active_count = sum(len(tasks) for tasks in active_tasks.values())

        # Get scheduled tasks
        scheduled_tasks = inspect.scheduled() or {}
        scheduled_count = sum(len(tasks) for tasks in scheduled_tasks.values())

        # Get reserved tasks (queued but not started)
        reserved_tasks = inspect.reserved() or {}
        reserved_count = sum(len(tasks) for tasks in reserved_tasks.values())

        # Get worker stats
        stats = inspect.stats() or {}
        active_workers = len(stats)

        # Calculate task counts for last 24 hours (approximation using Redis)
        completed_24h, failed_24h = await get_task_counts_24h()

        return {
            "active_tasks": active_count,
            "scheduled_tasks": scheduled_count,
            "pending_tasks": reserved_count,
            "active_workers": active_workers,
            "completed_24h": completed_24h,
            "failed_24h": failed_24h,
        }

    except Exception as e:
        logger.error("Failed to get Celery metrics", extra={"error": str(e)})
        return {
            "active_tasks": 0,
            "scheduled_tasks": 0,
            "pending_tasks": 0,
            "active_workers": 0,
            "completed_24h": 0,
            "failed_24h": 0,
            "error": "Failed to retrieve Celery metrics",
        }


async def get_task_counts_24h() -> tuple[int, int]:
    """
    Get completed and failed task counts for the last 24 hours.

    This is an approximation using Redis result backend.
    For production, consider using a time-series database.
    """
    try:
        _ = await RedisClient.get_client()

        # Get task IDs from the last 24 hours (stored in Redis result backend)
        # This is a simplified implementation
        # In production, you'd want to track task completion in a time-series DB

        completed = 0
        failed = 0

        # For MVP, return placeholder values
        # TODO: Implement proper task tracking with time-series data
        return completed, failed

    except Exception as e:
        logger.warning("Failed to get task counts", extra={"error": str(e)})
        return 0, 0


@router.get("/celery/tasks")
async def get_celery_tasks():
    """
    Get current Celery task status from all workers.

    Returns:
        Active, scheduled, and reserved tasks from all Celery workers.
    """
    try:
        inspect = celery_app.control.inspect()

        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}
        stats = inspect.stats() or {}

        return {
            "workers": list(stats.keys()),
            "active_tasks": active,
            "scheduled_tasks": scheduled,
            "reserved_tasks": reserved,
            "worker_stats": stats,
        }

    except Exception as e:
        logger.error("Failed to get Celery tasks", extra={"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve Celery task status",
        ) from e


@router.get("/celery/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of a specific Celery task.

    Args:
        task_id: Celery task ID

    Returns:
        Task status, result, and metadata
    """
    try:
        result = AsyncResult(task_id, app=celery_app)

        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "traceback": result.traceback if result.failed() else None,
        }

    except Exception as e:
        logger.error(
            "Failed to get task status", extra={"task_id": task_id, "error": str(e)}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task status for {task_id}",
        ) from e
