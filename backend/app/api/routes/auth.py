"""
Authentication routes for registration and login.

Provides endpoints for:
- User registration with multi-tenant support
- Login with JWT tokens
- User profile management
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import sentry_sdk
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app import utils
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.core.db import get_async_session
from app.core.redis import RedisClient
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_verification_token,
    encrypt_token,
    get_password_hash,
    verify_email_token,
    verify_password,
    verify_password_reset_token,
)
from app.models import (
    Message,
    OAuthAccount,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshToken,
    ResendVerificationRequest,
    Tenant,
    Token,
    User,
    UserPublic,
    UserRegister,
)
from app.services.token_service import (
    create_and_store_refresh_token,
    invalidate_refresh_token,
    revoke_all_user_tokens,
    verify_refresh_token,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/auth/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
async def register(
    user_in: UserRegister,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    Register a new user with automatic tenant creation.

    This endpoint creates both a user and an associated tenant record atomically.
    The user becomes the "Owner" of the new tenant.

    **Business Logic:**
    - Creates a new tenant record
    - Creates user with tenant_id reference
    - Sets role to "Owner" by default
    - Hashes password with bcrypt cost factor 12
    - Marks email as unverified (verification required before login)

    **Security:**
    - Password must be minimum 8 characters
    - Email must be unique
    - Password is hashed with bcrypt (cost factor 12)

    **Returns:**
    - User profile (excluding password hash)
    - 400 if email already exists
    - 422 if validation fails
    """
    # Check if user already exists
    result = await session.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Create tenant first
    tenant = Tenant()
    session.add(tenant)
    await session.flush()  # Get tenant ID

    # Create user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        tenant_id=tenant.id,
        role="Owner",
        is_verified=False,  # Requires email verification
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Log successful registration with Sentry breadcrumb
    sentry_sdk.add_breadcrumb(
        category="auth",
        message="User registered successfully",
        level="info",
        data={
            "user_id": str(user.id),
            "tenant_id": user.tenant_id,
            "email": user.email,
        },
    )
    logger.info(
        f"User registered: {user.email} (user_id={user.id}, tenant_id={user.tenant_id})"
    )

    # Send verification email (only if email is configured)
    if settings.emails_enabled:
        try:
            verification_token = create_verification_token(user.id)
            email_data = utils.generate_verification_email(
                email_to=user.email, token=verification_token
            )
            utils.send_email(
                email_to=user.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
            logger.info(f"Verification email sent to {user.email} (user_id={user.id})")
        except Exception as e:
            logger.error(
                f"Failed to send verification email to {user.email}: {str(e)}",
                exc_info=True,
            )
            # Don't fail registration if email sending fails
            # User can request verification email resend later
    else:
        verification_token = create_verification_token(user.id)
        logger.warning(
            f"Email disabled - verification token for {user.email}: {verification_token[:30]}..."
        )

    return user


@router.post("/auth/login", response_model=Token, tags=["auth"])
async def login(
    session: AsyncSession = Depends(get_async_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Login endpoint using OAuth2 password flow.

    **Authentication:**
    - Validates email and password
    - Checks if email is verified
    - Returns JWT access token on success

    **Security:**
    - Returns 401 for invalid credentials
    - Returns 401 for unverified email
    - TODO: Add rate limiting (5 attempts per 15 min)

    **Request:**
    - username: User's email address
    - password: User's password

    **Response:**
    - access_token: JWT token (24 hour expiration)
    - token_type: "bearer"
    """
    # Get user by email (form_data.username is actually the email)
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt
        sentry_sdk.add_breadcrumb(
            category="auth",
            message="Failed login attempt",
            level="warning",
            data={"email": form_data.username, "reason": "invalid_credentials"},
        )
        logger.warning(f"Failed login attempt for email: {form_data.username}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Check if email is verified (AC#4 requirement)
    # NOTE: Email verification flow is implemented in Story 2.2
    # For development/testing, you can temporarily set is_verified=True in the database
    if not user.is_verified:
        # Log unverified email login attempt
        sentry_sdk.add_breadcrumb(
            category="auth",
            message="Login attempt with unverified email",
            level="warning",
            data={"user_id": str(user.id), "email": user.email},
        )
        logger.warning(
            f"Login attempt with unverified email: {user.email} (user_id={user.id})"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your email for verification link.",
        )

    # Create access token with multi-tenant claims
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        tenant_id=user.tenant_id,
        role=user.role,
        email=user.email,
    )

    # Create and store refresh token in database (30 days expiration per Story 2.3 AC#1)
    refresh_token = await create_and_store_refresh_token(user.id, session)

    # Log successful login
    sentry_sdk.add_breadcrumb(
        category="auth",
        message="User logged in successfully",
        level="info",
        data={
            "user_id": str(user.id),
            "tenant_id": user.tenant_id,
            "email": user.email,
            "role": user.role,
        },
    )
    logger.info(
        f"User logged in: {user.email} (user_id={user.id}, tenant_id={user.tenant_id})"
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.post("/auth/refresh", response_model=Token, tags=["auth"])
async def refresh_access_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    Refresh access token using a valid refresh token with rotation.

    **Flow:**
    1. Validate the refresh token from database
    2. Check if token exists, not used, not revoked, not expired
    3. Load user from database
    4. Generate new access token with current user data
    5. Generate new refresh token (rotation)
    6. Invalidate old refresh token (mark as used)
    7. Return new access and refresh tokens

    **Security (Story 2.3 AC#3-4):**
    - Refresh token must be valid and not expired
    - Refresh token must exist in database (not used, not revoked)
    - Token rotation: old token invalidated, new one issued
    - Returns 401 if token is invalid, expired, used, or user not found
    - New access token includes current user data (role, tenant_id may have changed)

    **Request:**
    - refresh_token: JWT refresh token (from login response)

    **Response:**
    - access_token: New JWT access token (24 hour expiration)
    - refresh_token: New JWT refresh token (30 day expiration)
    - token_type: "bearer"
    """
    # Verify refresh token from database
    user = await verify_refresh_token(refresh_token, session)

    if not user:
        # Log failed refresh attempt
        logger.warning("Failed refresh token attempt: invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Generate new access token with CURRENT user data
    # (role, tenant_id, email may have changed since refresh token was issued)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        tenant_id=user.tenant_id,
        role=user.role,
        email=user.email,
    )

    # Generate new refresh token (rotation per Story 2.3 AC#4)
    new_refresh_token = await create_and_store_refresh_token(user.id, session)

    # Invalidate old refresh token (mark as used)
    await invalidate_refresh_token(refresh_token, session, mark_as="used")

    # Log successful token refresh
    logger.info(f"Token refreshed for user {user.email} (user_id={user.id})")

    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
    )


@router.get("/users/me", response_model=UserPublic, tags=["users"])
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current authenticated user profile.

    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post("/auth/logout", response_model=Message, tags=["auth"])
async def logout(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    Logout endpoint with refresh token revocation.

    **Flow:**
    1. Get current authenticated user from JWT
    2. Revoke all refresh tokens for this user
    3. Return success message

    **Security (Story 2.3 AC#2, AC#4):**
    - Revokes all refresh tokens for the user (logout from all devices)
    - Client must delete access token from storage
    - Access tokens continue to work until expiration (24h max)

    **Note:**
    For single-device logout with Redis blacklist, see Story 2.3 technical notes.
    Current implementation revokes all refresh tokens for security.
    """
    # Revoke all refresh tokens for this user
    revoked_count = await revoke_all_user_tokens(current_user.id, session)

    # Log logout
    logger.info(
        f"User logged out: {current_user.email} (user_id={current_user.id}, tokens_revoked={revoked_count})"
    )

    return Message(message="Successfully logged out")


@router.post("/auth/verify-email", response_model=Message, tags=["auth"])
async def verify_email(
    token: str,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    Verify user email address via JWT token.

    **Flow:**
    1. Decode and validate verification token
    2. Extract user_id from token
    3. Find user in database
    4. Mark email as verified
    5. Return success message

    **Security:**
    - Token must be valid and not expired (24h TTL)
    - Token type must be "email_verification"
    - Operation is idempotent (can be called multiple times safely)

    **Request:**
    - token: JWT verification token (from email link)

    **Response:**
    - 200: Email verified successfully
    - 400: Token expired or invalid
    - 404: User not found
    """
    try:
        # Decode token and extract user_id
        user_id_str = verify_email_token(token)
        user_id = uuid.UUID(user_id_str)

        # Find user in database
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if already verified (idempotent)
        if user.is_verified:
            logger.info(
                f"Email already verified for user {user.email} (user_id={user.id})"
            )
            return Message(message="Email already verified")

        # Update is_verified field
        user.is_verified = True
        session.add(user)
        await session.commit()

        # Log successful verification
        sentry_sdk.add_breadcrumb(
            category="auth",
            message="Email verified successfully",
            level="info",
            data={
                "user_id": str(user.id),
                "email": user.email,
            },
        )
        logger.info(f"Email verified for user {user.email} (user_id={user.id})")

        return Message(message="Email verified successfully")

    except ValueError as e:
        # Token expired or invalid
        logger.warning(f"Email verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/auth/resend-verification", response_model=Message, tags=["auth"])
async def resend_verification(
    request: ResendVerificationRequest,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    Resend email verification link with rate limiting.

    **Flow:**
    1. Check rate limit (1 resend per 60 seconds per email)
    2. Find user by email
    3. Generate new verification token
    4. Send verification email
    5. Set rate limit in Redis

    **Security:**
    - Rate limited to 1 request per 60 seconds per email
    - Always returns success to prevent email enumeration
    - Only sends email if user exists and is not verified
    - Uses Redis for distributed rate limiting

    **Request:**
    - email: User's email address

    **Response:**
    - 200: Success message (always, even if email doesn't exist)
    - 429: Rate limit exceeded
    """
    email = request.email

    # Rate limiting: check Redis cache
    redis = await RedisClient.get_client()
    rate_limit_key = f"resend_verification:{email}"

    if await redis.get(rate_limit_key):
        logger.warning(f"Rate limit exceeded for email verification resend: {email}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 60 seconds before requesting another email",
        )

    # Find user by email
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Security: Always return success to prevent email enumeration
    response_message = (
        "If this email exists and is not verified, a verification link has been sent"
    )

    if user and not user.is_verified:
        # Generate new verification token
        token = create_verification_token(user.id)

        # Send verification email (only if email is configured)
        if settings.emails_enabled:
            try:
                email_data = utils.generate_verification_email(
                    email_to=user.email, token=token
                )
                utils.send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )
                logger.info(
                    f"Verification email resent to {user.email} (user_id={user.id})"
                )
            except Exception as e:
                logger.error(
                    f"Failed to resend verification email to {user.email}: {str(e)}",
                    exc_info=True,
                )
                # Don't expose email sending failure to prevent information leakage
        else:
            logger.warning(
                f"Email disabled - verification token for {user.email}: {token[:30]}..."
            )

        # Set rate limit in Redis (60 second TTL)
        await redis.setex(rate_limit_key, 60, "1")

        # Log resend attempt
        sentry_sdk.add_breadcrumb(
            category="auth",
            message="Verification email resent",
            level="info",
            data={
                "user_id": str(user.id),
                "email": user.email,
            },
        )
        logger.info(f"Verification email resent to {user.email} (user_id={user.id})")
    elif user and user.is_verified:
        # User already verified - still return success but don't send email
        logger.info(f"Resend verification requested for already verified user: {email}")
    else:
        # User doesn't exist - still return success for security
        logger.info(f"Resend verification requested for non-existent email: {email}")

    return Message(message=response_message)


# ============================================================================
# Google OAuth 2.0 Endpoints (Story 2.5)
# ============================================================================


@router.get(
    "/auth/google/authorize",
    response_model=dict[str, str],
    tags=["auth"],
)
async def google_authorize(
    request: Request,
    redis: Redis = Depends(RedisClient.get_client),
) -> dict[str, str]:
    """
    Generate Google OAuth authorization URL.

    This endpoint creates a Google OAuth authorization URL with a state parameter
    for CSRF protection. The state is stored in Redis with a 5-minute TTL.

    **OAuth Flow:**
    1. Frontend calls this endpoint
    2. Backend generates authorization URL with state parameter
    3. Frontend redirects user to Google consent screen
    4. User authorizes
    5. Google redirects back to callback endpoint

    **Security:**
    - State parameter stored in Redis (5-minute TTL) for CSRF protection
    - HTTPS enforced in production (Google requirement)
    - Rate limiting: 10 requests per minute per IP

    **Returns:**
    - authorization_url: Google OAuth consent screen URL
    """
    try:
        from app.core.oauth import google_oauth_client

        if not google_oauth_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth is not configured. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET environment variables.",
            )

        # Rate limiting: 10 requests per minute per IP
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = f"oauth_authorize:{client_ip}"

        # Get current count
        current_count = await redis.get(rate_limit_key)
        if current_count and int(current_count) >= 10:
            logger.warning(
                f"Rate limit exceeded for OAuth authorize from IP: {client_ip}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OAuth authorization requests. Please try again in 1 minute.",
            )

        # Increment rate limit counter (60 second TTL)
        if current_count:
            await redis.incr(rate_limit_key)
        else:
            await redis.setex(rate_limit_key, 60, "1")

        # Generate random state parameter for CSRF protection
        import secrets

        state = secrets.token_urlsafe(32)

        # Store state in Redis with 5-minute expiration
        await redis.setex(f"oauth_state:{state}", 300, "1")

        # Generate authorization URL
        authorization_url = await google_oauth_client.get_authorization_url(
            redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI,
            state=state,
            scope=["openid", "email", "profile"],
        )

        logger.info(
            f"Generated Google OAuth authorization URL with state: {state[:8]}... from IP: {client_ip}"
        )

        return {"authorization_url": authorization_url}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the actual error for debugging
        logger.error(
            f"OAuth authorize error: {type(e).__name__}: {str(e)}", exc_info=True
        )
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth authorization URL: {str(e)}",
        )


@router.get(
    "/auth/google/callback",
    tags=["auth"],
)
async def google_callback(
    code: str,
    state: str,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(RedisClient.get_client),
) -> RedirectResponse:
    """
    Google OAuth callback handler.

    This endpoint handles the OAuth callback from Google, validates the state parameter,
    exchanges the authorization code for an access token, fetches the user profile,
    and creates or links the user account.

    **Account Merging Logic:**
    - **New user (email not in system):** Create user with is_verified=True, insert oauth_accounts entry
    - **Existing email/password user:** Link OAuth to existing account, update profile
    - **Existing OAuth user:** Update tokens (refresh access token, expires_at)

    **Security:**
    - State parameter validation (CSRF protection)
    - OAuth tokens encrypted before database storage
    - Rate limiting: 10 requests per minute per IP

    **Returns:**
    - Redirects to frontend with access_token and refresh_token as URL parameters
    """
    from app.core.oauth import google_oauth_client

    if not google_oauth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    # Rate limiting: 10 requests per minute per IP
    client_ip = request.client.host if request.client else "unknown"
    rate_limit_key = f"oauth_callback:{client_ip}"

    # Get current count
    current_count = await redis.get(rate_limit_key)
    if current_count and int(current_count) >= 10:
        logger.warning(f"Rate limit exceeded for OAuth callback from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OAuth callback requests. Please try again in 1 minute.",
        )

    # Increment rate limit counter (60 second TTL)
    if current_count:
        await redis.incr(rate_limit_key)
    else:
        await redis.setex(rate_limit_key, 60, "1")

    # Validate state parameter (CSRF protection)
    stored_state = await redis.get(f"oauth_state:{state}")
    if not stored_state:
        logger.warning(f"Invalid or expired OAuth state: {state[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter. Please try again.",
        )

    # Delete used state
    await redis.delete(f"oauth_state:{state}")

    try:
        # Exchange authorization code for access token
        token_response = await google_oauth_client.get_access_token(
            code, redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
        )

        # Fetch user profile from Google
        user_id, user_email = await google_oauth_client.get_id_email(
            token_response["access_token"]
        )

        # Get additional profile info (name, picture)
        import httpx

        async with httpx.AsyncClient() as client:
            profile_response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {token_response['access_token']}"},
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()

        logger.info(f"Google OAuth callback for email: {user_email}")

    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google. Please try again.",
        )

    # Check if user exists by email (case-insensitive)
    from sqlalchemy import func

    result = await session.execute(
        select(User).where(func.lower(User.email) == user_email.lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # Check if OAuth account already exists
        oauth_result = await session.execute(
            select(OAuthAccount).where(
                OAuthAccount.user_id == existing_user.id,
                OAuthAccount.oauth_name == "google",
            )
        )
        existing_oauth = oauth_result.scalar_one_or_none()

        if existing_oauth:
            # Update existing OAuth tokens
            existing_oauth.access_token = encrypt_token(token_response["access_token"])
            existing_oauth.refresh_token = (
                encrypt_token(token_response["refresh_token"])
                if token_response.get("refresh_token")
                else None
            )
            existing_oauth.expires_at = (
                datetime.utcnow()
                + timedelta(seconds=token_response.get("expires_in", 3600))
                if token_response.get("expires_in")
                else None
            )
            existing_oauth.updated_at = datetime.utcnow()
            session.add(existing_oauth)

            logger.info(
                f"Updated OAuth tokens for existing user: {user_email} (user_id={existing_user.id})"
            )
        else:
            # Link OAuth to existing account (account merging)
            new_oauth_account = OAuthAccount(
                user_id=existing_user.id,
                oauth_name="google",
                access_token=encrypt_token(token_response["access_token"]),
                refresh_token=(
                    encrypt_token(token_response["refresh_token"])
                    if token_response.get("refresh_token")
                    else None
                ),
                expires_at=(
                    datetime.utcnow()
                    + timedelta(seconds=token_response.get("expires_in", 3600))
                    if token_response.get("expires_in")
                    else None
                ),
                account_id=user_id,
                account_email=user_email,
            )
            session.add(new_oauth_account)

            # Update user profile with Google name if not set
            if not existing_user.full_name and profile_data.get("name"):
                existing_user.full_name = profile_data["name"]
                session.add(existing_user)

            logger.info(
                f"Linked Google OAuth to existing account: {user_email} (user_id={existing_user.id})"
            )
            sentry_sdk.add_breadcrumb(
                category="auth",
                message="OAuth account merged",
                level="info",
                data={
                    "user_id": str(existing_user.id),
                    "email": user_email,
                    "oauth_provider": "google",
                },
            )

        user = existing_user
    else:
        # Create new user with Google profile data
        # First create tenant (multi-tenant requirement)
        new_tenant = Tenant()
        session.add(new_tenant)
        await session.flush()  # Get tenant.id

        new_user = User(
            email=user_email,
            full_name=profile_data.get("name"),
            is_verified=True,  # Google emails are pre-verified
            tenant_id=new_tenant.id,
            role="Owner",  # Default role for new tenant owner
            hashed_password=None,  # OAuth-only user (no password)
        )
        session.add(new_user)
        await session.flush()  # Get user.id

        # Create OAuth account record
        oauth_account = OAuthAccount(
            user_id=new_user.id,
            oauth_name="google",
            access_token=encrypt_token(token_response["access_token"]),
            refresh_token=(
                encrypt_token(token_response["refresh_token"])
                if token_response.get("refresh_token")
                else None
            ),
            expires_at=(
                datetime.utcnow()
                + timedelta(seconds=token_response.get("expires_in", 3600))
                if token_response.get("expires_in")
                else None
            ),
            account_id=user_id,
            account_email=user_email,
        )
        session.add(oauth_account)

        logger.info(
            f"Created new user via Google OAuth: {user_email} (user_id={new_user.id})"
        )
        sentry_sdk.add_breadcrumb(
            category="auth",
            message="New user created via OAuth",
            level="info",
            data={
                "user_id": str(new_user.id),
                "email": user_email,
                "oauth_provider": "google",
            },
        )

        user = new_user

    await session.commit()
    await session.refresh(user)

    # Generate JWT access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        tenant_id=user.tenant_id,
        role=user.role,
        email=user.email,
    )

    # Create and store refresh token
    refresh_token = await create_and_store_refresh_token(
        user_id=user.id,
        session=session,
    )

    logger.info(f"Google OAuth login successful for: {user.email} (user_id={user.id})")

    # Redirect to frontend with tokens as URL parameters
    # Frontend will extract tokens and store them in localStorage
    frontend_url = settings.FRONTEND_HOST
    callback_params = urlencode(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )
    redirect_url = f"{frontend_url}/auth/callback?{callback_params}"

    return RedirectResponse(url=redirect_url, status_code=302)


# ============================================================================
# Password Reset Endpoints (Story 2.4)
# ============================================================================


@router.post("/auth/reset-password", response_model=Message, tags=["auth"])
async def request_password_reset(
    *,
    request_data: PasswordResetRequest,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(RedisClient.get_client),
) -> Any:
    """
    Request password reset email with rate limiting.

    **Flow:**
    1. Check rate limit (3 requests per hour per email)
    2. Find user by email
    3. Generate password reset token (1-hour expiration)
    4. Send password reset email
    5. Log request for security monitoring

    **Security (Story 2.4 AC#1):**
    - Rate limited to 3 requests per hour per email
    - Always returns success to prevent email enumeration
    - Only sends email if user exists and is verified
    - Token expires in 1 hour (stricter than access tokens)
    - Uses Redis for distributed rate limiting

    **Request:**
    - email: User's email address

    **Response:**
    - 200: Success message (always, even if email doesn't exist)
    - 429: Rate limit exceeded
    """
    # Rate limiting: 3 requests per hour per email
    email = request_data.email
    rate_limit_key = f"password_reset:{email}"

    # Get current count for this email
    current_count = await redis.get(rate_limit_key)
    if current_count and int(current_count) >= 3:
        logger.warning(f"Rate limit exceeded for password reset: {email}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please try again in 1 hour.",
        )

    # Increment rate limit counter (1 hour TTL)
    if current_count:
        await redis.incr(rate_limit_key)
    else:
        await redis.setex(rate_limit_key, 3600, "1")  # 1 hour = 3600 seconds

    # Find user by email (case-insensitive)
    from sqlalchemy import func

    result = await session.execute(
        select(User).where(func.lower(User.email) == email.lower())
    )
    user = result.scalar_one_or_none()

    # Security: Always return success to prevent email enumeration
    response_message = (
        "If an account exists with this email, you will receive a password reset link"
    )

    if user:
        # Generate password reset token (1-hour expiration)
        reset_token = create_password_reset_token(user.id, user.email)

        # Send password reset email
        from app.utils import generate_reset_password_email, send_email

        email_data = generate_reset_password_email(
            email_to=user.email,
            email=user.email,
            token=reset_token,
        )

        try:
            send_email(
                email_to=user.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

            logger.info(
                f"Password reset email sent to {user.email} (user_id={user.id})"
            )

            # Log for security monitoring
            sentry_sdk.add_breadcrumb(
                category="auth",
                message="Password reset requested",
                level="info",
                data={
                    "user_id": str(user.id),
                    "email": user.email,
                },
            )
        except Exception as e:
            # Log error but still return success (prevent email enumeration)
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            sentry_sdk.capture_exception(e)
    else:
        # User doesn't exist - still return success for security
        logger.info(f"Password reset requested for non-existent email: {email}")

        # Log for security monitoring
        sentry_sdk.add_breadcrumb(
            category="auth",
            message="Password reset requested for non-existent email",
            level="warning",
            data={"email": email},
        )

    return Message(message=response_message)


@router.post("/auth/confirm-reset", response_model=Message, tags=["auth"])
async def confirm_password_reset(
    *,
    request_data: PasswordResetConfirm,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(RedisClient.get_client),
) -> Any:
    """
    Confirm password reset with token and new password.

    **Flow:**
    1. Check if token already used (Redis blacklist)
    2. Validate reset token (signature, expiration, type)
    3. Extract user_id from token payload
    4. Update user password with bcrypt hash
    5. Invalidate all refresh tokens (force re-login)
    6. Add token to Redis blacklist (prevent reuse)
    7. Send confirmation email
    8. Return success message

    **Security (Story 2.4 AC#2-4):**
    - Token must be valid password_reset type (not access/refresh)
    - Token must not be expired (1-hour TTL)
    - Token must not be already used (Redis blacklist check)
    - Password must be minimum 8 characters
    - All user sessions invalidated after password change
    - Token blacklisted after successful use (prevent replay attacks)

    **Request:**
    - token: JWT password reset token (from email link)
    - new_password: New password (min 8 characters)

    **Response:**
    - 200: Password reset successful
    - 400: Token invalid or expired
    - 404: User not found
    - 410: Token already used
    """
    token = request_data.token
    new_password = request_data.new_password

    # Validate password length (Pydantic should already do this, but extra check)
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    # Check if token already used (Redis blacklist)
    import hashlib

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    token_blacklist_key = f"reset_token_used:{token_hash}"

    if await redis.get(token_blacklist_key):
        logger.warning("Attempt to reuse password reset token")
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This password reset link has already been used",
        )

    # Verify token
    try:
        payload = verify_password_reset_token(token)
    except ValueError as e:
        logger.warning(f"Invalid password reset token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Get user
    user_id_str = payload["sub"]
    user_id = uuid.UUID(user_id_str)

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update password with bcrypt hash
    user.hashed_password = get_password_hash(new_password)
    session.add(user)

    # Invalidate all refresh tokens for this user (force re-login on all devices)
    from sqlalchemy import update as sql_update

    await session.execute(
        sql_update(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .values(revoked_at=datetime.utcnow())
    )

    await session.commit()

    # Blacklist this reset token (1-hour TTL to match token expiration)
    await redis.setex(token_blacklist_key, 3600, "1")

    # Send confirmation email
    try:
        email_data = utils.generate_password_changed_email(
            email_to=user.email, username=user.email
        )
        utils.send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
        logger.info(
            f"Password changed confirmation email sent to {user.email} (user_id={user.id})"
        )
    except Exception as e:
        # Log error but don't fail the password reset
        logger.error(
            f"Failed to send password changed confirmation email to {user.email}: {str(e)}"
        )
        sentry_sdk.capture_exception(e)

    # Log for security monitoring
    sentry_sdk.add_breadcrumb(
        category="auth",
        message="Password reset completed",
        level="info",
        data={
            "user_id": str(user.id),
            "email": user.email,
        },
    )

    return Message(
        message="Password reset successful. You can now log in with your new password."
    )
