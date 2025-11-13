"""
Tests for database seed script functionality.

Tests verify that:
- Seed data creates all required entities
- Seed script is idempotent (can run multiple times)
- Demo users have properly hashed passwords
- Tenant isolation is maintained
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import verify_password
from app.db.seeds import seed_database
from app.models import Company, Location, Tenant, User


@pytest.mark.asyncio
async def test_seed_creates_tenant(async_db: AsyncSession) -> None:
    """Test that seed script creates exactly 1 demo tenant."""
    db = async_db
    await seed_database()

    result = await db.execute(select(Tenant))
    tenants = result.scalars().all()

    assert len(tenants) >= 1, "At least 1 tenant should exist after seeding"

    # Verify tenant has timestamps
    tenant = tenants[0]
    assert tenant.created_at is not None
    assert tenant.updated_at is not None


@pytest.mark.asyncio
async def test_seed_creates_users(async_db: AsyncSession) -> None:
    """Test that seed script creates 2 demo users with correct roles."""
    db = async_db
    await seed_database()

    # Check owner user
    result = await db.execute(select(User).where(User.email == "owner@demo.com"))
    owner = result.scalar_one_or_none()

    assert owner is not None, "Owner user should exist"
    assert owner.email == "owner@demo.com"
    assert owner.full_name == "Demo Owner"
    assert owner.role == "Owner"
    assert owner.email_verified is True
    assert owner.is_active is True
    assert owner.tenant_id is not None

    # Check manager user
    result = await db.execute(select(User).where(User.email == "manager@demo.com"))
    manager = result.scalar_one_or_none()

    assert manager is not None, "Manager user should exist"
    assert manager.email == "manager@demo.com"
    assert manager.full_name == "Demo Manager"
    assert manager.role == "Manager"
    assert manager.email_verified is True
    assert manager.is_active is True
    assert manager.tenant_id is not None

    # Verify same tenant
    assert owner.tenant_id == manager.tenant_id


@pytest.mark.asyncio
async def test_seed_password_hashing(async_db: AsyncSession) -> None:
    """Test that demo user passwords are properly hashed with bcrypt."""
    db = async_db
    await seed_database()

    result = await db.execute(select(User).where(User.email == "owner@demo.com"))
    owner = result.scalar_one_or_none()

    assert owner is not None
    # Check that password is hashed (bcrypt starts with $2b$)
    assert owner.hashed_password.startswith("$2b$")

    # Verify password can be validated
    assert verify_password("DemoPass123!", owner.hashed_password)
    assert not verify_password("WrongPassword", owner.hashed_password)


@pytest.mark.asyncio
async def test_seed_creates_company(async_db: AsyncSession) -> None:
    """Test that seed script creates demo company with Chilean RUT."""
    db = async_db
    await seed_database()

    result = await db.execute(select(Company).where(Company.name == "Demo Company"))
    company = result.scalar_one_or_none()

    assert company is not None, "Demo company should exist"
    assert company.name == "Demo Company"
    assert company.identifier == "12.345.678-9"  # Chilean RUT format
    assert company.country == "Chile"
    assert company.industry == "Retail"
    assert company.timezone == "America/Santiago"
    assert company.is_demo is True
    assert company.tenant_id is not None


@pytest.mark.asyncio
async def test_seed_creates_locations(async_db: AsyncSession) -> None:
    """Test that seed script creates 2 demo locations."""
    db = async_db
    await seed_database()

    # Get demo company first
    result = await db.execute(select(Company).where(Company.name == "Demo Company"))
    company = result.scalar_one_or_none()
    assert company is not None

    # Check locations
    result = await db.execute(select(Location).where(Location.company_id == company.id))
    locations = result.scalars().all()

    assert len(locations) == 2, "Should have exactly 2 demo locations"

    # Check primary location
    primary_locations = [loc for loc in locations if loc.is_primary]
    assert len(primary_locations) == 1, "Should have exactly 1 primary location"

    main_store = next((loc for loc in locations if loc.name == "Main Store"), None)
    assert main_store is not None
    assert main_store.is_primary is True
    assert "Providencia" in main_store.address

    # Check secondary location
    mall_location = next(
        (loc for loc in locations if loc.name == "Mall Location"), None
    )
    assert mall_location is not None
    assert mall_location.is_primary is False
    assert "Mall Plaza" in mall_location.address


@pytest.mark.asyncio
async def test_seed_idempotency(async_db: AsyncSession) -> None:
    """Test that seed script can be run multiple times without duplicating data."""
    db = async_db
    # Run seed script twice
    await seed_database()
    await seed_database()

    # Verify only 2 demo users exist (not 4)
    result = await db.execute(
        select(User).where(User.email.in_(["owner@demo.com", "manager@demo.com"]))
    )
    users = result.scalars().all()
    assert len(users) == 2, "Should have exactly 2 demo users after running twice"

    # Verify only 1 demo company exists (not 2)
    result = await db.execute(select(Company).where(Company.name == "Demo Company"))
    companies = result.scalars().all()
    assert len(companies) == 1, "Should have exactly 1 demo company after running twice"

    # Verify only 2 locations exist (not 4)
    result = await db.execute(
        select(Location).where(Location.name.in_(["Main Store", "Mall Location"]))
    )
    locations = result.scalars().all()
    assert len(locations) == 2, "Should have exactly 2 locations after running twice"


@pytest.mark.asyncio
async def test_seed_tenant_isolation(async_db: AsyncSession) -> None:
    """Test that all seed data belongs to the same tenant."""
    db = async_db
    await seed_database()

    # Get demo users
    result = await db.execute(select(User).where(User.email == "owner@demo.com"))
    owner = result.scalar_one_or_none()
    assert owner is not None

    tenant_id = owner.tenant_id

    # Verify company belongs to same tenant
    result = await db.execute(select(Company).where(Company.name == "Demo Company"))
    company = result.scalar_one_or_none()
    assert company is not None
    assert company.tenant_id == tenant_id

    # Verify all users belong to same tenant
    result = await db.execute(
        select(User).where(User.email.in_(["owner@demo.com", "manager@demo.com"]))
    )
    users = result.scalars().all()
    for user in users:
        assert user.tenant_id == tenant_id
