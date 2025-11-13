"""Task queue endpoints for background job management.

Provides endpoints to:
- Queue background tasks
- Check task status
- Retrieve task results
"""
from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.workers.celery_app import celery_app
from app.workers.tasks import sample_task

router = APIRouter(tags=["tasks"])


class SampleTaskRequest(BaseModel):
    """Request body for sample task."""

    param1: str
    param2: int


class TaskResponse(BaseModel):
    """Response for task creation."""

    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    """Response for task status check."""

    task_id: str
    status: str
    result: Any | None = None
    error: str | None = None


@router.post(
    "/sample", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED
)
async def queue_sample_task(request: SampleTaskRequest) -> TaskResponse:
    """Queue a sample background task.

    Args:
        request: Task parameters (param1, param2)

    Returns:
        TaskResponse with task_id for status tracking
    """
    # Queue the task
    task = sample_task.delay(request.param1, request.param2)

    return TaskResponse(
        task_id=task.id,
        status="queued",
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get status and result of a background task.

    Args:
        task_id: Celery task ID

    Returns:
        TaskStatusResponse with current status and result (if complete)

    Raises:
        HTTPException: If task_id is invalid
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        response = TaskStatusResponse(
            task_id=task_id,
            status=task_result.status.lower(),
        )

        if task_result.ready():
            if task_result.successful():
                response.result = task_result.result
            elif task_result.failed():
                response.error = str(task_result.info)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task ID or error retrieving status: {str(e)}",
        )
