"""Tests for Alembic database migrations.

This test module verifies:
- AC3: Migrations can upgrade successfully
- AC3: Migrations can downgrade successfully (rollback)
- Migration idempotency (running upgrade multiple times)
"""

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from app.core.db import engine


@pytest.fixture(scope="module")
def alembic_config():
    """Create Alembic config for testing"""
    config = Config("backend/app/alembic.ini")
    config.set_main_option("script_location", "backend/app/alembic")
    return config


def test_migration_upgrade(alembic_config):
    """Test that migration upgrade works successfully (AC3)"""
    # Run upgrade to head
    command.upgrade(alembic_config, "head")

    # Verify key tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "tenants" in tables
    assert "companies" in tables
    assert "locations" in tables
    assert "user" in tables


def test_migration_downgrade(alembic_config):
    """Test that migration downgrade (rollback) works successfully (AC3)"""
    # First upgrade to head
    command.upgrade(alembic_config, "head")

    # Get current revision
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current_revision = result.scalar()

    # Downgrade one step
    command.downgrade(alembic_config, "-1")

    # Verify we moved back a revision
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        new_revision = result.scalar()

    assert new_revision != current_revision, "Revision should change after downgrade"


def test_migration_idempotency(alembic_config):
    """Test that running migration multiple times is safe"""
    # Run upgrade twice
    command.upgrade(alembic_config, "head")
    command.upgrade(alembic_config, "head")  # Should not fail

    # Verify tables still exist and are correct
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "tenants" in tables
    assert "companies" in tables
    assert "locations" in tables


def test_migration_creates_indexes(alembic_config):
    """Verify that migration creates proper indexes on tenant_id and company_id"""
    command.upgrade(alembic_config, "head")

    inspector = inspect(engine)

    # Check indexes on users table
    user_indexes = inspector.get_indexes("user")
    user_index_columns = [idx.get("column_names", []) for idx in user_indexes]
    assert any(
        "tenant_id" in cols for cols in user_index_columns
    ), "user table should have index on tenant_id"

    # Check indexes on companies table
    company_indexes = inspector.get_indexes("companies")
    company_index_columns = [idx.get("column_names", []) for idx in company_indexes]
    assert any(
        "tenant_id" in cols for cols in company_index_columns
    ), "companies table should have index on tenant_id"

    # Check indexes on locations table
    location_indexes = inspector.get_indexes("locations")
    location_index_columns = [idx.get("column_names", []) for idx in location_indexes]
    assert any(
        "company_id" in cols for cols in location_index_columns
    ), "locations table should have index on company_id"
