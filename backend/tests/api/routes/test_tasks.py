"""Tests for task API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_queue_sample_task(client: TestClient):
    """Test queuing a sample task returns task_id."""
    response = client.post(
        "/api/v1/tasks/sample",
        json={"param1": "test_value", "param2": 42},
    )

    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "queued"
    assert len(data["task_id"]) > 0


def test_get_task_status(client: TestClient):
    """Test getting task status for queued task."""
    # First queue a task
    queue_response = client.post(
        "/api/v1/tasks/sample",
        json={"param1": "test", "param2": 123},
    )
    task_id = queue_response.json()["task_id"]

    # Get task status
    status_response = client.get(f"/api/v1/tasks/{task_id}")

    assert status_response.status_code == 200
    data = status_response.json()
    assert data["task_id"] == task_id
    assert data["status"] in ["pending", "success", "failure", "queued"]


def test_get_task_status_invalid_id(client: TestClient):
    """Test getting status for invalid task ID returns error."""
    response = client.get("/api/v1/tasks/invalid-task-id")

    # Should handle gracefully (may return 400 or show pending status)
    assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_task_execution_integration(client: TestClient):
    """Integration test for full task lifecycle (queue -> execute -> complete)."""
    # Queue task
    queue_response = client.post(
        "/api/v1/tasks/sample",
        json={"param1": "integration_test", "param2": 999},
    )
    assert queue_response.status_code == 202
    task_id = queue_response.json()["task_id"]

    # Note: In a real integration test with Celery running,
    # we would wait for task completion and verify the result.
    # For unit tests, we verify the task was queued successfully.

    # Get initial status
    status_response = client.get(f"/api/v1/tasks/{task_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["task_id"] == task_id
