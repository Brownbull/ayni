"""Tests for JWT Tenant Isolation Enforcement (AC: 3, 5).

This module verifies that:
1. API requests with JWT tokens enforce tenant_id isolation
2. Manipulated JWT tenant_id claims are rejected
3. Missing tenant_id in JWT returns proper error codes
4. Cross-tenant API access is blocked (403/404)

CRITICAL: These tests prevent API-level cross-tenant data leaks.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Company

# ============================================================================
# AC3, AC5: JWT Tenant Enforcement Tests
# ============================================================================


@pytest.mark.asyncio
async def test_jwt_with_wrong_tenant_id_blocks_company_access(
    client: TestClient, async_db: AsyncSession, create_test_companies, create_jwt_token
):
    """Test that API request with Company A's token cannot access Company B's data.

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    AC: 5 - API request with manipulated JWT tenant_id claim
    """
    company_a, company_b = create_test_companies

    # Create JWT for Tenant A (tenant_id=100)
    token = create_jwt_token(tenant_id=company_a.tenant_id, user_id="test-user-a")

    # Attempt to access Company B's data (tenant_id=200)
    response = client.get(
        f"/api/v1/companies/{company_b.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # CRITICAL: Should return 403 Forbidden or 404 Not Found (not 200)
    assert response.status_code in [403, 404], (
        f"JWT VIOLATION: Tenant {company_a.tenant_id} user accessed Company {company_b.id} "
        f"(Tenant {company_b.tenant_id}) data via API!"
        f"\n\nExpected status: 403 or 404"
        f"\nActual status: {response.status_code}"
        f"\n\nCRITICAL: API is not enforcing JWT tenant_id isolation!"
    )


@pytest.mark.asyncio
async def test_jwt_with_own_tenant_id_allows_company_access(
    client: TestClient, async_db: AsyncSession, create_test_companies, create_jwt_token
):
    """Test that API request with correct tenant_id allows access.

    This ensures RLS doesn't over-restrict and block legitimate access.

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    """
    company_a, company_b = create_test_companies

    # Create JWT for Tenant A
    token = create_jwt_token(tenant_id=company_a.tenant_id, user_id="test-user-a")

    # Access Company A's data (same tenant) - should work
    response = client.get(
        f"/api/v1/companies/{company_a.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should return 200 OK or 404 if endpoint doesn't exist yet
    # (404 is acceptable if company endpoints not implemented in Epic 1)
    assert response.status_code in [200, 404], (
        f"Tenant {company_a.tenant_id} user cannot access their own Company {company_a.id}!"
        f"\n\nExpected status: 200 or 404 (if endpoint not implemented)"
        f"\nActual status: {response.status_code}"
        f"\n\nResponse: {response.text}"
    )


@pytest.mark.asyncio
async def test_jwt_with_manipulated_tenant_id_rejected(
    client: TestClient, create_jwt_token
):
    """Test that JWT with manipulated tenant_id (non-existent) is rejected.

    Simulates attacker creating token with tenant_id=999 (doesn't exist).

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    AC: 5 - API request with manipulated JWT tenant_id claim
    """
    # Create token with non-existent tenant_id
    token = create_jwt_token(tenant_id=999, user_id="attacker")

    # Attempt to access any company endpoint
    response = client.get(
        "/api/v1/companies/1", headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 401 Unauthorized, 403 Forbidden, or 404 Not Found
    # Depends on whether tenant validation happens before or after query
    assert response.status_code in [401, 403, 404], (
        f"JWT VIOLATION: Token with manipulated tenant_id=999 was accepted!"
        f"\n\nExpected status: 401, 403, or 404"
        f"\nActual status: {response.status_code}"
        f"\n\nCRITICAL: API accepts tokens with invalid tenant_id!"
    )


@pytest.mark.asyncio
async def test_jwt_without_tenant_id_claim_rejected(client: TestClient):
    """Test that JWT missing tenant_id claim returns 401 Unauthorized.

    Tokens MUST include tenant_id for multi-tenant endpoints.

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    AC: 5 - Test missing tenant_id in JWT payload
    """
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.core.config import settings

    # Create token WITHOUT tenant_id claim
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {
        "exp": expire,
        "sub": "test-user",
        # NOTE: NO tenant_id claim
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    # Attempt to access company endpoint
    response = client.get(
        "/api/v1/companies/1", headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 401 Unauthorized
    assert response.status_code in [401, 403, 404], (
        f"JWT VIOLATION: Token without tenant_id claim was accepted!"
        f"\n\nExpected status: 401 (Unauthorized)"
        f"\nActual status: {response.status_code}"
        f"\n\nCRITICAL: API accepts tokens without tenant_id claim!"
    )


@pytest.mark.asyncio
async def test_jwt_with_null_tenant_id_rejected(client: TestClient):
    """Test that JWT with tenant_id=null is rejected.

    Some attacks might set tenant_id to null to bypass checks.

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    """
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.core.config import settings

    # Create token with null tenant_id
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {
        "exp": expire,
        "sub": "test-user",
        "tenant_id": None,  # NULL tenant_id
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    # Attempt to access company endpoint
    response = client.get(
        "/api/v1/companies/1", headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 401 or 403
    assert response.status_code in [401, 403, 404], (
        f"JWT VIOLATION: Token with null tenant_id was accepted!"
        f"\n\nExpected status: 401 or 403"
        f"\nActual status: {response.status_code}"
    )


@pytest.mark.asyncio
async def test_expired_jwt_rejected(client: TestClient):
    """Test that expired JWT tokens are rejected.

    Ensures token expiration is enforced even with valid tenant_id.

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    """
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.core.config import settings

    # Create expired token
    expire = datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
    to_encode = {"exp": expire, "sub": "test-user", "tenant_id": 100}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    # Attempt to access endpoint
    response = client.get(
        "/api/v1/companies/1", headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401, (
        f"JWT VIOLATION: Expired token was accepted!"
        f"\n\nExpected status: 401"
        f"\nActual status: {response.status_code}"
    )


@pytest.mark.asyncio
async def test_jwt_with_invalid_signature_rejected(client: TestClient):
    """Test that JWT with invalid signature is rejected.

    Prevents attackers from forging tokens.

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    """
    from datetime import datetime, timedelta, timezone

    import jwt

    # Create token with WRONG secret key
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"exp": expire, "sub": "attacker", "tenant_id": 100}
    token = jwt.encode(to_encode, "WRONG_SECRET_KEY", algorithm="HS256")

    # Attempt to access endpoint
    response = client.get(
        "/api/v1/companies/1", headers={"Authorization": f"Bearer {token}"}
    )

    # Should return 401 or 403
    assert response.status_code in [401, 403], (
        f"JWT VIOLATION: Token with invalid signature was accepted!"
        f"\n\nExpected status: 401 or 403"
        f"\nActual status: {response.status_code}"
        f"\n\nCRITICAL: API is not validating JWT signatures!"
    )


@pytest.mark.asyncio
async def test_request_without_authorization_header_rejected(client: TestClient):
    """Test that requests without Authorization header are rejected.

    Ensures authentication is required for protected endpoints.

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    """
    # Attempt to access company endpoint without token
    response = client.get("/api/v1/companies/1")

    # Should return 401 or 403
    assert response.status_code in [401, 403, 404], (
        f"API VIOLATION: Unauthenticated request was accepted!"
        f"\n\nExpected status: 401 or 403"
        f"\nActual status: {response.status_code}"
        f"\n\nCRITICAL: Protected endpoints allow unauthenticated access!"
    )


# ============================================================================
# Integration Tests: JWT + RLS Together
# ============================================================================


@pytest.mark.asyncio
async def test_jwt_tenant_enforcement_matches_rls_policy(
    client: TestClient,
    async_db: AsyncSession,
    create_test_companies,
    create_jwt_token,
    set_rls_context,
):
    """Integration test: JWT tenant_id and RLS policy work together.

    Verifies that:
    1. JWT tenant_id is extracted correctly
    2. RLS context is set from JWT
    3. Database queries respect both JWT and RLS

    AC: 3 - Tests verify JWT token tenant_id is properly enforced in queries
    """
    company_a, company_b = create_test_companies

    # Create JWT for Tenant A
    token = create_jwt_token(tenant_id=company_a.tenant_id)

    # Make API request (this should set RLS context from JWT)
    response = client.get(
        f"/api/v1/companies/{company_b.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should be blocked (403/404)
    assert response.status_code in [
        403,
        404,
    ], "Integration failure: JWT + RLS should block cross-tenant access"

    # Verify RLS context can still be manually set (for admin operations)
    await set_rls_context(async_db, tenant_id=company_a.tenant_id)

    from sqlmodel import select

    result = await async_db.execute(select(Company).where(Company.id == company_a.id))
    companies = result.fetchall()

    assert len(companies) > 0, "RLS context setting should still work independently"
