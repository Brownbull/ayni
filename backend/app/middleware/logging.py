"""
Request/Response logging middleware with unique request IDs.

This middleware:
1. Generates a unique UUID request_id for each request
2. Logs incoming requests with method, path, request_id, timestamp
3. Logs outgoing responses with status_code, duration_ms, request_id
4. Adds request_id to request.state for access by exception handlers
"""

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured JSON-like logging
logger = logging.getLogger("ayni.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses with unique request IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request, log details, and measure response time."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store request_id in request state for access by handlers
        request.state.request_id = request_id

        # Log incoming request
        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
            },
        )

        # Measure request duration
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log outgoing response
        logger.info(
            "Outgoing response",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # Add request_id to response headers
        response.headers["X-Request-ID"] = request_id

        return response
