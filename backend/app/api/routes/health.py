"""
Health check endpoints for monitoring and observability.

Provides both basic and detailed health checks:
- Basic: GET /health (no dependencies, for load balancers)
- Detailed: GET /api/v1/health (checks database, Redis, etc.)
"""

import time
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.deps import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def detailed_health(db: SessionDep) -> dict[str, Any]:
    """Detailed health check with service status.

    Checks:
    - Database connectivity and latency
    - Redis connectivity and latency (if configured)

    Returns:
        200: All services healthy
        503: One or more services unhealthy
    """
    health_status: dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {},
    }

    # Check database
    try:
        start = time.time()
        await db.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start) * 1000, 2)
        health_status["services"]["database"] = {
            "status": "healthy",
            "latency_ms": latency_ms,
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "unhealthy"

    # Check Redis (placeholder - not yet implemented in Story 1.3)
    # Redis will be added in Story 1.4
    # For now, we note it as not configured
    health_status["services"]["redis"] = {"status": "not_configured"}

    # Determine HTTP status code based on overall health
    status_code = (
        status.HTTP_200_OK
        if health_status["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    # Return JSONResponse with appropriate status code
    return JSONResponse(status_code=status_code, content=health_status)
