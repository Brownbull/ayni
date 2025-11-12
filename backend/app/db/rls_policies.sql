-- Row-Level Security (RLS) Policies for Multi-Tenant Isolation
-- This file contains all RLS policies to enforce tenant isolation at the database level
-- CRITICAL: These policies prevent data leaks between tenants (NFR2.11-2.14)

-- ============================================================================
-- Enable RLS on all tenant-scoped tables
-- ============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

-- Note: tenants table does not need RLS as it's the root of tenant hierarchy


-- ============================================================================
-- RLS Policy for users table
-- ============================================================================

-- Drop policy if exists (for migration idempotency)
DROP POLICY IF EXISTS tenant_isolation_policy ON users;

-- Create policy: Users can only see users in their tenant
CREATE POLICY tenant_isolation_policy ON users
    USING (tenant_id = current_setting('app.current_tenant')::INTEGER);


-- ============================================================================
-- RLS Policy for companies table
-- ============================================================================

-- Drop policy if exists (for migration idempotency)
DROP POLICY IF EXISTS tenant_isolation_policy ON companies;

-- Create policy: Companies filtered by tenant_id
CREATE POLICY tenant_isolation_policy ON companies
    USING (tenant_id = current_setting('app.current_tenant')::INTEGER);


-- ============================================================================
-- RLS Policy for locations table
-- ============================================================================

-- Drop policy if exists (for migration idempotency)
DROP POLICY IF EXISTS tenant_isolation_policy ON locations;

-- Create policy: Locations filtered by tenant via company relationship
-- This ensures locations are only accessible to users in the same tenant
CREATE POLICY tenant_isolation_policy ON locations
    USING (
        company_id IN (
            SELECT id FROM companies
            WHERE tenant_id = current_setting('app.current_tenant')::INTEGER
        )
    );


-- ============================================================================
-- Helper function to set tenant context
-- ============================================================================

-- This function can be called to set the tenant context for the current session
-- Usage: SELECT set_tenant_context(123);
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id INTEGER)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant', p_tenant_id::TEXT, false);
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- Verification Queries (for testing)
-- ============================================================================

-- To verify RLS policies are enabled, run:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- To see all policies:
-- SELECT * FROM pg_policies WHERE schemaname = 'public';
