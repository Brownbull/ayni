import base64
from datetime import datetime, timedelta
from typing import Any

import jwt
from cryptography.fernet import Fernet
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
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
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
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
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


def create_verification_token(
    user_id: str | Any, expires_delta: timedelta | None = None
) -> str:
    """
    Create JWT email verification token.

    Args:
        user_id: User ID (UUID as string)
        expires_delta: Token expiration time (default: 24 hours)

    Returns:
        Encoded JWT verification token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(user_id),
        "type": "email_verification",
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def verify_email_token(token: str) -> str:
    """
    Decode and validate email verification token.

    Args:
        token: JWT verification token string

    Returns:
        User ID extracted from token

    Raises:
        ValueError: If token is expired, invalid, or wrong type
    """
    try:
        payload = decode_token(token)

        # Validate token type
        if payload.get("type") != "email_verification":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing user_id in token")

        return user_id

    except jwt.ExpiredSignatureError:
        raise ValueError("Verification token expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid verification token: {str(e)}")


def create_password_reset_token(
    user_id: str | Any,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create JWT password reset token with 1-hour expiration.

    Args:
        user_id: User ID (UUID as string)
        email: User email address
        expires_delta: Token expiration time (default: 1 hour)

    Returns:
        Encoded JWT password reset token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=1)

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(user_id),
        "email": email,
        "type": "password_reset",
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> dict[str, Any]:
    """
    Decode and validate password reset token.

    Args:
        token: JWT password reset token string

    Returns:
        Token payload dictionary with user_id and email

    Raises:
        ValueError: If token is expired, invalid, or wrong type
    """
    try:
        payload = decode_token(token)

        # Validate token type
        if payload.get("type") != "password_reset":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise ValueError("Missing user_id or email in token")

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError("Password reset token expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid password reset token: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _get_encryption_key() -> bytes:
    """
    Derive Fernet encryption key from JWT secret.

    Uses base64-encoded SHA256 hash of JWT_SECRET to create a valid Fernet key.
    This ensures the encryption key is deterministic and based on the app secret.

    Returns:
        32-byte Fernet-compatible encryption key
    """
    import hashlib

    # Create SHA256 hash of JWT_SECRET
    key_hash = hashlib.sha256(settings.JWT_SECRET.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_hash)


def encrypt_token(token: str) -> str:
    """
    Encrypt OAuth token for database storage.

    Args:
        token: Plain text OAuth token

    Returns:
        Encrypted token (base64-encoded)
    """
    fernet = Fernet(_get_encryption_key())
    encrypted = fernet.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt OAuth token from database.

    Args:
        encrypted_token: Encrypted token (base64-encoded)

    Returns:
        Plain text OAuth token

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    fernet = Fernet(_get_encryption_key())
    decrypted = fernet.decrypt(encrypted_token.encode())
    return decrypted.decode()
