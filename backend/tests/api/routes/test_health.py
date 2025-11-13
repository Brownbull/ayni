"""
Tests for health check endpoints.

Covers:
- AC1: Basic /health endpoint returns 200 with {"status": "healthy"}
- AC2: Detailed /api/v1/health endpoint returns service status
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestBasicHealthEndpoint:
    """Tests for basic health endpoint (AC1)"""

    def test_health_endpoint_returns_200(self):
        """Test basic health endpoint returns 200 status code"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_correct_format(self):
        """Test basic health endpoint returns {"status": "healthy"}"""
        response = client.get("/health")
        data = response.json()
        assert data == {"status": "healthy"}

    def test_health_endpoint_accessible_without_authentication(self):
        """Test basic health endpoint doesn't require authentication"""
        # No Authorization header provided
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestDetailedHealthEndpoint:
    """Tests for detailed health endpoint (AC2)"""

    @pytest.mark.asyncio
    async def test_detailed_health_endpoint_structure(self, client: TestClient):
        """Test detailed health endpoint returns correct structure"""
        response = client.get("/api/v1/health")

        # Should return regardless of database status
        assert response.status_code in [200, 503]

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert "database" in data["services"]

    @pytest.mark.asyncio
    async def test_detailed_health_database_check(self, client: TestClient):
        """Test detailed health endpoint checks database"""
        response = client.get("/api/v1/health")
        data = response.json()

        # Database service should be checked
        assert "database" in data["services"]
        db_status = data["services"]["database"]

        # Should have either status with latency_ms or error
        assert "status" in db_status
        if db_status["status"] == "healthy":
            assert "latency_ms" in db_status
            assert isinstance(db_status["latency_ms"], int | float)
        else:
            assert "error" in db_status

    @pytest.mark.asyncio
    async def test_detailed_health_redis_check(self, client: TestClient):
        """Test detailed health endpoint includes Redis status"""
        response = client.get("/api/v1/health")
        data = response.json()

        # Redis should be checked (Story 1.4 implementation)
        assert "redis" in data["services"]
        redis_status = data["services"]["redis"]

        # Should have either status with latency_ms or error
        assert "status" in redis_status
        if redis_status["status"] == "healthy":
            assert "latency_ms" in redis_status
            assert isinstance(redis_status["latency_ms"], int | float)
        else:
            # If Redis is down, should be degraded not unhealthy
            assert "error" in redis_status

    @pytest.mark.asyncio
    async def test_detailed_health_returns_503_when_database_unhealthy(
        self, client: TestClient
    ):
        """Test detailed health endpoint returns 503 when database connection fails"""
        # Override the dependency to return a mocked session
        from app.api.deps import get_db

        mock_db = AsyncMock()
        mock_db.execute.side_effect = Exception("Database connection failed")

        async def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            response = client.get("/api/v1/health")

            # Should return 503 Service Unavailable
            assert response.status_code == 503

            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["services"]["database"]["status"] == "unhealthy"
            assert "error" in data["services"]["database"]
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_detailed_health_returns_503_when_redis_unhealthy(
        self, client: TestClient
    ):
        """Test detailed health endpoint returns 503 (degraded) when Redis is down.

        This test addresses the critical bug from Story 1.3 where health endpoint
        calculated status_code but always returned 200. This ensures Redis failures
        properly return 503 status code.
        """
        from unittest.mock import AsyncMock, patch

        from app.api.deps import get_db
        from app.core.redis import RedisClient

        # Override database dependency to return a healthy mocked session
        mock_db = AsyncMock()
        # Mock successful database query execution
        mock_db.execute.return_value = None  # Successful SELECT 1

        async def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # Mock Redis to raise connection error
            with patch.object(
                RedisClient,
                "get_client",
                side_effect=Exception("Redis connection failed"),
            ):
                response = client.get("/api/v1/health")

                # Should return 503 Service Unavailable (degraded)
                assert response.status_code == 503

                data = response.json()
                assert data["status"] == "degraded"
                assert data["services"]["redis"]["status"] == "unhealthy"
                assert "error" in data["services"]["redis"]
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()
