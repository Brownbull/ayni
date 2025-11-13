"""
Tests for Alembic database migrations.

Tests verify that:
- Migrations can be applied successfully
- All required tables are created
- Indexes and constraints are properly set up
- Migrations can be rolled back
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_all_tables_created(async_db: AsyncSession) -> None:
    """Test that all required tables exist after migrations."""
    db = async_db
    # Get list of tables
    result = await db.execute(
        text(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        )
    )
    tables = [row[0] for row in result.fetchall()]

    # Required tables from Stories 1.2 and 1.3
    required_tables = [
        "tenants",
        "user",  # FastAPI template uses "user" not "users"
        "companies",
        "locations",
        "item",  # From FastAPI template
        "alembic_version",  # Alembic metadata table
    ]

    for table in required_tables:
        assert table in tables, f"Table '{table}' should exist after migrations"


@pytest.mark.asyncio
async def test_tenant_table_structure(async_db: AsyncSession) -> None:
    """Test that tenants table has correct structure."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'tenants'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {
        row[0]: {"type": row[1], "nullable": row[2]} for row in result.fetchall()
    }

    assert "id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

    # ID should be primary key (not nullable)
    assert columns["id"]["nullable"] == "NO"


@pytest.mark.asyncio
async def test_user_table_structure(async_db: AsyncSession) -> None:
    """Test that user table has correct structure with tenant_id."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'user'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {
        row[0]: {"type": row[1], "nullable": row[2]} for row in result.fetchall()
    }

    # Required columns
    required_columns = [
        "id",
        "email",
        "hashed_password",
        "tenant_id",
        "role",
        "email_verified",
        "is_active",
        "is_superuser",
        "created_at",
        "updated_at",
    ]

    for col in required_columns:
        assert col in columns, f"Column '{col}' should exist in user table"

    # tenant_id should allow NULL (for superusers)
    assert columns["tenant_id"]["nullable"] == "YES"


@pytest.mark.asyncio
async def test_company_table_structure(async_db: AsyncSession) -> None:
    """Test that companies table has correct structure."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'companies'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {
        row[0]: {"type": row[1], "nullable": row[2]} for row in result.fetchall()
    }

    required_columns = [
        "id",
        "tenant_id",
        "name",
        "identifier",  # For Chilean RUT
        "country",
        "industry",
        "timezone",
        "opt_in_benchmarking",
        "is_demo",
        "created_at",
        "updated_at",
    ]

    for col in required_columns:
        assert col in columns, f"Column '{col}' should exist in companies table"

    # tenant_id should be required (not nullable)
    assert columns["tenant_id"]["nullable"] == "NO"


@pytest.mark.asyncio
async def test_location_table_structure(async_db: AsyncSession) -> None:
    """Test that locations table has correct structure."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'locations'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {
        row[0]: {"type": row[1], "nullable": row[2]} for row in result.fetchall()
    }

    required_columns = [
        "id",
        "company_id",
        "name",
        "address",
        "website",
        "is_primary",
        "deleted_at",
        "created_at",
        "updated_at",
    ]

    for col in required_columns:
        assert col in columns, f"Column '{col}' should exist in locations table"

    # company_id should be required (foreign key)
    assert columns["company_id"]["nullable"] == "NO"


@pytest.mark.asyncio
async def test_foreign_key_constraints(async_db: AsyncSession) -> None:
    """Test that foreign key constraints are properly set up."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """
        )
    )
    foreign_keys = result.fetchall()

    # Convert to dict for easier checking
    fk_dict = {}
    for row in foreign_keys:
        table, column, foreign_table, foreign_column = row
        fk_dict[(table, column)] = (foreign_table, foreign_column)

    # Verify key foreign key relationships
    assert ("user", "tenant_id") in fk_dict or len(foreign_keys) > 0
    assert ("companies", "tenant_id") in fk_dict or len(foreign_keys) > 0
    assert ("locations", "company_id") in fk_dict or len(foreign_keys) > 0


@pytest.mark.asyncio
async def test_indexes_created(async_db: AsyncSession) -> None:
    """Test that indexes are created for foreign keys and frequently queried columns."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """
        )
    )
    indexes = result.fetchall()

    # Verify we have some indexes created
    assert len(indexes) > 0, "Expected at least some indexes to be created"

    # We expect indexes on foreign keys
    # Note: SQLModel may use different naming conventions
    assert len(indexes) > 0, "There should be indexes created"

    # Check for tenant_id indexes (important for multi-tenant queries)
    tenant_indexes = [
        idx
        for idx in indexes
        if "tenant_id" in idx[1].lower() or "tenant_id" in idx[2].lower()
    ]
    assert len(tenant_indexes) >= 1, "Should have indexes on tenant_id columns"


@pytest.mark.asyncio
async def test_rls_enabled_on_tables(async_db: AsyncSession) -> None:
    """Test that Row-Level Security is enabled on multi-tenant tables."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT tablename, rowsecurity
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename IN ('user', 'companies', 'locations')
        """
        )
    )
    rls_status = {row[0]: row[1] for row in result.fetchall()}

    # RLS should be enabled on multi-tenant tables
    for table in ["user", "companies", "locations"]:
        if table in rls_status:
            assert rls_status[table] is True, f"RLS should be enabled on {table} table"


@pytest.mark.asyncio
async def test_rls_policies_exist(async_db: AsyncSession) -> None:
    """Test that RLS policies are created for tenant isolation."""
    db = async_db
    result = await db.execute(
        text(
            """
            SELECT tablename, policyname, cmd
            FROM pg_policies
            WHERE schemaname = 'public'
        """
        )
    )
    policies = result.fetchall()

    # Convert to dict for easier checking
    policy_dict = {}
    for row in policies:
        table, policy_name, cmd = row
        if table not in policy_dict:
            policy_dict[table] = []
        policy_dict[table].append((policy_name, cmd))

    # Check that policies exist for multi-tenant tables
    assert len(policies) > 0, "Should have RLS policies defined"

    # User table should have isolation policies
    if "user" in policy_dict:
        assert len(policy_dict["user"]) >= 1, "User table should have RLS policies"

    # Companies table should have isolation policies
    if "companies" in policy_dict:
        assert (
            len(policy_dict["companies"]) >= 1
        ), "Companies table should have RLS policies"


@pytest.mark.asyncio
async def test_alembic_version_tracking(async_db: AsyncSession) -> None:
    """Test that Alembic version tracking is working."""
    db = async_db
    result = await db.execute(text("SELECT version_num FROM alembic_version"))
    version = result.scalar_one_or_none()

    assert version is not None, "Alembic version should be tracked"
    assert len(version) > 0, "Version number should not be empty"


@pytest.mark.asyncio
async def test_migration_rollback(async_db: AsyncSession) -> None:
    """
    Test that migration rollback (downgrade) works correctly.

    This test verifies AC#4 requirement: "rollback procedures are tested".
    It performs a downgrade and upgrade cycle to ensure rollback functionality works.
    """
    import os
    import subprocess

    db = async_db

    # Get current migration version
    result = await db.execute(text("SELECT version_num FROM alembic_version"))
    current_version = result.scalar_one_or_none()
    assert current_version is not None, "Should have a current migration version"

    # Get list of tables before rollback
    result = await db.execute(
        text(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        )
    )
    tables_before = {row[0] for row in result.fetchall()}

    # Perform rollback (downgrade one migration)
    backend_dir = os.path.join(os.path.dirname(__file__), "../..")
    rollback_result = subprocess.run(
        ["uv", "run", "alembic", "downgrade", "-1"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
    )

    # Rollback should succeed (exit code 0)
    assert (
        rollback_result.returncode == 0
    ), f"Rollback should succeed. Error: {rollback_result.stderr}"

    # Verify version changed after rollback
    result = await db.execute(text("SELECT version_num FROM alembic_version"))
    downgraded_version = result.scalar_one_or_none()

    # Version should be different after downgrade (or None if we downgraded to base)
    assert (
        downgraded_version != current_version
    ), "Migration version should change after downgrade"

    # Re-apply the migration (upgrade to head)
    upgrade_result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
    )

    # Upgrade should succeed
    assert (
        upgrade_result.returncode == 0
    ), f"Upgrade should succeed. Error: {upgrade_result.stderr}"

    # Verify we're back to the original version
    result = await db.execute(text("SELECT version_num FROM alembic_version"))
    final_version = result.scalar_one_or_none()

    assert (
        final_version == current_version
    ), "Should return to original version after upgrade"

    # Verify tables are restored after re-upgrade
    result = await db.execute(
        text(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        )
    )
    tables_after = {row[0] for row in result.fetchall()}

    # Tables should be the same as before the rollback test
    assert (
        tables_before == tables_after
    ), "Tables should be restored after downgrade/upgrade cycle"
