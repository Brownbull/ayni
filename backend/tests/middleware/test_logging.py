"""
Tests for request logging middleware.

Covers AC4: Request logging middleware captures all requests with request IDs
"""

import logging

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRequestLoggingMiddleware:
    """Tests for request logging middleware (AC4)"""

    def test_request_id_in_response_headers(self):
        """Test that request_id is added to response headers"""
        response = client.get("/health")

        assert "x-request-id" in response.headers
        request_id = response.headers["x-request-id"]

        # Verify it's a UUID format (contains hyphens)
        assert "-" in request_id
        assert len(request_id) == 36  # UUID v4 format: 8-4-4-4-12

    def test_unique_request_ids_for_each_request(self):
        """Test that each request gets a unique request_id"""
        response1 = client.get("/health")
        response2 = client.get("/health")

        request_id1 = response1.headers["x-request-id"]
        request_id2 = response2.headers["x-request-id"]

        assert request_id1 != request_id2

    def test_middleware_logs_request(self, caplog):
        """Test that middleware logs incoming requests"""
        with caplog.at_level(logging.INFO, logger="ayni.api"):
            client.get("/health")

            # Check for request log
            request_logs = [
                r for r in caplog.records if "Incoming request" in r.message
            ]
            assert len(request_logs) > 0

            # Verify request log contains expected fields
            request_log = request_logs[-1]
            assert "request_id" in request_log.__dict__
            assert "method" in request_log.__dict__
            assert "path" in request_log.__dict__

    def test_middleware_logs_response(self, caplog):
        """Test that middleware logs outgoing responses"""
        with caplog.at_level(logging.INFO, logger="ayni.api"):
            client.get("/health")

            # Check for response log
            response_logs = [
                r for r in caplog.records if "Outgoing response" in r.message
            ]
            assert len(response_logs) > 0

            # Verify response log contains expected fields
            response_log = response_logs[-1]
            assert "request_id" in response_log.__dict__
            assert "status_code" in response_log.__dict__
            assert "duration_ms" in response_log.__dict__

    def test_same_request_id_in_request_and_response_logs(self, caplog):
        """Test that same request_id appears in both request and response logs"""
        with caplog.at_level(logging.INFO, logger="ayni.api"):
            response = client.get("/health")
            response_request_id = response.headers["x-request-id"]

            # Get request and response logs for this request
            request_logs = [
                r for r in caplog.records if "Incoming request" in r.message
            ]
            response_logs = [
                r for r in caplog.records if "Outgoing response" in r.message
            ]

            assert len(request_logs) > 0
            assert len(response_logs) > 0

            # Verify request_id matches across logs and response header
            request_log_id = request_logs[-1].__dict__["request_id"]
            response_log_id = response_logs[-1].__dict__["request_id"]

            assert request_log_id == response_log_id
            assert request_log_id == response_request_id
