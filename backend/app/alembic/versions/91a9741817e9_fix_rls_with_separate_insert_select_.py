"""fix_rls_with_separate_insert_select_policies

Revision ID: 91a9741817e9
Revises: 5daba51e66a0
Create Date: 2025-11-12 17:50:59.437192

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '91a9741817e9'
down_revision = '5daba51e66a0'
branch_labels = None
depends_on = None


def upgrade():
    """Create separate policies for SELECT vs INSERT/UPDATE/DELETE operations"""
    from sqlalchemy import text
    conn = op.get_bind()

    # Drop existing single policy
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON "user"'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON locations'))

    # ========================================================================
    # User table policies
    # ========================================================================
    # SELECT policy: Only show rows matching current tenant context
    conn.execute(text('''
        CREATE POLICY tenant_isolation_select ON "user"
        FOR SELECT
        USING (
            tenant_id IS NOT DISTINCT FROM current_setting('app.current_tenant', true)::INTEGER
        )
    '''))

    # INSERT/UPDATE/DELETE policy: Allow operations when tenant context matches OR is not set
    conn.execute(text('''
        CREATE POLICY tenant_isolation_modify ON "user"
        FOR ALL
        USING (
            current_setting('app.current_tenant', true) IS NULL OR
            tenant_id IS NOT DISTINCT FROM current_setting('app.current_tenant', true)::INTEGER
        )
        WITH CHECK (
            current_setting('app.current_tenant', true) IS NULL OR
            tenant_id IS NOT DISTINCT FROM current_setting('app.current_tenant', true)::INTEGER
        )
    '''))

    # ========================================================================
    # Companies table policies
    # ========================================================================
    conn.execute(text('''
        CREATE POLICY tenant_isolation_select ON companies
        FOR SELECT
        USING (tenant_id = current_setting('app.current_tenant', true)::INTEGER)
    '''))

    conn.execute(text('''
        CREATE POLICY tenant_isolation_modify ON companies
        FOR ALL
        USING (
            current_setting('app.current_tenant', true) IS NULL OR
            tenant_id = current_setting('app.current_tenant', true)::INTEGER
        )
        WITH CHECK (
            current_setting('app.current_tenant', true) IS NULL OR
            tenant_id = current_setting('app.current_tenant', true)::INTEGER
        )
    '''))

    # ========================================================================
    # Locations table policies
    # ========================================================================
    conn.execute(text('''
        CREATE POLICY tenant_isolation_select ON locations
        FOR SELECT
        USING (
            company_id IN (
                SELECT id FROM companies
                WHERE tenant_id = current_setting('app.current_tenant', true)::INTEGER
            )
        )
    '''))

    conn.execute(text('''
        CREATE POLICY tenant_isolation_modify ON locations
        FOR ALL
        USING (
            current_setting('app.current_tenant', true) IS NULL OR
            company_id IN (
                SELECT id FROM companies
                WHERE tenant_id = current_setting('app.current_tenant', true)::INTEGER
            )
        )
        WITH CHECK (
            current_setting('app.current_tenant', true) IS NULL OR
            company_id IN (
                SELECT id FROM companies
                WHERE tenant_id = current_setting('app.current_tenant', true)::INTEGER
            )
        )
    '''))


def downgrade():
    """Revert to single tenant_isolation_policy"""
    from sqlalchemy import text
    conn = op.get_bind()

    # Drop new split policies
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_select ON "user"'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_modify ON "user"'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_select ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_modify ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_select ON locations'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_modify ON locations'))

    # Recreate original single policy
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
