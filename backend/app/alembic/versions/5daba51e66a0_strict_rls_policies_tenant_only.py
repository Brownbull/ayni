"""strict_rls_policies_tenant_only

Revision ID: 5daba51e66a0
Revises: bf07dc2a7ad6
Create Date: 2025-11-12 17:47:56.102625

NOTE: This migration is SUPERSEDED by 91a9741817e9.
It attempted to use strict RLS policies but did not handle INSERT operations correctly.
The final solution splits policies into SELECT (strict) and MODIFY (lenient for setup).

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '5daba51e66a0'
down_revision = 'bf07dc2a7ad6'
branch_labels = None
depends_on = None


def upgrade():
    """Use strict RLS policies that only show rows matching current tenant"""
    from sqlalchemy import text
    conn = op.get_bind()

    # Drop existing policies
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON "user"'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON locations'))

    # Create strict policies - only show rows where tenant_id matches exactly
    # Rows with NULL tenant_id will NOT be visible when tenant context is set
    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON "user"
        USING (
            tenant_id IS NOT DISTINCT FROM current_setting('app.current_tenant', true)::INTEGER
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


def downgrade():
    """Revert to previous policies with NULL handling"""
    from sqlalchemy import text
    conn = op.get_bind()

    # Drop strict policies
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON "user"'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON locations'))

    # Recreate policies with NULL handling
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
