"""Security test suite for multi-tenant isolation.

This package contains comprehensive security tests that verify:
- RLS policies exist on all tenant-scoped tables
- Cross-tenant data access is blocked at database level
- JWT tenant_id enforcement prevents unauthorized access
- Security audit reporting
"""
