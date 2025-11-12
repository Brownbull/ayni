"""fix_rls_policies_for_null_tenant_id

Revision ID: bf07dc2a7ad6
Revises: def789ghi012
Create Date: 2025-11-12 17:47:08.677083

NOTE: This migration is SUPERSEDED by 91a9741817e9.
It was an intermediate step in fixing RLS enforcement. The final solution was to:
1. Remove SUPERUSER privileges from the ayni_user role
2. Create separate SELECT and MODIFY policies (in migration 91a9741817e9)

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'bf07dc2a7ad6'
down_revision = 'def789ghi012'
branch_labels = None
depends_on = None


def upgrade():
    """Fix RLS policies to handle NULL tenant_id and use FORCE RLS"""
    from sqlalchemy import text
    conn = op.get_bind()

    # Drop existing policies
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON "user"'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON locations'))

    # Recreate policies with NULL handling
    # Users with NULL tenant_id (like superuser) won't be filtered by RLS
    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON "user"
        USING (
            tenant_id IS NULL OR
            tenant_id = current_setting('app.current_tenant', true)::INTEGER
        )
    '''))

    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON companies
        USING (tenant_id = current_setting('app.current_tenant', true)::INTEGER)
    '''))

    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON locations
        USING (
            company_id IN (
                SELECT id FROM companies
                WHERE tenant_id = current_setting('app.current_tenant', true)::INTEGER
            )
        )
    '''))

    # Use FORCE ROW LEVEL SECURITY to enforce even for table owners
    conn.execute(text('ALTER TABLE "user" FORCE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE companies FORCE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE locations FORCE ROW LEVEL SECURITY'))


def downgrade():
    """Revert to original RLS policies"""
    from sqlalchemy import text
    conn = op.get_bind()

    # Remove FORCE RLS
    conn.execute(text('ALTER TABLE "user" NO FORCE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE companies NO FORCE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE locations NO FORCE ROW LEVEL SECURITY'))

    # Drop new policies
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON "user"'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON locations'))

    # Recreate original policies without NULL handling
    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON "user"
        USING (tenant_id = current_setting('app.current_tenant', true)::INTEGER)
    '''))

    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON companies
        USING (tenant_id = current_setting('app.current_tenant', true)::INTEGER)
    '''))

    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON locations
        USING (
            company_id IN (
                SELECT id FROM companies
                WHERE tenant_id = current_setting('app.current_tenant', true)::INTEGER
            )
        )
    '''))
