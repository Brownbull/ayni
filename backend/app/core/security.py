from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt cost factor 12 as per NFR2.6-2.7 security requirements
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta,
    tenant_id: int | None = None,
    role: str | None = None,
    email: str | None = None,
) -> str:
    """
    Create JWT access token with multi-tenant claims.

    Args:
        subject: User ID (UUID as string)
        expires_delta: Token expiration time
        tenant_id: Tenant ID for RLS context (required for multi-tenancy)
        role: User role (Owner, Manager, Analyst, Viewer)
        email: User email address

    Returns:
        Encoded JWT token
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "access",
    }

    # Add multi-tenant claims for RLS
    if tenant_id is not None:
        to_encode["tenant_id"] = tenant_id
    if role:
        to_encode["role"] = role
    if email:
        to_encode["email"] = email

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta,
) -> str:
    """
    Create JWT refresh token.

    Refresh tokens have minimal claims - they're used only to obtain new access tokens.
    They should NOT include sensitive claims like tenant_id or role.

    Args:
        subject: User ID (UUID as string)
        expires_delta: Token expiration time (typically 30 days)

    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload dictionary

    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
