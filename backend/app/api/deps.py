"""
API Dependencies for Database Sessions and User Authentication

ARCHITECTURAL DECISION: Tenant Context via Dependency Injection (not Middleware)
================================================================================

This module uses FastAPI dependency injection to set tenant context for RLS policies,
rather than middleware. This design choice was made for the following reasons:

1. **Per-Request Database Session Scoping**: Dependency injection guarantees tenant
   context is set on the SAME session that handles subsequent queries. Middleware
   would need to pass session context across request lifecycle, adding complexity.

2. **Granular Control**: Only authenticated endpoints need tenant context. Dependency
   injection allows selective application via `CurrentUser = Depends(get_current_user)`.
   Middleware would run on ALL requests, including public endpoints.

3. **Type Safety**: FastAPI dependencies provide type hints and editor support.
   get_current_user() returns typed User object with tenant_id accessible to routes.

4. **Testability**: Dependencies are easily mocked in tests. Middleware requires
   more complex test setup with full request/response cycle simulation.

5. **Explicit Flow**: Tenant context setting is visible in the dependency chain:
   token → get_current_user() → set_tenant_context() → RLS policies active.
   With middleware, this flow is implicit and harder to trace.

6. **Error Handling**: Authentication failures (invalid token, inactive user) are
   handled in the same function that sets context, reducing error handling complexity.

IMPORTANT: While architecture.md shows middleware example for illustration,
dependency injection is the PREFERRED pattern for FastAPI + SQLAlchemy applications.
Both approaches correctly enforce tenant isolation; dependency injection does so
with better ergonomics and type safety.

References:
- Story 1.2 Implementation: backend/app/api/deps.py:75-113
- RLS Policies: backend/app/db/rls_policies.sql
- Test Coverage: backend/tests/test_rls_tenant_isolation.py:204-394
"""

from collections.abc import AsyncGenerator, Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import async_session_maker, engine
from app.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


# ============================================================================
# Tenant Context Management
# ============================================================================


async def set_tenant_context(session: AsyncSession, tenant_id: int) -> None:
    """Set tenant context for RLS policies.

    This function MUST be called before any database queries in a multi-tenant context.
    It sets the PostgreSQL session variable that RLS policies use for tenant isolation.

    Args:
        session: AsyncSession - The database session
        tenant_id: int - The tenant ID from the authenticated user's JWT token
    """
    await session.execute(
        text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
        {"tenant_id": str(tenant_id)},
    )


# ============================================================================
# Database Session Dependencies
# ============================================================================


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session dependency.

    Yields an async database session. Tenant context must be set separately
    after authentication via set_tenant_context().
    """
    async with async_session_maker() as session:
        yield session


# Sync session for backwards compatibility (migrations, scripts)
def get_db_sync() -> Generator[Session, None, None]:
    """Synchronous database session for scripts and migrations"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


# ============================================================================
# User Authentication Dependencies
# ============================================================================


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Get current authenticated user from JWT token and set tenant context.

    This dependency:
    1. Validates the JWT token
    2. Fetches the user from the database
    3. Sets the tenant context for RLS policies

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If token is invalid, user not found, or user is inactive
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # Query user (before setting tenant context - this is the initial auth query)
    result = await session.execute(select(User).where(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # CRITICAL SECURITY VALIDATION: Ensure tenant_id is never NULL
    # NULL tenant_id would bypass RLS policies and potentially expose all tenant data
    # This check prevents catastrophic data leaks (NFR2.11-2.14)
    if user.tenant_id is None:
        raise HTTPException(
            status_code=500,
            detail="User has no tenant association - data isolation cannot be guaranteed",
        )

    # CRITICAL: Set tenant context for RLS policies
    # All subsequent queries in this session will be filtered by this tenant_id
    await set_tenant_context(session, user.tenant_id)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Verify current user has superuser privileges"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
