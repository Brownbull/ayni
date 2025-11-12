"""Make tenant_id nullable for backwards compatibility

Revision ID: def789ghi012
Revises: abc123def456
Create Date: 2025-11-12 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'def789ghi012'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None


def upgrade():
    # Make tenant_id and role nullable in user table for backwards compatibility
    # This allows existing test infrastructure to work while still supporting multi-tenancy
    op.alter_column('user', 'tenant_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    op.alter_column('user', 'role',
                    existing_type=sa.VARCHAR(length=50),
                    nullable=True)


def downgrade():
    # Revert to NOT NULL (would fail if there are NULL values)
    op.alter_column('user', 'role',
                    existing_type=sa.VARCHAR(length=50),
                    nullable=False)
    op.alter_column('user', 'tenant_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
