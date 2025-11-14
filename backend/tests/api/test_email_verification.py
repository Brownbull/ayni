"""
Tests for email verification endpoints (Story 2.2).

Tests cover:
- Email verification with valid/expired/invalid tokens
- Resend verification with rate limiting
- Login blocked for unverified users
- Token generation and validation
"""

import uuid
from datetime import timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_verification_token, verify_email_token
from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    """Generate unique email address for testing to avoid collisions."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def test_create_verification_token() -> None:
    """Test verification token generation with correct claims."""
    user_id = "test-user-123"

    token = create_verification_token(user_id)

    # Decode without verification for inspection
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

    assert payload["sub"] == user_id
    assert payload["type"] == "email_verification"
    assert "exp" in payload
    assert "iat" in payload


def test_verify_email_token_valid() -> None:
    """Test verification token validation with valid token."""
    user_id = "test-user-456"
    token = create_verification_token(user_id)

    decoded_user_id = verify_email_token(token)

    assert decoded_user_id == user_id


def test_verify_email_token_expired() -> None:
    """Test verification token validation fails for expired token."""
    user_id = "test-user-789"

    # Create token with -1 hour expiration (already expired)
    token = create_verification_token(user_id, timedelta(hours=-1))

    with pytest.raises(ValueError, match="Verification token expired"):
        verify_email_token(token)


def test_verify_email_token_invalid() -> None:
    """Test verification token validation fails for invalid token."""
    with pytest.raises(ValueError, match="Invalid verification token"):
        verify_email_token("invalid.token.here")


def test_verify_email_token_wrong_type() -> None:
    """Test verification token validation fails for wrong token type (access token)."""
    from app.core.security import create_access_token

    # Create an access token instead of verification token
    access_token = create_access_token(
        subject="user-123",
        expires_delta=timedelta(hours=24),
        tenant_id=1,
        role="Owner",
        email="test@example.com",
    )

    with pytest.raises(ValueError, match="Invalid token type"):
        verify_email_token(access_token)


def test_verify_email_success() -> None:
    """
    Test POST /auth/verify-email with valid token marks email as verified.

    Acceptance Criteria: AC1
    """
    # Create unverified user
    email = unique_email("verify")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert register_response.status_code == 201
    user_data = register_response.json()
    user_id = user_data["id"]

    # Response confirms user is not verified initially
    assert user_data["is_verified"] is False

    # Generate verification token
    token = create_verification_token(user_id)

    # Verify email
    verify_response = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": token},
    )

    assert verify_response.status_code == 200
    assert "verified" in verify_response.json()["message"].lower()

    # Verify the user can now login (confirms verification worked)
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_verify_email_expired_token() -> None:
    """
    Test POST /auth/verify-email returns 400 for expired token.

    Acceptance Criteria: AC4
    """
    # Create unverified user
    email = unique_email("expired")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Generate expired token
    expired_token = create_verification_token(user_id, timedelta(hours=-1))

    # Try to verify with expired token
    verify_response = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": expired_token},
    )

    assert verify_response.status_code == 400
    assert "expired" in verify_response.json()["detail"].lower()


def test_verify_email_invalid_token() -> None:
    """Test POST /auth/verify-email returns 400 for invalid token."""
    verify_response = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": "invalid.token.here"},
    )

    assert verify_response.status_code == 400
    assert "invalid" in verify_response.json()["detail"].lower()


def test_verify_email_nonexistent_user() -> None:
    """Test POST /auth/verify-email returns 404 if user doesn't exist."""
    # Generate token for non-existent user
    fake_user_id = "00000000-0000-0000-0000-000000000000"
    token = create_verification_token(fake_user_id)

    verify_response = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": token},
    )

    assert verify_response.status_code == 404
    assert "not found" in verify_response.json()["detail"].lower()


def test_verify_email_idempotent() -> None:
    """
    Test POST /auth/verify-email is idempotent (calling twice doesn't error).

    Acceptance Criteria: AC1
    """
    # Create unverified user
    email = unique_email("idempotent")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Generate verification token
    token = create_verification_token(user_id)

    # Verify email first time
    verify_response1 = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": token},
    )
    assert verify_response1.status_code == 200

    # Verify email second time (should still succeed)
    verify_response2 = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": token},
    )
    assert verify_response2.status_code == 200
    assert "already verified" in verify_response2.json()["message"].lower()


def test_login_unverified_user() -> None:
    """
    Test login endpoint rejects unverified users with 401.

    Acceptance Criteria: AC3
    """
    # Create unverified user
    email = unique_email("unverified")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    # Verify user is not verified in response
    assert register_response.json()["is_verified"] is False

    # Try to login
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 401
    assert "not verified" in login_response.json()["detail"].lower()


def test_login_verified_user() -> None:
    """
    Test login endpoint allows verified users to login.

    Acceptance Criteria: AC3
    """
    # Create and verify user
    email = unique_email("verified")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Verify email
    token = create_verification_token(user_id)
    verify_response = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": token},
    )
    assert verify_response.status_code == 200

    # Try to login (should succeed)
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_resend_verification_success() -> None:
    """
    Test POST /auth/resend-verification sends new email for unverified user.

    Acceptance Criteria: AC5
    """
    # Create unverified user
    email = unique_email("resend")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    # Resend verification email
    resend_response = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": email},
    )

    assert resend_response.status_code == 200
    assert "verification link" in resend_response.json()["message"].lower()


def test_resend_verification_rate_limit() -> None:
    """
    Test resend-verification enforces rate limiting (1 per 60 seconds).

    Acceptance Criteria: AC5
    """
    # Create unverified user
    email = unique_email("ratelimit")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    # First resend (should succeed)
    resend_response1 = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": email},
    )
    assert resend_response1.status_code == 200

    # Second resend immediately (should be rate limited)
    resend_response2 = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": email},
    )
    assert resend_response2.status_code == 429
    assert "wait" in resend_response2.json()["detail"].lower()


def test_resend_verification_no_email_enumeration() -> None:
    """
    Test resend-verification doesn't reveal if email exists (always returns success).

    Acceptance Criteria: AC5 (Security requirement)
    """
    # Try to resend for non-existent email
    non_existent_email = unique_email("nonexistent")
    resend_response = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": non_existent_email},
    )

    # Should return 200 (not 404) to prevent email enumeration
    assert resend_response.status_code == 200
    assert "verification link" in resend_response.json()["message"].lower()


def test_resend_verification_already_verified() -> None:
    """
    Test resend-verification doesn't send email if user already verified.

    Acceptance Criteria: AC5
    """
    # Create and verify user
    email = unique_email("alreadyverified")
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Verify email
    token = create_verification_token(user_id)
    verify_response = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": token},
    )
    assert verify_response.status_code == 200

    # Try to resend verification (should return success but not send email)
    resend_response = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": email},
    )

    # Should still return 200 for security (no enumeration)
    assert resend_response.status_code == 200


def test_integration_full_flow() -> None:
    """
    Integration test: register → verify → login success.

    Acceptance Criteria: All
    """
    email = unique_email("integration")
    password = "testpassword123"

    # Step 1: Register user
    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password, "full_name": "Integration Test"},
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Step 2: Verify user can't login yet
    login_response1 = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response1.status_code == 401  # Unverified

    # Step 3: Verify email
    token = create_verification_token(user_id)
    verify_response = client.post(
        f"{settings.API_V1_STR}/auth/verify-email",
        params={"token": token},
    )
    assert verify_response.status_code == 200

    # Step 4: Now login should succeed
    login_response2 = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response2.status_code == 200
    assert "access_token" in login_response2.json()
    assert "refresh_token" in login_response2.json()
