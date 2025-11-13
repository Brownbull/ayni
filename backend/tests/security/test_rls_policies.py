"""Tests for RLS Policy Detection and Enforcement (AC: 2).

This module verifies that:
1. All tables with tenant_id or company_id have RLS enabled
2. All tenant-scoped tables have proper RLS policies configured
3. Missing policies are detected and reported

CRITICAL: These tests prevent CATASTROPHIC cross-tenant data leaks.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.security.conftest import get_all_tenant_tables, get_table_rls_status

# ============================================================================
# AC2: RLS Policy Detection Tests
# ============================================================================


@pytest.mark.asyncio
async def test_all_tenant_tables_have_rls_enabled(async_db: AsyncSession):
    """Verify all tables with tenant_id/company_id have RLS enabled.

    This test scans the database schema to find all tables with tenant
    isolation columns and verifies that Row-Level Security is enabled.

    CRITICAL: If this test fails, tenant data is at risk of leaking.

    AC: 2 - Tests validate RLS policies exist on ALL tables with tenant_id
    """
    # Get all tables that should have RLS
    tenant_tables = await get_all_tenant_tables(async_db)

    assert len(tenant_tables) > 0, "No tenant tables found - schema may be incorrect"

    missing_rls = []
    for table_name in tenant_tables:
        status = await get_table_rls_status(async_db, table_name)

        if not status:
            missing_rls.append(f"{table_name}: Table not found in pg_class")
            continue

        if not status["rls_enabled"]:
            missing_rls.append(
                f"{table_name}: RLS not enabled (relrowsecurity = false)"
            )

    assert len(missing_rls) == 0, (
        f"RLS SECURITY VIOLATION: {len(missing_rls)} table(s) missing RLS protection:\n"
        + "\n".join(f"  - {issue}" for issue in missing_rls)
        + "\n\nFIX: Enable RLS with: ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"
    )


@pytest.mark.asyncio
async def test_all_tenant_tables_have_policies(async_db: AsyncSession):
    """Verify all tenant tables have at least one RLS policy configured.

    RLS must be both ENABLED and have POLICIES to actually enforce isolation.
    This test ensures policies exist, not just that RLS is enabled.

    AC: 2 - Tests validate RLS policies exist on ALL tables with tenant_id
    """
    tenant_tables = await get_all_tenant_tables(async_db)

    missing_policies = []
    for table_name in tenant_tables:
        status = await get_table_rls_status(async_db, table_name)

        if not status:
            missing_policies.append(f"{table_name}: Table not found")
            continue

        if status["policy_count"] == 0:
            missing_policies.append(
                f"{table_name}: RLS enabled but NO POLICIES configured"
            )

    assert len(missing_policies) == 0, (
        f"RLS SECURITY VIOLATION: {len(missing_policies)} table(s) have RLS enabled "
        "but NO POLICIES:\n"
        + "\n".join(f"  - {issue}" for issue in missing_policies)
        + "\n\nWARNING: RLS without policies = NO PROTECTION"
        + "\n\nFIX: Add policy with: CREATE POLICY tenant_isolation_policy ON {table_name} "
        "USING (tenant_id = current_setting('app.current_tenant')::INTEGER);"
    )


@pytest.mark.asyncio
async def test_companies_table_has_rls(async_db: AsyncSession):
    """Verify companies table specifically has RLS and policies.

    Companies is the core tenant isolation table - extra validation.

    AC: 2 - Tests validate RLS policies exist on ALL tables with tenant_id
    """
    status = await get_table_rls_status(async_db, "companies")

    assert status is not None, "companies table not found in database"
    assert status["rls_enabled"], (
        "CRITICAL: companies table does not have RLS enabled! "
        "Run: ALTER TABLE companies ENABLE ROW LEVEL SECURITY;"
    )
    assert status["policy_count"] > 0, (
        "CRITICAL: companies table has RLS enabled but no policies! "
        "Tenant isolation is NOT enforced."
    )


@pytest.mark.asyncio
async def test_locations_table_has_rls(async_db: AsyncSession):
    """Verify locations table has RLS and policies.

    Locations are scoped to companies, which are scoped to tenants.

    AC: 2 - Tests validate RLS policies exist on ALL tables with tenant_id
    """
    status = await get_table_rls_status(async_db, "locations")

    assert status is not None, "locations table not found in database"
    assert status["rls_enabled"], (
        "CRITICAL: locations table does not have RLS enabled! "
        "Run: ALTER TABLE locations ENABLE ROW LEVEL SECURITY;"
    )
    assert status["policy_count"] > 0, (
        "CRITICAL: locations table has RLS enabled but no policies! "
        "Company data isolation is NOT enforced."
    )


@pytest.mark.asyncio
async def test_user_table_has_rls(async_db: AsyncSession):
    """Verify user table has RLS and policies.

    Users must be isolated by tenant to prevent cross-tenant access.

    AC: 2 - Tests validate RLS policies exist on ALL tables with tenant_id
    """
    status = await get_table_rls_status(async_db, "user")

    assert status is not None, "user table not found in database"
    assert status["rls_enabled"], (
        "CRITICAL: user table does not have RLS enabled! "
        "Run: ALTER TABLE user ENABLE ROW LEVEL SECURITY;"
    )
    assert status["policy_count"] > 0, (
        "CRITICAL: user table has RLS enabled but no policies! "
        "User isolation is NOT enforced."
    )


@pytest.mark.asyncio
async def test_no_bypass_rls_grants_exist(async_db: AsyncSession):
    """Verify no users have BYPASSRLS privilege (except superuser).

    If application database user has BYPASSRLS, RLS policies are ignored.
    This would be a CATASTROPHIC security vulnerability.

    NOTE: This test is EXPECTED TO FAIL in test/development environments where
    the test database user has BYPASSRLS for setup/teardown purposes. In PRODUCTION,
    the application database user MUST NOT have BYPASSRLS privilege.

    PRODUCTION REQUIREMENT: Before deployment, verify that the application's
    database user does NOT have BYPASSRLS privilege using:
    SELECT rolname, rolbypassrls FROM pg_roles WHERE rolname = '<app_user>';

    AC: 2 - Tests validate RLS policies exist on ALL tables with tenant_id
    """
    from sqlalchemy import text

    query = text(
        """
        SELECT rolname, rolbypassrls
        FROM pg_roles
        WHERE rolname NOT LIKE 'pg_%'  -- Exclude system roles
          AND rolname != 'postgres'     -- Exclude superuser
          AND rolbypassrls = true
    """
    )

    result = await async_db.execute(query)
    bypass_users = result.fetchall()

    assert len(bypass_users) == 0, (
        f"RLS SECURITY VIOLATION: {len(bypass_users)} user(s) have BYPASSRLS privilege:\n"
        + "\n".join(f"  - {row[0]}" for row in bypass_users)
        + "\n\nWARNING: These users can see ALL tenant data regardless of RLS policies!"
        + "\n\nFIX: REVOKE BYPASSRLS privilege from application database users."
    )
