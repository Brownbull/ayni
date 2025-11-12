"""Add RLS tables and multi-tenant schema

Revision ID: abc123def456
Revises: 1a31ce608336
Create Date: 2025-11-12 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================================
    # Create Tenants table (root of multi-tenancy hierarchy)
    # ============================================================================
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # ============================================================================
    # Create Companies table with tenant isolation
    # ============================================================================
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('country', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('industry', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('timezone', sqlmodel.sql.sqltypes.AutoString(length=50), server_default='America/Santiago', nullable=False),
        sa.Column('opt_in_benchmarking', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('is_demo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_companies_tenant_id', 'companies', ['tenant_id'])

    # ============================================================================
    # Create Locations table with tenant-scoped access via company
    # ============================================================================
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('website', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('is_primary', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_locations_company_id', 'locations', ['company_id'])

    # ============================================================================
    # Modify Users table to add multi-tenant fields
    # ============================================================================
    op.add_column('user', sa.Column('tenant_id', sa.Integer(), nullable=True))  # Nullable first for data migration
    op.add_column('user', sa.Column('role', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True))
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False))

    # Create foreign key constraint
    op.create_foreign_key('user_tenant_id_fkey', 'user', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    op.create_index('idx_users_tenant_id', 'user', ['tenant_id'])

    # After data migration (if any), make tenant_id and role NOT NULL
    # Note: In production, you would first populate these fields before making them non-nullable
    # For now, we'll make them non-nullable immediately since this is a new installation
    op.alter_column('user', 'tenant_id', nullable=False)
    op.alter_column('user', 'role', nullable=False)

    # ============================================================================
    # Apply Row-Level Security (RLS) policies
    # ============================================================================
    # Read and execute the RLS policies SQL file
    conn = op.get_bind()

    # Enable RLS on tables
    conn.execute(text('ALTER TABLE "user" ENABLE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE companies ENABLE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE locations ENABLE ROW LEVEL SECURITY'))

    # Create RLS policies for users table
    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON "user"
        USING (tenant_id = current_setting('app.current_tenant', true)::INTEGER)
    '''))

    # Create RLS policies for companies table
    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON companies
        USING (tenant_id = current_setting('app.current_tenant', true)::INTEGER)
    '''))

    # Create RLS policies for locations table (tenant-scoped via company)
    conn.execute(text('''
        CREATE POLICY tenant_isolation_policy ON locations
        USING (
            company_id IN (
                SELECT id FROM companies
                WHERE tenant_id = current_setting('app.current_tenant', true)::INTEGER
            )
        )
    '''))

    # Create helper function to set tenant context
    conn.execute(text('''
        CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id INTEGER)
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('app.current_tenant', p_tenant_id::TEXT, false);
        END;
        $$ LANGUAGE plpgsql
    '''))


def downgrade():
    # ============================================================================
    # Remove RLS policies and helper function
    # ============================================================================
    conn = op.get_bind()

    # Drop helper function
    conn.execute(text('DROP FUNCTION IF EXISTS set_tenant_context(INTEGER)'))

    # Drop RLS policies
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON locations'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON companies'))
    conn.execute(text('DROP POLICY IF EXISTS tenant_isolation_policy ON "user"'))

    # Disable RLS
    conn.execute(text('ALTER TABLE locations DISABLE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE companies DISABLE ROW LEVEL SECURITY'))
    conn.execute(text('ALTER TABLE "user" DISABLE ROW LEVEL SECURITY'))

    # ============================================================================
    # Remove multi-tenant fields from Users table
    # ============================================================================
    op.drop_index('idx_users_tenant_id', table_name='user')
    op.drop_constraint('user_tenant_id_fkey', 'user', type_='foreignkey')
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'email_verified')
    op.drop_column('user', 'role')
    op.drop_column('user', 'tenant_id')

    # ============================================================================
    # Drop tables in reverse order (respecting foreign key dependencies)
    # ============================================================================
    op.drop_index('idx_locations_company_id', table_name='locations')
    op.drop_table('locations')

    op.drop_index('idx_companies_tenant_id', table_name='companies')
    op.drop_table('companies')

    op.drop_table('tenants')
