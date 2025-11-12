"""Tests for Row-Level Security (RLS) and multi-tenant isolation.

This test module verifies:
1. Database schema is correct (AC1)
2. RLS policies enforce tenant isolation (AC2)
3. Tenant context switching works correctly (AC2)
4. Connection pooling is configured (AC4)

CRITICAL: These tests validate tenant data isolation which is non-negotiable (NFR2.11-2.14)
"""

from sqlalchemy import inspect, text
from sqlmodel import select

from app.api.deps import set_tenant_context
from app.core.db import async_engine, async_session_maker
from app.models import Company, Location, Tenant, User

# ============================================================================
# AC1: Schema Validation Tests
# ============================================================================


def test_tenants_table_exists():
    """Verify tenants table exists with correct columns"""
    from app.core.db import engine

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "tenants" in tables, "tenants table should exist"

    columns = {col["name"]: col for col in inspector.get_columns("tenants")}
    assert "id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns


def test_users_table_has_tenant_fields():
    """Verify users table has tenant_id, role, and other multi-tenant fields"""
    from app.core.db import engine

    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("user")}

    # Check tenant-related columns exist
    assert "tenant_id" in columns, "user table should have tenant_id column"
    assert "role" in columns, "user table should have role column"
    assert "email_verified" in columns, "user table should have email_verified column"
    assert "created_at" in columns, "user table should have created_at column"
    assert "updated_at" in columns, "user table should have updated_at column"

    # Verify tenant_id is indexed
    indexes = inspector.get_indexes("user")
    tenant_indexed = any("tenant_id" in idx.get("column_names", []) for idx in indexes)
    assert tenant_indexed, "tenant_id should have an index"


def test_companies_table_schema():
    """Verify companies table exists with correct structure"""
    from app.core.db import engine

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "companies" in tables, "companies table should exist"

    columns = {col["name"]: col for col in inspector.get_columns("companies")}

    # Required columns
    assert "id" in columns
    assert "tenant_id" in columns
    assert "name" in columns
    assert "country" in columns
    assert "created_at" in columns

    # Optional columns
    assert "identifier" in columns  # RUT for Chile
    assert "industry" in columns
    assert "timezone" in columns
    assert "opt_in_benchmarking" in columns
    assert "is_demo" in columns

    # Verify tenant_id is indexed
    indexes = inspector.get_indexes("companies")
    tenant_indexed = any("tenant_id" in idx.get("column_names", []) for idx in indexes)
    assert tenant_indexed, "companies.tenant_id should have an index"


def test_locations_table_schema():
    """Verify locations table exists with correct structure"""
    from app.core.db import engine

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "locations" in tables, "locations table should exist"

    columns = {col["name"]: col for col in inspector.get_columns("locations")}

    # Required columns
    assert "id" in columns
    assert "company_id" in columns
    assert "name" in columns
    assert "is_primary" in columns
    assert "created_at" in columns

    # Optional columns
    assert "address" in columns
    assert "website" in columns
    assert "deleted_at" in columns

    # Verify company_id is indexed
    indexes = inspector.get_indexes("locations")
    company_indexed = any(
        "company_id" in idx.get("column_names", []) for idx in indexes
    )
    assert company_indexed, "locations.company_id should have an index"


# ============================================================================
# AC2: RLS Policy Tests
# ============================================================================


def test_rls_enabled_on_tables():
    """Verify RLS is enabled on users, companies, and locations tables"""
    from app.core.db import engine

    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT tablename, rowsecurity
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename IN ('user', 'companies', 'locations')
            """
            )
        )
        rls_status = {row[0]: row[1] for row in result}

        assert rls_status.get("user") is True, "RLS should be enabled on user table"
        assert (
            rls_status.get("companies") is True
        ), "RLS should be enabled on companies table"
        assert (
            rls_status.get("locations") is True
        ), "RLS should be enabled on locations table"


def test_rls_policies_exist():
    """Verify RLS policies exist on all tenant-scoped tables"""
    from app.core.db import engine

    with engine.connect() as conn:
        # Check for SELECT policies
        result = conn.execute(
            text(
                """
                SELECT tablename
                FROM pg_policies
                WHERE schemaname = 'public'
                AND policyname = 'tenant_isolation_select'
            """
            )
        )
        select_policies = [row[0] for row in result]

        assert (
            "user" in select_policies
        ), "tenant_isolation_select should exist on user table"
        assert (
            "companies" in select_policies
        ), "tenant_isolation_select should exist on companies table"
        assert (
            "locations" in select_policies
        ), "tenant_isolation_select should exist on locations table"

        # Check for MODIFY policies
        result = conn.execute(
            text(
                """
                SELECT tablename
                FROM pg_policies
                WHERE schemaname = 'public'
                AND policyname = 'tenant_isolation_modify'
            """
            )
        )
        modify_policies = [row[0] for row in result]

        assert (
            "user" in modify_policies
        ), "tenant_isolation_modify should exist on user table"
        assert (
            "companies" in modify_policies
        ), "tenant_isolation_modify should exist on companies table"
        assert (
            "locations" in modify_policies
        ), "tenant_isolation_modify should exist on locations table"


async def test_tenant_isolation_users_table():
    """Test that users from different tenants cannot see each other's data"""
    async with async_session_maker() as session:
        # Create two tenants
        tenant1 = Tenant()
        tenant2 = Tenant()
        session.add_all([tenant1, tenant2])
        await session.commit()
        await session.refresh(tenant1)
        await session.refresh(tenant2)

        # Create users in different tenants
        from uuid import uuid4

        user1 = User(
            id=uuid4(),
            tenant_id=tenant1.id,
            email="user1@tenant1.com",
            hashed_password="hashed",
            role="Owner",
        )
        user2 = User(
            id=uuid4(),
            tenant_id=tenant2.id,
            email="user2@tenant2.com",
            hashed_password="hashed",
            role="Owner",
        )
        session.add_all([user1, user2])
        await session.commit()

    # Test tenant 1 can only see their users
    async with async_session_maker() as session:
        async with session.begin():
            await set_tenant_context(session, tenant1.id)
            result = await session.execute(select(User))
            users = result.scalars().all()

            assert len(users) == 1, "Should only see 1 user in tenant 1"
            assert users[0].email == "user1@tenant1.com"

    # Test tenant 2 can only see their users
    async with async_session_maker() as session:
        async with session.begin():
            await set_tenant_context(session, tenant2.id)
            result = await session.execute(select(User))
            users = result.scalars().all()

            assert len(users) == 1, "Should only see 1 user in tenant 2"
            assert users[0].email == "user2@tenant2.com"


async def test_tenant_isolation_companies_table():
    """Test that companies are isolated by tenant_id"""
    async with async_session_maker() as session:
        # Create two tenants
        tenant1 = Tenant()
        tenant2 = Tenant()
        session.add_all([tenant1, tenant2])
        await session.commit()
        await session.refresh(tenant1)
        await session.refresh(tenant2)

        # Create companies in different tenants
        company1 = Company(tenant_id=tenant1.id, name="Company 1", country="Chile")
        company2 = Company(tenant_id=tenant2.id, name="Company 2", country="Chile")
        session.add_all([company1, company2])
        await session.commit()

    # Test tenant 1 can only see their companies
    async with async_session_maker() as session:
        async with session.begin():
            await set_tenant_context(session, tenant1.id)
            result = await session.execute(select(Company))
            companies = result.scalars().all()

            assert len(companies) == 1, "Should only see 1 company in tenant 1"
            assert companies[0].name == "Company 1"

    # Test tenant 2 can only see their companies
    async with async_session_maker() as session:
        async with session.begin():
            await set_tenant_context(session, tenant2.id)
            result = await session.execute(select(Company))
            companies = result.scalars().all()

            assert len(companies) == 1, "Should only see 1 company in tenant 2"
            assert companies[0].name == "Company 2"


async def test_tenant_isolation_locations_via_company():
    """Test that locations are isolated by tenant via company relationship"""
    async with async_session_maker() as session:
        # Create two tenants
        tenant1 = Tenant()
        tenant2 = Tenant()
        session.add_all([tenant1, tenant2])
        await session.commit()
        await session.refresh(tenant1)
        await session.refresh(tenant2)

        # Create companies
        company1 = Company(tenant_id=tenant1.id, name="Company 1", country="Chile")
        company2 = Company(tenant_id=tenant2.id, name="Company 2", country="Chile")
        session.add_all([company1, company2])
        await session.commit()
        await session.refresh(company1)
        await session.refresh(company2)

        # Create locations
        location1 = Location(company_id=company1.id, name="Location 1")
        location2 = Location(company_id=company2.id, name="Location 2")
        session.add_all([location1, location2])
        await session.commit()

    # Test tenant 1 can only see their locations (via company)
    async with async_session_maker() as session:
        async with session.begin():
            await set_tenant_context(session, tenant1.id)
            result = await session.execute(select(Location))
            locations = result.scalars().all()

            assert len(locations) == 1, "Should only see 1 location in tenant 1"
            assert locations[0].name == "Location 1"

    # Test tenant 2 can only see their locations
    async with async_session_maker() as session:
        async with session.begin():
            await set_tenant_context(session, tenant2.id)
            result = await session.execute(select(Location))
            locations = result.scalars().all()

            assert len(locations) == 1, "Should only see 1 location in tenant 2"
            assert locations[0].name == "Location 2"


# ============================================================================
# AC2: Tenant Context Switching Tests
# ============================================================================


async def test_set_tenant_context_function():
    """Test that set_tenant_context correctly sets the PostgreSQL session variable"""
    async with async_session_maker() as session:
        async with session.begin():
            # Set tenant context to 123
            await set_tenant_context(session, 123)

            # Verify it was set correctly
            result = await session.execute(
                text("SELECT current_setting('app.current_tenant', true)")
            )
            current_tenant = result.scalar()

            assert current_tenant == "123", "Tenant context should be set to 123"


async def test_tenant_context_switching():
    """Test switching between multiple tenants in different sessions"""
    async with async_session_maker() as session:
        # Create three tenants
        tenant1 = Tenant()
        tenant2 = Tenant()
        tenant3 = Tenant()
        session.add_all([tenant1, tenant2, tenant3])
        await session.commit()
        await session.refresh(tenant1)
        await session.refresh(tenant2)
        await session.refresh(tenant3)

        # Create companies for each tenant
        company1 = Company(tenant_id=tenant1.id, name="T1 Company", country="Chile")
        company2 = Company(tenant_id=tenant2.id, name="T2 Company", country="Chile")
        company3 = Company(tenant_id=tenant3.id, name="T3 Company", country="Chile")
        session.add_all([company1, company2, company3])
        await session.commit()

    # Switch contexts and verify isolation
    for tenant_id, expected_name in [
        (tenant1.id, "T1 Company"),
        (tenant2.id, "T2 Company"),
        (tenant3.id, "T3 Company"),
    ]:
        async with async_session_maker() as session:
            async with session.begin():
                await set_tenant_context(session, tenant_id)
                result = await session.execute(select(Company))
                companies = result.scalars().all()

                assert len(companies) == 1
                assert companies[0].name == expected_name


# ============================================================================
# AC4: Connection Pooling Tests
# ============================================================================


async def test_connection_pool_configuration():
    """Verify async engine has correct connection pool settings"""
    pool = async_engine.pool

    # From story requirements: min 5, max 20, recycle 3600, timeout 30
    assert pool.size() == 5, "Pool size should be 5 (min connections)"
    assert pool._max_overflow == 15, "Max overflow should be 15 (total max 20)"

    # Pool recycle and timeout are configured in create_async_engine
    # These values are set in db.py configuration and stored in pool attributes
    assert async_engine.pool._recycle == 3600, "Pool recycle should be 3600 seconds"
    assert async_engine.pool._timeout == 30.0, "Pool timeout should be 30 seconds"


# ============================================================================
# Helper function tests
# ============================================================================


async def test_set_tenant_context_helper_function_exists():
    """Verify the set_tenant_context SQL helper function exists"""
    async with async_engine.begin() as conn:
        # Check if function exists
        result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_proc
                    WHERE proname = 'set_tenant_context'
                )
            """
            )
        )
        exists = result.scalar()

        assert exists is True, "set_tenant_context SQL function should exist"


# ============================================================================
# Cleanup Fixture
# ============================================================================
# Note: Cleanup is commented out due to event loop issues in pytest-asyncio
# In production, you would use database transactions or separate test databases
# @pytest.fixture(autouse=True, scope="function")
# async def cleanup_test_data():
#     """Clean up test data after each test"""
#     yield
#
#     # Clean up all test data
#     async with async_session_maker() as session:
#         # Delete in reverse order of dependencies
#         await session.execute(text("DELETE FROM locations"))
#         await session.execute(text("DELETE FROM companies"))
#         await session.execute(text("DELETE FROM \"user\" WHERE email LIKE '%@tenant%.com'"))
#         await session.execute(text("DELETE FROM tenants"))
#         await session.commit()
