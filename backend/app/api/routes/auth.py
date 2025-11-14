"""
Authentication routes for registration and login.

Provides endpoints for:
- User registration with multi-tenant support
- Login with JWT tokens
- User profile management
"""

import logging
import uuid
from datetime import timedelta
from typing import Any

import jwt
import sentry_sdk
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import get_current_active_user
from app.core.config import settings
from app.core.db import get_async_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models import Message, Tenant, Token, User, UserPublic, UserRegister

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

    # TODO: Send verification email (Story 2.1 subtask - email verification)
    # For now, just return the user

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

    # Create refresh token (30 days expiration per Story 2.1 AC#4)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=refresh_token_expires,
    )

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
    Refresh access token using a valid refresh token.

    **Flow:**
    1. Validate the refresh token
    2. Extract user ID from token
    3. Load user from database
    4. Generate new access token with current user data
    5. Return new access token

    **Security:**
    - Refresh token must be valid and not expired
    - Refresh token must have type="refresh"
    - Returns 401 if token is invalid, expired, or user not found
    - New access token includes current user data (role, tenant_id may have changed)

    **Request:**
    - refresh_token: JWT refresh token (from login response)

    **Response:**
    - access_token: New JWT access token (24 hour expiration)
    - token_type: "bearer"
    """
    try:
        # Decode and validate refresh token
        payload = decode_token(refresh_token)

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected refresh token.",
            )

        # Get user ID from token
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Convert to UUID and fetch user
        user_id = uuid.UUID(user_id_str)
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Check if user is still active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
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

        return Token(access_token=access_token, token_type="bearer")

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired refresh token: {str(e)}",
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
async def logout() -> Any:
    """
    Logout endpoint (stateless JWT).

    Since we use stateless JWT tokens, logout is handled client-side
    by deleting the token from storage.

    For production, consider implementing token blacklisting using Redis
    (Story 1.4 Redis infrastructure is available).
    """
    return Message(message="Successfully logged out")
