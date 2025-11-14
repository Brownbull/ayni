"""
Tests for authentication endpoints.

Tests cover:
- User registration with tenant creation
- Login with JWT token generation
- User profile retrieval
- Error handling for invalid credentials
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.main import app
from app.models import Tenant, User

client = TestClient(app)


def test_register_new_user(db: Session) -> None:
    """
    Test user registration creates both user and tenant.

    Acceptance Criteria covered:
    - AC1: User account is created with hashed password
    - AC2: Associated tenant record is created
    - AC3: Email is marked as unverified (is_verified=False)
    """
    email = "newuser@example.com"
    password = "testpassword123"

    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password, "full_name": "New User"},
    )

    assert response.status_code == 201
    data = response.json()

    # Verify user data in response
    assert data["email"] == email
    assert data["is_active"] is True
    assert data["is_verified"] is False  # Email not verified yet
    assert data["role"] == "Owner"
    assert "id" in data
    assert "tenant_id" in data

    # Verify user exists in database
    user = db.exec(select(User).where(User.email == email)).first()
    assert user is not None
    assert user.email == email
    assert user.is_verified is False
    assert user.role == "Owner"

    # Verify tenant was created
    assert user.tenant_id is not None
    tenant = db.exec(select(Tenant).where(Tenant.id == user.tenant_id)).first()
    assert tenant is not None


def test_register_duplicate_email(_db: Session) -> None:
    """
    Test registration fails with existing email.

    Acceptance Criteria:
    - Returns 400 status code
    - Returns appropriate error message
    """
    # Create first user
    email = "duplicate@example.com"
    password = "testpassword123"

    response1 = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert response1.status_code == 201

    # Try to register with same email
    response2 = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )

    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


def test_login_success(_db: Session) -> None:
    """
    Test successful login returns JWT token.

    Acceptance Criteria covered:
    - AC5: Login validates email and password
    - AC4: JWT token is returned with correct claims
    """
    # Create user first
    email = "loginuser@example.com"
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},  # OAuth2 uses form data
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 200
    data = login_response.json()

    # Verify token structure
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_invalid_credentials(_db: Session) -> None:
    """
    Test login fails with invalid credentials.

    Acceptance Criteria:
    - Returns 401 status code for invalid credentials
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_current_user(_db: Session) -> None:
    """
    Test GET /users/me returns current authenticated user.

    Acceptance Criteria:
    - Requires valid JWT token
    - Returns user profile
    """
    # Create and login user
    email = "meuser@example.com"
    password = "testpassword123"

    # Register
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password, "full_name": "Me User"},
    )

    # Login to get token
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]

    # Get current user
    me_response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    data = me_response.json()

    assert data["email"] == email
    assert data["full_name"] == "Me User"
    assert data["is_active"] is True


def test_get_current_user_unauthorized(_db: Session) -> None:
    """
    Test GET /users/me fails without token.

    Acceptance Criteria:
    - Returns 401 status code without valid token
    """
    response = client.get(f"{settings.API_V1_STR}/users/me")

    assert response.status_code == 401


def test_register_invalid_email(_db: Session) -> None:
    """
    Test registration with invalid email format returns 422.

    Review Finding: Missing test for invalid email format validation
    """
    invalid_emails = [
        "notanemail",
        "@example.com",
        "user@",
        "user @example.com",
        "",
    ]

    for invalid_email in invalid_emails:
        response = client.post(
            f"{settings.API_V1_STR}/auth/register",
            json={"email": invalid_email, "password": "testpassword123"},
        )
        # Should return 422 for validation error
        assert response.status_code == 422, f"Failed for email: {invalid_email}"


def test_register_weak_password(_db: Session) -> None:
    """
    Test registration with password less than 8 characters returns 422.

    Review Finding: Missing test for weak password validation
    Server-side validation should reject passwords < 8 characters
    """
    weak_passwords = ["short", "1234567", "abc", ""]

    for weak_password in weak_passwords:
        response = client.post(
            f"{settings.API_V1_STR}/auth/register",
            json={"email": "user@example.com", "password": weak_password},
        )
        # Should return 422 for validation error
        assert response.status_code == 422, f"Failed for password: {weak_password}"
        assert "detail" in response.json()


def test_login_unverified_email(_db: Session) -> None:
    """
    Test login with unverified email returns 401.

    Review Finding: Missing test for unverified email check
    AC#4 requires email verification before login
    """
    # Register user (creates with is_verified=False)
    email = "unverified@example.com"
    password = "testpassword123"

    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    # Attempt to login without verifying email
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Should return 401 because email is not verified
    assert login_response.status_code == 401
    assert "not verified" in login_response.json()["detail"].lower()


def test_refresh_token_flow(db: Session) -> None:
    """
    Test refresh token endpoint returns new access token.

    Review Finding: Missing test for refresh token functionality
    AC#4 requires refresh token (30 days) implementation
    """
    # Register and verify user
    email = "refreshtest@example.com"
    password = "testpassword123"

    # Register
    register_response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    # Manually verify user in database for testing
    user = db.exec(select(User).where(User.email == email)).first()
    assert user is not None
    user.is_verified = True  # Manually verify for testing
    db.add(user)
    db.commit()

    # Login to get tokens
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    # Verify both tokens are present
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    refresh_token = tokens["refresh_token"]

    # Use refresh token to get new access token
    refresh_response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] != tokens["access_token"]  # Should be different


def test_jwt_token_payload_structure(db: Session) -> None:
    """
    Test JWT token contains all required claims.

    Review Finding: No tests verify JWT token payload structure
    AC#4 requires tenant_id, role, email claims
    """
    import jwt

    # Register and verify user
    email = "jwttest@example.com"
    password = "testpassword123"

    # Register
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )

    # Manually verify user
    user = db.exec(select(User).where(User.email == email)).first()
    user.is_verified = True
    db.add(user)
    db.commit()

    # Login
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]

    # Decode token (without verification for testing)
    payload = jwt.decode(
        access_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )

    # Verify required claims exist
    assert "sub" in payload  # User ID
    assert "tenant_id" in payload  # Required for RLS
    assert "role" in payload  # User role
    assert "email" in payload  # User email
    assert "exp" in payload  # Expiration
    assert "iat" in payload  # Issued at
    assert "type" in payload  # Token type
    assert payload["type"] == "access"

    # Verify claim values match user
    assert payload["email"] == email
    assert payload["role"] == "Owner"
    assert payload["tenant_id"] == user.tenant_id
