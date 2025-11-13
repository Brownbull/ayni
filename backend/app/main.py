import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.api.middleware.performance import performance_middleware
from app.core.config import settings
from app.middleware.error_handlers import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware

# Import Celery app for task autodiscovery
from app.workers.celery_app import celery_app  # noqa: F401


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


def scrub_sensitive_data(event: dict, hint: dict) -> dict | None:  # noqa: ARG001
    """Remove sensitive data from Sentry events before sending."""
    # Scrub password fields
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            for key in ["password", "token", "secret", "jwt", "api_key"]:
                if key in data:
                    data[key] = "[Filtered]"

    # Scrub authorization headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        if isinstance(headers, dict):
            for key in ["Authorization", "X-API-Key", "Cookie"]:
                if key in headers:
                    headers[key] = "[Filtered]"

    return event


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        environment=settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        before_send=scrub_sensitive_data,
        release=os.getenv("GIT_COMMIT_SHA", "unknown"),
        # Enable performance monitoring
        enable_tracing=True,
        # Set sample rate for profiling
        profiles_sample_rate=0.1,
    )

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

# 2. Performance Monitoring Middleware
app.middleware("http")(performance_middleware)

# 3. Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 4. Exception Handlers (register after middleware)
register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health():
    """Basic health check endpoint for load balancers.

    This endpoint has no external dependencies and always returns healthy
    if the application is running. Use /api/v1/health for detailed checks.
    """
    return {"status": "healthy"}
