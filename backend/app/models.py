import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

# ============================================================================
# Multi-Tenant Core Models
# ============================================================================


class Tenant(SQLModel, table=True):
    """Root tenant table for multi-tenancy isolation via RLS"""

    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    users: list["User"] = Relationship(back_populates="tenant", cascade_delete=True)
    companies: list["Company"] = Relationship(
        back_populates="tenant", cascade_delete=True
    )


class Company(SQLModel, table=True):
    """Company table with tenant isolation"""

    __tablename__ = "companies"

    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    identifier: str | None = Field(default=None, max_length=50)  # RUT for Chile, tax ID
    country: str = Field(max_length=50, nullable=False)
    industry: str | None = Field(default=None, max_length=100)
    timezone: str = Field(default="America/Santiago", max_length=50)
    opt_in_benchmarking: bool = Field(default=True)
    is_demo: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tenant: Tenant | None = Relationship(back_populates="companies")
    locations: list["Location"] = Relationship(
        back_populates="company", cascade_delete=True
    )


class Location(SQLModel, table=True):
    """Location table with tenant-scoped access via company"""

    __tablename__ = "locations"

    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    address: str | None = Field(default=None)
    website: str | None = Field(default=None, max_length=255)
    is_primary: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    company: Company | None = Relationship(back_populates="locations")


# ============================================================================
# User Models (Extended for Multi-Tenancy)
# ============================================================================


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters long",
    )
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
# Compatible with fastapi-users for authentication
class User(UserBase, table=True):
    """User model with multi-tenant support and fastapi-users integration"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    is_verified: bool = Field(
        default=False, description="Email verification status"
    )  # fastapi-users uses is_verified instead of email_verified

    # Multi-tenant and custom fields
    tenant_id: int | None = Field(default=None, foreign_key="tenants.id", index=True)
    role: str | None = Field(
        default="Owner", max_length=50
    )  # Owner, Manager, Analyst, Viewer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tenant: Tenant | None = Relationship(back_populates="users")
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="user", cascade_delete=True
    )


# RefreshToken model for secure token storage and rotation
class RefreshToken(SQLModel, table=True):
    """Refresh token model for JWT token rotation and session persistence"""

    __tablename__ = "refresh_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    token_hash: str = Field(max_length=255, nullable=False, index=True)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: datetime | None = Field(default=None)
    revoked_at: datetime | None = Field(default=None)

    # Relationships
    user: User | None = Relationship(back_populates="refresh_tokens")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    is_verified: bool


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token and optional refresh token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ResendVerificationRequest(SQLModel):
    email: EmailStr = Field(
        max_length=255, description="Email address to resend verification to"
    )
