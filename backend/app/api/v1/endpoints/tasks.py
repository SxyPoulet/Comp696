"""
API endpoints for task status tracking.
"""

from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from app.api.v1.schemas import TaskStatus
from app.tasks.celery_app import celery_app

router = APIRouter()


@router.get("/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str):
    """
    Get the status of a background task.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if not task_result:
        raise HTTPException(status_code=404, detail="Task not found")

    # Map Celery states to our status format
    status = task_result.state

    result = None
    error = None
    progress = None

    if status == "SUCCESS":
        result = task_result.result
    elif status == "FAILURE":
        error = str(task_result.info)
    elif status == "PROGRESS":
        # If task reported progress
        if isinstance(task_result.info, dict):
            progress = task_result.info.get("progress")
            result = task_result.info

    return TaskStatus(
        task_id=task_id,
        status=status,
        result=result,
        error=error,
        progress=progress
    )


@router.delete("/{task_id}", status_code=204)
def revoke_task(task_id: str):
    """
    Revoke (cancel) a running task.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if not task_result:
        raise HTTPException(status_code=404, detail="Task not found")

    # Revoke the task
    task_result.revoke(terminate=True)

    return None
