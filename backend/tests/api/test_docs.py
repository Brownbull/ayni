"""
Tests for API documentation auto-generation.

Covers AC6: API documentation is auto-generated at /docs (Swagger UI)
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestAPIDocumentation:
    """Tests for API documentation (AC6)"""

    def test_swagger_ui_accessible(self):
        """Test Swagger UI is accessible at /docs"""
        response = client.get("/docs")

        assert response.status_code == 200
        # Swagger UI returns HTML
        assert "text/html" in response.headers["content-type"]
        # Verify it's actually Swagger UI content
        assert b"swagger" in response.content.lower()

    def test_redoc_accessible(self):
        """Test ReDoc is accessible at /redoc"""
        response = client.get("/redoc")

        assert response.status_code == 200
        # ReDoc returns HTML
        assert "text/html" in response.headers["content-type"]
        # Verify it's actually ReDoc content
        assert b"redoc" in response.content.lower()

    def test_openapi_schema_accessible(self):
        """Test OpenAPI schema is accessible"""
        response = client.get("/api/v1/openapi.json")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_openapi_has_metadata(self):
        """Test OpenAPI schema includes title, version, description"""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        info = schema["info"]
        assert "title" in info
        assert "version" in info
        # Title should be set from settings.PROJECT_NAME
        assert len(info["title"]) > 0

    def test_health_endpoints_in_documentation(self):
        """Test health endpoints appear in OpenAPI documentation"""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        paths = schema["paths"]

        # Basic health endpoint should be documented
        assert "/health" in paths
        assert "get" in paths["/health"]

        # Detailed health endpoint should be documented
        assert "/api/v1/health" in paths
        assert "get" in paths["/api/v1/health"]

    def test_health_endpoint_has_response_schema(self):
        """Test health endpoints have response schemas defined"""
        response = client.get("/api/v1/openapi.json")
        schema = response.json()

        # Check basic health endpoint has 200 response
        basic_health = schema["paths"]["/health"]["get"]
        assert "responses" in basic_health
        assert "200" in basic_health["responses"]

        # Check detailed health endpoint has responses
        detailed_health = schema["paths"]["/api/v1/health"]["get"]
        assert "responses" in detailed_health
        assert "200" in detailed_health["responses"]
