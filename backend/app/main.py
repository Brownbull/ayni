import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.middleware.error_handlers import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware

# Import Celery app for task autodiscovery
from app.workers.celery_app import celery_app  # noqa: F401


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Middleware Stack (order matters!)
# 1. CORS Middleware (must be first to handle preflight requests)
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 2. Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 3. Exception Handlers (register after middleware)
register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health():
    """Basic health check endpoint for load balancers.

    This endpoint has no external dependencies and always returns healthy
    if the application is running. Use /api/v1/health for detailed checks.
    """
    return {"status": "healthy"}
