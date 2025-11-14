"""add is_verified field to users

Revision ID: 20251114_add_verified
Revises: 91a9741817e9
Create Date: 2025-11-14 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251114_add_verified'
down_revision: Union[str, None] = '91a9741817e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add is_verified field to users table for email verification.

    This field is used by fastapi-users authentication pattern.
    - is_verified: Boolean field, defaults to False
    - Replaces email_verified for consistency with fastapi-users
    """
    # Add is_verified column (defaults to False)
    op.add_column('user', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))

    # If email_verified column exists, copy its data to is_verified
    # This handles migration from old schema
    op.execute("""
        UPDATE "user"
        SET is_verified = COALESCE(email_verified, false)
        WHERE email_verified IS NOT NULL
    """)

    # Drop email_verified column if it exists (we use is_verified now)
    # Note: This is a destructive operation, only run if email_verified exists
    try:
        op.drop_column('user', 'email_verified')
    except Exception:
        # Column doesn't exist, that's fine
        pass


def downgrade() -> None:
    """
    Revert is_verified field addition.

    Restores email_verified column for backward compatibility.
    """
    # Add back email_verified column
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))

    # Copy data from is_verified to email_verified
    op.execute("""
        UPDATE "user"
        SET email_verified = is_verified
    """)

    # Drop is_verified column
    op.drop_column('user', 'is_verified')
