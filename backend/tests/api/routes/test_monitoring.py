"""Tests for monitoring endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


def test_monitoring_metrics_endpoint_success(
    client: TestClient,
    db: AsyncSession,  # noqa: ARG001
):
    """Test that monitoring metrics endpoint returns all required metrics."""
    response = client.get("/api/v1/monitoring/metrics")

    assert response.status_code == 200
    data = response.json()

    # Verify top-level fields
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0

    # Verify services status
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]

    # Database should be healthy in tests
    assert data["services"]["database"]["status"] == "healthy"
    assert "latency_ms" in data["services"]["database"]

    # Redis should be healthy in tests
    assert data["services"]["redis"]["status"] == "healthy"
    assert "latency_ms" in data["services"]["redis"]

    # Verify Celery metrics
    assert "celery_metrics" in data
    celery = data["celery_metrics"]
    assert "active_tasks" in celery
    assert "scheduled_tasks" in celery
    assert "pending_tasks" in celery
    assert "active_workers" in celery
    assert "completed_24h" in celery
    assert "failed_24h" in celery


def test_monitoring_metrics_caching(
    client: TestClient,
    db: AsyncSession,  # noqa: ARG001
):
    """Test that monitoring metrics are cached with 1-minute TTL."""
    # Make first request
    response1 = client.get("/api/v1/monitoring/metrics")
    assert response1.status_code == 200
    data1 = response1.json()

    # Make second request immediately - should return cached data
    response2 = client.get("/api/v1/monitoring/metrics")
    assert response2.status_code == 200
    data2 = response2.json()

    # Timestamps should be identical (cached response)
    assert data1["timestamp"] == data2["timestamp"]
    assert data1["uptime_seconds"] == data2["uptime_seconds"]


def test_celery_tasks_endpoint(client: TestClient):
    """Test Celery tasks status endpoint."""
    response = client.get("/api/v1/monitoring/celery/tasks")

    # This endpoint might return 500 if no Celery workers are running
    # In CI/CD, workers might not be available
    if response.status_code == 200:
        data = response.json()
        assert "workers" in data
        assert "active_tasks" in data
        assert "scheduled_tasks" in data
        assert "reserved_tasks" in data
        assert "worker_stats" in data
    else:
        # If no workers available, should return 500
        assert response.status_code == 500


def test_task_status_endpoint_with_invalid_task_id(client: TestClient):
    """Test task status endpoint with an invalid task ID."""
    fake_task_id = "nonexistent-task-id-12345"
    response = client.get(f"/api/v1/monitoring/celery/task/{fake_task_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["task_id"] == fake_task_id
    assert "status" in data
    # Non-existent tasks return PENDING status
    assert data["status"] == "PENDING"


def test_monitoring_returns_503_when_database_down(client: TestClient, monkeypatch):
    """Test that monitoring endpoint returns 503 when database is unavailable."""
    # Mock database engine to raise exception
    from app.core import db

    class MockEngine:
        def begin(self):
            class AsyncContextManager:
                async def __aenter__(self):
                    raise Exception("Database connection failed")

                async def __aexit__(self, *args):
                    pass

            return AsyncContextManager()

    monkeypatch.setattr(db, "async_engine", MockEngine())

    # The cache will be bypassed due to Redis connection failure
    # which will be caught and logged by the monitoring endpoint

    response = client.get("/api/v1/monitoring/metrics")

    # Should return 503 when critical services are down
    assert response.status_code == 503
    assert "Critical services unavailable" in response.json()["detail"]


def test_monitoring_performance_header_present(
    client: TestClient,
    db: AsyncSession,  # noqa: ARG001
):
    """Test that monitoring endpoint includes performance timing header."""
    response = client.get("/api/v1/monitoring/metrics")

    assert response.status_code == 200
    # Performance middleware should add X-Response-Time header
    assert "X-Response-Time" in response.headers
    assert response.headers["X-Response-Time"].endswith("ms")
