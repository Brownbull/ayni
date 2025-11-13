"""
Tests for configuration management and validation.

This module tests:
- Environment variable loading
- JWT_SECRET validation (minimum 64 characters)
- Fail-fast behavior on missing required variables
- Environment-specific validation (local vs production)
"""

import warnings

import pytest
from pydantic import ValidationError

from app.core.config import Settings


class TestConfigurationLoading:
    """Test configuration loads from environment variables."""

    def test_settings_loads_from_environment(self, monkeypatch):
        """Test Settings class loads configuration from environment variables."""
        # Set required environment variables
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpassword123")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "testadminpassword")
        monkeypatch.setenv("JWT_SECRET", "a" * 64)  # 64 character string
        monkeypatch.setenv("ENVIRONMENT", "local")

        settings = Settings()

        assert settings.PROJECT_NAME == "TestProject"
        assert settings.POSTGRES_SERVER == "testdb"
        assert settings.POSTGRES_USER == "testuser"
        assert settings.JWT_SECRET == "a" * 64
        assert settings.ENVIRONMENT == "local"

    def test_settings_uses_defaults_for_optional_fields(self, monkeypatch):
        """Test Settings uses default values for optional configuration."""
        # Set only required fields
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpassword123")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "testadminpassword")
        monkeypatch.setenv("JWT_SECRET", "b" * 64)
        monkeypatch.setenv("ENVIRONMENT", "local")

        settings = Settings()

        # Check defaults
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.API_V1_STR == "/api/v1"
        assert settings.POSTGRES_PORT == 5432
        assert settings.REDIS_URL == "redis://localhost:6379/0"


class TestJWTSecretValidation:
    """Test JWT_SECRET validation enforces minimum 64 characters."""

    def test_jwt_secret_minimum_length_passes_at_64_chars(self, monkeypatch):
        """Test JWT_SECRET with exactly 64 characters passes validation."""
        self._set_required_env(monkeypatch)
        monkeypatch.setenv("JWT_SECRET", "x" * 64)  # Exactly 64 characters

        settings = Settings()
        assert len(settings.JWT_SECRET) == 64

    def test_jwt_secret_minimum_length_warns_in_local_environment(
        self, monkeypatch, caplog
    ):
        """Test JWT_SECRET with <64 chars generates warning in local environment."""
        self._set_required_env(monkeypatch)
        monkeypatch.setenv("JWT_SECRET", "x" * 63)  # 63 characters
        monkeypatch.setenv("ENVIRONMENT", "local")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            settings = Settings()
            assert len(settings.JWT_SECRET) == 63
            # Check that a warning was issued
            assert len(w) > 0
            assert any(
                "JWT_SECRET must be at least 64 characters" in str(warning.message)
                for warning in w
            )

    def test_jwt_secret_minimum_length_fails_in_production(self, monkeypatch):
        """Test JWT_SECRET with <64 chars raises error in production environment."""
        self._set_required_env(monkeypatch)
        monkeypatch.setenv("JWT_SECRET", "x" * 63)  # 63 characters
        monkeypatch.setenv("ENVIRONMENT", "production")

        with pytest.raises(ValueError) as exc_info:
            Settings()

        assert "JWT_SECRET must be at least 64 characters" in str(exc_info.value)

    def test_jwt_secret_with_long_string_passes(self, monkeypatch):
        """Test JWT_SECRET with >64 characters passes validation."""
        self._set_required_env(monkeypatch)
        monkeypatch.setenv("JWT_SECRET", "y" * 128)  # 128 characters

        settings = Settings()
        assert len(settings.JWT_SECRET) == 128

    @staticmethod
    def _set_required_env(monkeypatch):
        """Helper to set required environment variables for testing."""
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "securepassword123")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "secureadminpass")


class TestFailFastValidation:
    """Test configuration fails fast on missing required variables."""

    def test_missing_jwt_secret_fails_fast(self, monkeypatch):
        """Test Settings instantiation fails when JWT_SECRET is missing."""
        # Disable loading from .env file to test validation
        monkeypatch.delenv("JWT_SECRET", raising=False)

        # Set all required fields except JWT_SECRET
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpassword123")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "testadminpassword")
        # JWT_SECRET is missing

        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)  # Disable .env file loading

        # Verify error mentions JWT_SECRET
        assert "JWT_SECRET" in str(exc_info.value)

    def test_missing_database_url_components_fails_fast(self, monkeypatch):
        """Test Settings fails when database configuration is missing."""
        # Clear database env vars to test validation
        monkeypatch.delenv("POSTGRES_SERVER", raising=False)
        monkeypatch.delenv("POSTGRES_USER", raising=False)

        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "testadminpassword")
        monkeypatch.setenv("JWT_SECRET", "z" * 64)
        # Missing POSTGRES_SERVER, POSTGRES_USER

        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)  # Disable .env file loading

        error_str = str(exc_info.value)
        assert "POSTGRES_SERVER" in error_str or "POSTGRES_USER" in error_str


class TestEnvironmentSpecificBehavior:
    """Test environment-specific validation behavior (local vs production)."""

    def test_weak_secrets_warn_in_local_environment(self, monkeypatch):
        """Test weak default secrets generate warnings in local environment."""
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "changethis")  # Weak default
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "changethis")  # Weak default
        monkeypatch.setenv("JWT_SECRET", "a" * 64)
        monkeypatch.setenv("ENVIRONMENT", "local")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Settings()

            # Check warnings were issued for weak secrets
            warning_messages = [str(warning.message) for warning in w]
            assert any("POSTGRES_PASSWORD" in msg for msg in warning_messages)
            assert any("FIRST_SUPERUSER_PASSWORD" in msg for msg in warning_messages)

    def test_weak_secrets_fail_in_production(self, monkeypatch):
        """Test weak default secrets raise errors in production environment."""
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "changethis")  # Weak default
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "secureadminpass")
        monkeypatch.setenv("JWT_SECRET", "b" * 64)
        monkeypatch.setenv("ENVIRONMENT", "production")

        with pytest.raises(ValueError) as exc_info:
            Settings()

        assert "POSTGRES_PASSWORD" in str(exc_info.value)
        assert "changethis" in str(exc_info.value)


class TestComputedFields:
    """Test computed configuration fields derive correctly."""

    def test_sqlalchemy_database_uri_builds_correctly(self, monkeypatch):
        """Test SQLALCHEMY_DATABASE_URI is built from Postgres components."""
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "mydbhost")
        monkeypatch.setenv("POSTGRES_PORT", "5433")
        monkeypatch.setenv("POSTGRES_USER", "myuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "mypassword123")
        monkeypatch.setenv("POSTGRES_DB", "mydb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "adminpass123")
        monkeypatch.setenv("JWT_SECRET", "c" * 64)
        monkeypatch.setenv("ENVIRONMENT", "local")

        settings = Settings()

        db_uri = str(settings.SQLALCHEMY_DATABASE_URI)
        assert "postgresql+asyncpg://" in db_uri
        assert "myuser" in db_uri
        assert "mydbhost" in db_uri
        assert "5433" in db_uri
        assert "mydb" in db_uri

    def test_celery_broker_uses_redis_url(self, monkeypatch):
        """Test CELERY_BROKER_URL defaults to REDIS_URL."""
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpass123")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "adminpass123")
        monkeypatch.setenv("JWT_SECRET", "d" * 64)
        monkeypatch.setenv("REDIS_URL", "redis://myredis:6379/0")
        monkeypatch.setenv("ENVIRONMENT", "local")

        settings = Settings()

        assert "redis://myredis:6379/0" in settings.CELERY_BROKER_URL
        assert "redis://myredis:6379/1" in settings.CELERY_RESULT_BACKEND

    def test_cors_origins_includes_frontend_host(self, monkeypatch):
        """Test all_cors_origins includes FRONTEND_HOST."""
        monkeypatch.setenv("PROJECT_NAME", "TestProject")
        monkeypatch.setenv("POSTGRES_SERVER", "testdb")
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpass123")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        monkeypatch.setenv("FIRST_SUPERUSER", "admin@test.com")
        monkeypatch.setenv("FIRST_SUPERUSER_PASSWORD", "adminpass123")
        monkeypatch.setenv("JWT_SECRET", "e" * 64)
        monkeypatch.setenv("FRONTEND_HOST", "http://localhost:5173")
        monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://example.com")
        monkeypatch.setenv("ENVIRONMENT", "local")

        settings = Settings()

        assert "http://localhost:5173" in settings.all_cors_origins
        assert "http://example.com" in settings.all_cors_origins
