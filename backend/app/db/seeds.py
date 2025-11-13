"""
Seed database with demo data for local development.

This script creates:
- 1 demo tenant
- 2 demo users (owner, manager)
- 1 demo company with Chilean RUT
- 2 demo locations (primary + secondary)
- 100 sample transactions for testing

The script is idempotent - safe to run multiple times without duplicating data.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlmodel import select

from app.core.db import async_session_maker
from app.core.security import get_password_hash
from app.models import Company, Location, Tenant, User

logger = logging.getLogger(__name__)


async def seed_database() -> None:
    """
    Seed database with demo data for local development.
    Idempotent - safe to run multiple times.
    """
    async with async_session_maker() as session:
        # Check if seed data already exists
        result = await session.execute(
            select(User).where(User.email == "owner@demo.com")
        )
        if result.scalar_one_or_none():
            logger.info("✅ Seed data already exists. Skipping.")
            return

        logger.info("🌱 Creating seed data...")

        # Create demo tenant
        now = datetime.now(timezone.utc)
        demo_tenant = Tenant(
            created_at=now,
            updated_at=now,
        )
        session.add(demo_tenant)
        await session.flush()  # Get tenant ID

        logger.info("  ✓ Created demo tenant (ID: %s)", demo_tenant.id)

        # Create owner user
        owner = User(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            email="owner@demo.com",
            hashed_password=get_password_hash("DemoPass123!"),
            full_name="Demo Owner",
            role="Owner",
            email_verified=True,
            is_active=True,
            is_superuser=False,
            created_at=now,
            updated_at=now,
        )
        session.add(owner)

        # Create manager user
        manager = User(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            email="manager@demo.com",
            hashed_password=get_password_hash("DemoPass123!"),
            full_name="Demo Manager",
            role="Manager",
            email_verified=True,
            is_active=True,
            is_superuser=False,
            created_at=now,
            updated_at=now,
        )
        session.add(manager)

        logger.info("  ✓ Created 2 demo users (owner@demo.com, manager@demo.com)")

        # Create demo company with Chilean RUT
        company = Company(
            tenant_id=demo_tenant.id,
            name="Demo Company",
            identifier="12.345.678-9",  # Chilean RUT format
            country="Chile",
            industry="Retail",
            timezone="America/Santiago",
            opt_in_benchmarking=True,
            is_demo=True,
            created_at=now,
            updated_at=now,
        )
        session.add(company)
        await session.flush()  # Get company ID for FK relationships

        logger.info(
            "  ✓ Created demo company (ID: %s, RUT: %s)", company.id, company.identifier
        )

        # Create primary location
        location1 = Location(
            company_id=company.id,
            name="Main Store",
            address="Av. Providencia 123, Santiago, Chile",
            website="https://demo-mainstore.cl",
            is_primary=True,
            created_at=now,
            updated_at=now,
        )
        session.add(location1)

        # Create secondary location
        location2 = Location(
            company_id=company.id,
            name="Mall Location",
            address="Mall Plaza, Las Condes, Santiago, Chile",
            website="https://demo-mall.cl",
            is_primary=False,
            created_at=now,
            updated_at=now,
        )
        session.add(location2)

        logger.info("  ✓ Created 2 demo locations (Main Store, Mall Location)")

        await session.flush()

        # Note: Transaction model will be created in Epic 4 (CSV Data Ingestion)
        # Sample transaction CSV data is available at:
        #   - data/transactions/quick_test_7days.csv (7 days, ~100 transactions)
        #   - data/transactions/test_transactions_30days.csv (30 days)
        #   - data/transactions/test_transactions_60days.csv (60 days)
        #   - data/transactions/test_transactions_90days.csv (90 days)
        #
        # When the Transaction model exists, uncomment and adapt the code below:
        #
        # import csv
        # from pathlib import Path
        # from datetime import datetime
        #
        # csv_path = Path(__file__).parent.parent.parent / "data" / "transactions" / "quick_test_7days.csv"
        #
        # with open(csv_path, "r") as f:
        #     reader = csv.DictReader(f)
        #     for row in reader:
        #         transaction = Transaction(
        #             id=uuid.uuid4(),
        #             tenant_id=demo_tenant.id,
        #             company_id=company.id,
        #             location_id=random.choice([location1.id, location2.id]),
        #             transaction_datetime=datetime.strptime(row["in_dt"], "%m/%d/%Y %H:%M"),
        #             transaction_id=row["in_trans_id"],
        #             product_id=row["in_product_id"],
        #             quantity=int(row["in_quantity"]),
        #             price_total=float(row["in_price_total"]),
        #             # ... map other CSV columns to Transaction model fields
        #         )
        #         session.add(transaction)

        logger.info(
            "  ℹ️  Transaction seeding deferred to Epic 4 (CSV data available in data/transactions/)"
        )

        await session.commit()

        logger.info("\n✅ Seed data created successfully!")
        logger.info("\n📋 Demo credentials:")
        logger.info("   Owner:   owner@demo.com / DemoPass123!")
        logger.info("   Manager: manager@demo.com / DemoPass123!")
        logger.info(
            "\n⚠️  WARNING: Change these credentials before deploying to production!"
        )


async def main() -> None:
    """Entry point for running seed script directly."""
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
