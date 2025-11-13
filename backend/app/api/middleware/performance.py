"""Performance monitoring middleware for request timing and slow query detection."""

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logger = logging.getLogger("ayni.api.performance")

# Slow request threshold in milliseconds
SLOW_REQUEST_THRESHOLD_MS = 500


async def performance_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Middleware to track API request performance.

    Measures request duration, logs slow requests, and adds performance
    headers to responses for debugging.

    Args:
        request: Incoming FastAPI request
        call_next: Next middleware/handler in chain

    Returns:
        Response with X-Response-Time header added
    """
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log slow requests
    if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
        logger.warning(
            "Slow request detected",
            extra={
                "path": str(request.url.path),
                "method": request.method,
                "duration_ms": round(duration_ms, 2),
                "status_code": response.status_code,
            },
        )

    # Add performance header for debugging
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

    return response
