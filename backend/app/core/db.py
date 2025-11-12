from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

# Async engine with connection pooling for production scalability
# Min connections: 5 (reduce cold start latency)
# Max connections: 20 (prevent connection exhaustion)
# Pool recycle: 3600s (1 hour) - recycle connections to avoid stale connections
# Timeout: 30s - max time to wait for connection from pool
async_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Min connections
    max_overflow=15,  # Max additional connections (total max = 20)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Wait up to 30s for connection
)

# Sync engine for backwards compatibility (migrations, scripts)
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI).replace("+asyncpg", "+psycopg")
)

# Async session maker
async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
