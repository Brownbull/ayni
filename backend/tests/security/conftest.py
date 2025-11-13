"""Security test fixtures and utilities.

This module provides shared fixtures for security testing:
- create_test_companies: Creates isolated test companies for different tenants
- set_rls_context: Helper to set PostgreSQL RLS context
- create_jwt_token: Helper to create test JWT tokens with tenant_id claims
- get_table_rls_status: Utility to query RLS policy status
"""

from datetime import timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Company, Location, Tenant


@pytest.fixture(scope="function")
async def create_test_tenants(async_db: AsyncSession):
    """Create two test tenants for isolation testing.

    Returns:
        tuple: (tenant_a, tenant_b) with different tenant IDs
    """
    tenant_a = Tenant()
    tenant_b = Tenant()

    async_db.add(tenant_a)
    async_db.add(tenant_b)
    await async_db.commit()
    await async_db.refresh(tenant_a)
    await async_db.refresh(tenant_b)

    return tenant_a, tenant_b


@pytest.fixture(scope="function")
async def create_test_companies(async_db: AsyncSession, create_test_tenants):
    """Create two test companies with different tenant IDs.

    This fixture is critical for testing cross-tenant isolation.
    Company A belongs to Tenant 100, Company B belongs to Tenant 200.

    Returns:
        tuple: (company_a, company_b) from different tenants
    """
    tenant_a, tenant_b = create_test_tenants

    company_a = Company(
        tenant_id=tenant_a.id,
        name="Test Company A",
        country="CL",
        identifier="12.345.678-9",
        is_demo=True,
    )
    company_b = Company(
        tenant_id=tenant_b.id,
        name="Test Company B",
        country="CL",
        identifier="98.765.432-1",
        is_demo=True,
    )

    async_db.add(company_a)
    async_db.add(company_b)
    await async_db.commit()
    await async_db.refresh(company_a)
    await async_db.refresh(company_b)

    return company_a, company_b


@pytest.fixture(scope="function")
async def create_test_locations(async_db: AsyncSession, create_test_companies):
    """Create test locations for each company.

    Creates 2 locations for Company A and 2 for Company B.
    Used to test cross-tenant isolation at the location level.

    Returns:
        dict: {
            'company_a_locations': [location1, location2],
            'company_b_locations': [location3, location4]
        }
    """
    company_a, company_b = create_test_companies

    # Locations for Company A
    loc_a1 = Location(
        company_id=company_a.id,
        name="Company A - Location 1",
        address="123 Test St, Santiago",
        is_primary=True,
    )
    loc_a2 = Location(
        company_id=company_a.id,
        name="Company A - Location 2",
        address="456 Test Ave, Valparaiso",
    )

    # Locations for Company B
    loc_b1 = Location(
        company_id=company_b.id,
        name="Company B - Location 1",
        address="789 Test Blvd, Santiago",
        is_primary=True,
    )
    loc_b2 = Location(
        company_id=company_b.id,
        name="Company B - Location 2",
        address="321 Test Rd, Concepcion",
    )

    async_db.add_all([loc_a1, loc_a2, loc_b1, loc_b2])
    await async_db.commit()

    for loc in [loc_a1, loc_a2, loc_b1, loc_b2]:
        await async_db.refresh(loc)

    return {
        "company_a_locations": [loc_a1, loc_a2],
        "company_b_locations": [loc_b1, loc_b2],
        "company_a": company_a,
        "company_b": company_b,
    }


@pytest.fixture
def set_rls_context():
    """Helper to set PostgreSQL RLS context for testing.

    This fixture returns an async function that sets the tenant context
    using the same mechanism as the production application.

    Usage:
        await set_rls_context(async_db, tenant_id=100)

    Returns:
        Callable: async function(session: AsyncSession, tenant_id: int) -> None
    """

    async def _set_context(session: AsyncSession, tenant_id: int) -> None:
        """Set tenant context for RLS policies.

        Args:
            session: The database session to use
            tenant_id: The tenant ID to set in the session variable
        """
        await session.execute(
            text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
            {"tenant_id": str(tenant_id)},
        )
        # Don't commit - just set the session variable

    return _set_context


@pytest.fixture
def create_jwt_token():
    """Helper to create test JWT tokens with tenant_id claims.

    Creates JWT tokens that can be used to test API endpoint access control.

    Usage:
        token = create_jwt_token(tenant_id=100, user_id="user-123")

    Returns:
        Callable: function(tenant_id: int, user_id: str = "test-user") -> str
    """

    def _create_token(tenant_id: int, user_id: str = "test-user") -> str:
        """Create a JWT token with tenant_id claim.

        Args:
            tenant_id: The tenant ID to embed in the token
            user_id: The user ID for the token subject (default: "test-user")

        Returns:
            str: Encoded JWT token
        """
        # Create token with tenant_id in the payload
        # Note: This extends the standard create_access_token to include tenant_id
        from datetime import datetime, timezone

        import jwt

        from app.core.config import settings

        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode = {
            "exp": expire,
            "sub": str(user_id),
            "tenant_id": tenant_id,  # CRITICAL: tenant_id claim for RLS
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    return _create_token


async def get_table_rls_status(session: AsyncSession, table_name: str) -> dict | None:
    """Utility to check if table has RLS enabled and policies configured.

    Queries PostgreSQL system catalogs to determine RLS status:
    - pg_class: Check if relrowsecurity is true (RLS enabled)
    - pg_policies: Count how many policies exist for the table

    Args:
        session: AsyncSession - Database session
        table_name: str - Name of the table to check

    Returns:
        dict: {
            'table_name': str,
            'rls_enabled': bool,
            'policy_count': int
        } or None if table doesn't exist
    """
    query = text(
        """
        SELECT
            c.relname as table_name,
            c.relrowsecurity as rls_enabled,
            COUNT(p.policyname) as policy_count
        FROM pg_class c
        LEFT JOIN pg_policies p ON p.tablename = c.relname
        WHERE c.relname = :table_name
          AND c.relkind = 'r'  -- Only regular tables
        GROUP BY c.relname, c.relrowsecurity
    """
    )

    result = await session.execute(query, {"table_name": table_name})
    row = result.fetchone()

    if not row:
        return None

    return {"table_name": row[0], "rls_enabled": row[1], "policy_count": row[2]}


async def get_all_tenant_tables(session: AsyncSession) -> list[str]:
    """Get all tables that have tenant_id or company_id columns.

    These are the tables that MUST have RLS policies to prevent
    cross-tenant data leaks.

    Args:
        session: AsyncSession - Database session

    Returns:
        list[str]: Table names that have tenant isolation columns
    """
    query = text(
        """
        SELECT DISTINCT c.table_name
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
          AND (c.column_name = 'tenant_id' OR c.column_name = 'company_id')
        ORDER BY c.table_name
    """
    )

    result = await session.execute(query)
    rows = result.fetchall()

    return [row[0] for row in rows]


async def attempt_cross_tenant_query(
    session: AsyncSession,
    table_model,
    tenant_id_field: str,
    current_tenant_id: int,
    target_tenant_id: int,
) -> list:
    """Test helper to attempt cross-tenant data access.

    Sets RLS context to current_tenant_id, then tries to query
    data belonging to target_tenant_id. Should return 0 results
    if RLS is working correctly.

    Args:
        session: Database session
        table_model: SQLModel class to query
        tenant_id_field: Name of the tenant field ('tenant_id' or 'company_id')
        current_tenant_id: Tenant to set in RLS context
        target_tenant_id: Tenant whose data we're trying to access

    Returns:
        list: Query results (should be empty if RLS works)
    """
    # Set RLS context
    await session.execute(
        text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
        {"tenant_id": str(current_tenant_id)},
    )

    # Attempt to query target tenant's data
    if tenant_id_field == "tenant_id":
        query = select(table_model).where(table_model.tenant_id == target_tenant_id)
    else:  # company_id
        query = select(table_model).where(table_model.company_id == target_tenant_id)

    result = await session.execute(query)
    return result.fetchall()
