"""
Tests for CORS middleware configuration.

Covers AC3: CORS middleware is configured for frontend origin
"""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


class TestCORSMiddleware:
    """Tests for CORS middleware (AC3)"""

    def test_cors_allows_configured_origin(self):
        """Test CORS allows requests from configured frontend origin"""
        origin = settings.FRONTEND_HOST
        response = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin

    def test_cors_allows_credentials(self):
        """Test CORS allows credentials (for JWT/cookies)"""
        origin = settings.FRONTEND_HOST
        response = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.headers["access-control-allow-credentials"] == "true"

    def test_cors_allows_common_methods(self):
        """Test CORS allows common HTTP methods"""
        origin = settings.FRONTEND_HOST
        response = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )

        allowed_methods = response.headers.get("access-control-allow-methods", "")
        # FastAPI with allow_methods=["*"] returns the requested method
        assert "POST" in allowed_methods or "*" in allowed_methods

    def test_cors_allows_authorization_header(self):
        """Test CORS allows Authorization header"""
        origin = settings.FRONTEND_HOST
        response = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )

        allowed_headers = response.headers.get("access-control-allow-headers", "")
        assert "authorization" in allowed_headers.lower() or "*" in allowed_headers

    def test_cors_actual_request_includes_origin(self):
        """Test actual requests include CORS origin header"""
        origin = settings.FRONTEND_HOST
        response = client.get(
            "/health",
            headers={"Origin": origin},
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
