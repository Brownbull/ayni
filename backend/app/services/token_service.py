"""
Token service for refresh token management.

Handles refresh token creation, validation, rotation, and revocation.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.security import create_refresh_token, decode_token, get_password_hash
from app.models import RefreshToken, User


async def create_and_store_refresh_token(
    user_id: uuid.UUID, session: AsyncSession
) -> str:
    """
    Create a refresh token and store its hash in the database.

    Args:
        user_id: User UUID
        session: Database session

    Returns:
        Raw refresh token string (to be sent to client)
    """
    # Generate refresh token with 30-day expiration
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        subject=str(user_id), expires_delta=expires_delta
    )

    # Hash the token for secure storage (same bcrypt cost as passwords: 12)
    token_hash = get_password_hash(refresh_token)

    # Store in database
    db_refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + expires_delta,
    )
    session.add(db_refresh_token)
    await session.commit()

    return refresh_token


async def verify_refresh_token(token: str, session: AsyncSession) -> User | None:
    """
    Verify refresh token and return associated user.

    Checks:
    - Token is valid JWT
    - Token type is "refresh"
    - Token is not expired
    - Token exists in database
    - Token has not been used (rotation)
    - Token has not been revoked
    - User exists and is active

    Args:
        token: Raw refresh token string
        session: Database session

    Returns:
        User if token is valid, None otherwise
    """
    try:
        # Decode token
        payload = decode_token(token)

        # Validate token type
        if payload.get("type") != "refresh":
            return None

        user_id_str = payload.get("sub")
        if not user_id_str:
            return None

        user_id = uuid.UUID(user_id_str)

        # Check if user exists
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        # Hash token to compare with stored hash
        # Note: We can't use verify_password directly because we need to find the token first
        # Instead, we'll fetch all user's refresh tokens and check each one
        # This is acceptable because users typically have few refresh tokens (1-3)

        result = await session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.used_at.is_(None))
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > datetime.now(timezone.utc))
        )
        valid_tokens = result.scalars().all()

        # Find matching token by comparing hash
        # Import verify_password here to avoid circular import
        from app.core.security import verify_password

        for db_token in valid_tokens:
            if verify_password(token, db_token.token_hash):
                return user

        return None

    except Exception:
        return None


async def invalidate_refresh_token(
    token: str, session: AsyncSession, mark_as: str = "used"
) -> bool:
    """
    Invalidate a refresh token by marking it as used or revoked.

    Args:
        token: Raw refresh token string
        session: Database session
        mark_as: Either "used" (for rotation) or "revoked" (for logout)

    Returns:
        True if token was invalidated, False otherwise
    """
    try:
        # Decode token to get user_id
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return False

        user_id = uuid.UUID(user_id_str)

        # Find all valid tokens for this user
        result = await session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.used_at.is_(None))
            .where(RefreshToken.revoked_at.is_(None))
        )
        valid_tokens = result.scalars().all()

        # Find matching token
        from app.core.security import verify_password

        for db_token in valid_tokens:
            if verify_password(token, db_token.token_hash):
                # Mark as used or revoked
                if mark_as == "used":
                    db_token.used_at = datetime.now(timezone.utc)
                elif mark_as == "revoked":
                    db_token.revoked_at = datetime.now(timezone.utc)

                session.add(db_token)
                await session.commit()
                return True

        return False

    except Exception:
        return False


async def revoke_all_user_tokens(user_id: uuid.UUID, session: AsyncSession) -> int:
    """
    Revoke all refresh tokens for a user (logout from all devices).

    Args:
        user_id: User UUID
        session: Database session

    Returns:
        Number of tokens revoked
    """
    result = await session.execute(
        select(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .where(RefreshToken.revoked_at.is_(None))
    )
    tokens = result.scalars().all()

    count = 0
    for token in tokens:
        token.revoked_at = datetime.now(timezone.utc)
        session.add(token)
        count += 1

    await session.commit()
    return count


async def cleanup_expired_tokens(session: AsyncSession) -> int:
    """
    Delete expired refresh tokens from database (housekeeping task).

    Should be run periodically via Celery task.

    Args:
        session: Database session

    Returns:
        Number of tokens deleted
    """
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.expires_at < datetime.now(timezone.utc))
    )
    expired_tokens = result.scalars().all()

    count = 0
    for token in expired_tokens:
        await session.delete(token)
        count += 1

    await session.commit()
    return count
