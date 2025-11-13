"""Tests for Cross-Tenant Data Access Prevention (AC: 1, 5).

This module verifies that:
1. Tenant A cannot query Tenant B's data through RLS policies
2. Direct database queries respect RLS policies
3. Cross-tenant access attempts return 0 results

CRITICAL: These tests prevent CATASTROPHIC cross-tenant data leaks.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Company, Location
from tests.security.conftest import attempt_cross_tenant_query

# ============================================================================
# AC1, AC5: Cross-Tenant Isolation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_tenant_a_cannot_access_tenant_b_companies(
    async_db: AsyncSession, create_test_companies, set_rls_context
):
    """Test Scenario 1: Set RLS context to Tenant A, attempt to query Tenant B's companies.

    CRITICAL: If this test fails, tenants can see each other's company data.

    AC: 1 - Automated tests attempt cross-tenant data access and verify all attempts are blocked
    AC: 5 - Test suite includes scenario: User A attempts to query User B's company data
    """
    company_a, company_b = create_test_companies

    # Set RLS context to Tenant A (tenant_id=100)
    await set_rls_context(async_db, tenant_id=company_a.tenant_id)

    # Attempt to query Company B's data (tenant_id=200)
    result = await async_db.execute(select(Company).where(Company.id == company_b.id))
    companies = result.fetchall()

    # CRITICAL: Should return 0 results (RLS blocks access)
    assert len(companies) == 0, (
        f"RLS VIOLATION: Tenant {company_a.tenant_id} accessed Company {company_b.id} "
        f"belonging to Tenant {company_b.tenant_id}!"
        f"\n\nCRITICAL SECURITY BREACH: Cross-tenant data leak detected."
    )


@pytest.mark.asyncio
async def test_tenant_b_cannot_access_tenant_a_companies(
    async_db: AsyncSession, create_test_companies, set_rls_context
):
    """Test Scenario 2: Set RLS context to Tenant B, attempt to query Tenant A's companies.

    Reverse test to ensure RLS works bidirectionally.

    AC: 1 - Automated tests attempt cross-tenant data access and verify all attempts are blocked
    AC: 5 - Test suite includes scenario: User A attempts to query User B's company data
    """
    company_a, company_b = create_test_companies

    # Set RLS context to Tenant B (tenant_id=200)
    await set_rls_context(async_db, tenant_id=company_b.tenant_id)

    # Attempt to query Company A's data (tenant_id=100)
    result = await async_db.execute(select(Company).where(Company.id == company_a.id))
    companies = result.fetchall()

    # CRITICAL: Should return 0 results (RLS blocks access)
    assert len(companies) == 0, (
        f"RLS VIOLATION: Tenant {company_b.tenant_id} accessed Company {company_a.id} "
        f"belonging to Tenant {company_a.tenant_id}!"
        f"\n\nCRITICAL SECURITY BREACH: Cross-tenant data leak detected."
    )


@pytest.mark.asyncio
async def test_tenant_a_cannot_access_tenant_b_locations(
    async_db: AsyncSession, create_test_locations, set_rls_context
):
    """Test cross-tenant isolation at the locations level.

    Locations are company-scoped, which are tenant-scoped.
    Must verify isolation works through the relationship chain.

    AC: 1 - Automated tests attempt cross-tenant data access and verify all attempts are blocked
    AC: 5 - Test suite includes scenario: User A attempts to query User B's company data
    """
    data = create_test_locations
    company_a = data["company_a"]
    company_b = data["company_b"]
    company_b_locations = data["company_b_locations"]

    # Set RLS context to Company A's tenant (tenant_id=100)
    await set_rls_context(async_db, tenant_id=company_a.tenant_id)

    # Attempt to query Company B's locations
    result = await async_db.execute(
        select(Location).where(Location.company_id == company_b.id)
    )
    locations = result.fetchall()

    # CRITICAL: Should return 0 results (RLS blocks access through company relationship)
    assert len(locations) == 0, (
        f"RLS VIOLATION: Tenant {company_a.tenant_id} accessed {len(locations)} locations "
        f"belonging to Company {company_b.id} (Tenant {company_b.tenant_id})!"
        f"\n\nExpected 0 locations, got {len(locations)}"
        f"\n\nLeaked location IDs: {[loc[0].id for loc in locations]}"
    )


@pytest.mark.asyncio
async def test_direct_database_query_bypassing_application(
    async_db: AsyncSession, create_test_companies, set_rls_context
):
    """Test Scenario 3: Direct database query (bypassing app) with wrong tenant context.

    Even if an attacker bypasses the application layer and queries the database
    directly, RLS policies should still enforce tenant isolation.

    AC: 1 - Automated tests attempt cross-tenant data access and verify all attempts are blocked
    AC: 5 - Direct database query bypassing application layer
    """
    company_a, company_b = create_test_companies

    # Set RLS context to Tenant A
    await set_rls_context(async_db, tenant_id=company_a.tenant_id)

    # Direct SQL query attempting to access Company B's data
    # This simulates an attacker with direct database access
    raw_query = text("SELECT * FROM companies WHERE id = :company_id")
    result = await async_db.execute(raw_query, {"company_id": company_b.id})
    companies = result.fetchall()

    # CRITICAL: Should return 0 results (RLS blocks at database level)
    assert len(companies) == 0, (
        f"RLS VIOLATION: Direct database query bypassed tenant isolation!"
        f"\n\nTenant {company_a.tenant_id} accessed Company {company_b.id} "
        f"(Tenant {company_b.tenant_id}) via raw SQL query."
        f"\n\nCRITICAL: RLS policies are not enforced at the database level!"
    )


@pytest.mark.asyncio
async def test_querying_all_companies_only_returns_own_tenant(
    async_db: AsyncSession, create_test_companies, set_rls_context
):
    """Test that SELECT * queries only return current tenant's data.

    Application might do `SELECT * FROM companies` for a list view.
    RLS must ensure only the current tenant's companies are returned.

    AC: 1 - Automated tests attempt cross-tenant data access and verify all attempts are blocked
    """
    company_a, company_b = create_test_companies

    # Set RLS context to Tenant A
    await set_rls_context(async_db, tenant_id=company_a.tenant_id)

    # Query all companies (no WHERE filter)
    result = await async_db.execute(select(Company))
    companies = result.fetchall()

    # Should only return Company A, not Company B
    company_ids = [c[0].id for c in companies]

    assert company_a.id in company_ids, (
        f"Tenant {company_a.tenant_id} cannot see its own company {company_a.id}! "
        "RLS policy is too restrictive."
    )

    assert company_b.id not in company_ids, (
        f"RLS VIOLATION: Tenant {company_a.tenant_id} can see Company {company_b.id} "
        f"belonging to Tenant {company_b.tenant_id} in SELECT * query!"
        f"\n\nReturned {len(companies)} companies, expected only 1 (Company A)."
        f"\n\nCompany IDs: {company_ids}"
    )


@pytest.mark.asyncio
async def test_rls_context_switching(
    async_db: AsyncSession, create_test_companies, set_rls_context
):
    """Test that RLS context can switch between tenants correctly.

    Simulates switching between tenant contexts in the same session
    (e.g., admin user switching between tenants).

    AC: 1 - Automated tests attempt cross-tenant data access and verify all attempts are blocked
    """
    company_a, company_b = create_test_companies

    # Start with Tenant A context
    await set_rls_context(async_db, tenant_id=company_a.tenant_id)

    result = await async_db.execute(select(Company))
    companies = result.fetchall()
    company_ids = {c[0].id for c in companies}

    assert company_a.id in company_ids, "Tenant A should see Company A"
    assert company_b.id not in company_ids, "Tenant A should NOT see Company B"

    # Switch to Tenant B context
    await set_rls_context(async_db, tenant_id=company_b.tenant_id)

    result = await async_db.execute(select(Company))
    companies = result.fetchall()
    company_ids = {c[0].id for c in companies}

    assert (
        company_b.id in company_ids
    ), "Tenant B should see Company B after context switch"
    assert (
        company_a.id not in company_ids
    ), f"RLS VIOLATION: After switching to Tenant B, can still see Tenant A's Company {company_a.id}!"


@pytest.mark.asyncio
async def test_no_rls_context_blocks_all_access(
    async_db: AsyncSession, create_test_companies
):
    """Test that queries without RLS context set return no results.

    If app.current_tenant is not set, RLS policies should block ALL access
    rather than allowing access to all tenants.

    AC: 1 - Automated tests attempt cross-tenant data access and verify all attempts are blocked
    """
    company_a, company_b = create_test_companies

    # DO NOT set RLS context (simulate missing tenant context)

    # Attempt to query companies
    result = await async_db.execute(select(Company))
    companies = result.fetchall()

    # CRITICAL: Should return 0 results (no context = no access)
    assert len(companies) == 0, (
        f"RLS VIOLATION: Query without tenant context returned {len(companies)} companies!"
        f"\n\nExpected 0 results when app.current_tenant is not set."
        f"\n\nCRITICAL: Missing tenant context should BLOCK access, not ALLOW access."
    )


@pytest.mark.asyncio
async def test_helper_function_attempt_cross_tenant_query(
    async_db: AsyncSession, create_test_companies
):
    """Test the attempt_cross_tenant_query helper function.

    This validates our test utility works correctly.
    """
    company_a, company_b = create_test_companies

    # Use helper to attempt cross-tenant access
    results = await attempt_cross_tenant_query(
        session=async_db,
        table_model=Company,
        tenant_id_field="tenant_id",
        current_tenant_id=company_a.tenant_id,
        target_tenant_id=company_b.tenant_id,
    )

    assert len(results) == 0, (
        f"Helper function failed: Tenant {company_a.tenant_id} accessed "
        f"Tenant {company_b.tenant_id}'s data"
    )
