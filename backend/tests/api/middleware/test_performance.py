"""Tests for performance monitoring middleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.middleware.performance import performance_middleware


@pytest.fixture
def app_with_performance_middleware():
    """Create a test FastAPI app with performance middleware."""
    app = FastAPI()
    app.middleware("http")(performance_middleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}

    @app.get("/slow")
    async def slow_endpoint():
        import time

        time.sleep(0.6)  # Sleep for 600ms to trigger slow request warning
        return {"message": "slow"}

    return app


def test_performance_middleware_adds_response_time_header(
    app_with_performance_middleware,
):
    """Test that performance middleware adds X-Response-Time header."""
    client = TestClient(app_with_performance_middleware)
    response = client.get("/test")

    assert response.status_code == 200
    assert "X-Response-Time" in response.headers
    assert response.headers["X-Response-Time"].endswith("ms")


def test_performance_middleware_measures_duration(app_with_performance_middleware):
    """Test that performance middleware measures request duration accurately."""
    client = TestClient(app_with_performance_middleware)
    response = client.get("/test")

    # Extract duration from header (format: "123.45ms")
    duration_str = response.headers["X-Response-Time"]
    duration_ms = float(duration_str.replace("ms", ""))

    # Duration should be positive and reasonable (< 1 second for simple endpoint)
    assert duration_ms > 0
    assert duration_ms < 1000


def test_performance_middleware_logs_slow_requests(
    app_with_performance_middleware, caplog
):
    """Test that slow requests (>500ms) are logged with warning level."""
    client = TestClient(app_with_performance_middleware)

    with caplog.at_level("WARNING"):
        response = client.get("/slow")

    assert response.status_code == 200

    # Check that slow request was logged
    assert any("Slow request detected" in record.message for record in caplog.records)

    # Verify duration is in header
    duration_str = response.headers["X-Response-Time"]
    duration_ms = float(duration_str.replace("ms", ""))
    assert duration_ms > 500  # Should be over the threshold


def test_performance_middleware_works_with_errors(app_with_performance_middleware):
    """Test that performance middleware handles endpoints that raise errors."""
    app = app_with_performance_middleware

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    client = TestClient(app)

    with pytest.raises(ValueError):
        client.get("/error")

    # Note: In production, exception handlers would catch this
    # This test verifies middleware doesn't interfere with error propagation
