"""
Global exception handlers for consistent error formatting.

All errors return a consistent format:
{
    "error": "Error Type",
    "detail": {...},
    "request_id": "uuid",
    "timestamp": "ISO8601"
}
"""

import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("ayni.api")


def format_error_response(
    error_type: str,
    detail: Any,
    request_id: str | None = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> JSONResponse:
    """Format error response consistently.

    Args:
        error_type: Type of error (e.g., "Validation Error", "Not Found")
        detail: Error details
        request_id: Optional request ID from logging middleware
        status_code: HTTP status code

    Returns:
        JSONResponse with consistent error format
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "detail": detail,
            "request_id": request_id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle FastAPI HTTPException with consistent formatting."""
        request_id = getattr(request.state, "request_id", None)

        logger.warning(
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "path": request.url.path,
            },
        )

        return format_error_response(
            error_type=f"HTTP {exc.status_code}",
            detail=exc.detail,
            request_id=request_id,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic RequestValidationError with consistent formatting."""
        request_id = getattr(request.state, "request_id", None)

        # Format validation errors for better readability
        errors = exc.errors()

        logger.warning(
            f"Validation error: {len(errors)} errors",
            extra={
                "request_id": request_id,
                "error_count": len(errors),
                "path": request.url.path,
            },
        )

        return format_error_response(
            error_type="Validation Error",
            detail=errors,
            request_id=request_id,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all handler for unexpected exceptions."""
        request_id = getattr(request.state, "request_id", None)

        # Log full exception details for debugging
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "exception_type": type(exc).__name__,
            },
        )

        # Return safe error message to client (don't expose internal details)
        return format_error_response(
            error_type="Internal Server Error",
            detail="An unexpected error occurred. Please try again later.",
            request_id=request_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
