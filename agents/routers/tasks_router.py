"""agents/routers/tasks_router.py — receive, track, and list tasks."""

import asyncio
import structlog
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter()

# In-memory task store (swap for Redis/Postgres in production)
_tasks: dict = {}


class TaskRequest(BaseModel):
    task_id: str
    workflow_type: str
    input_data: dict = {}
    user_key: str = "default"


@router.post("/tasks")
async def create_task(body: TaskRequest, request: Request):
    supervisor = request.app.state.supervisor
    _tasks[body.task_id] = {"status": "running", "result": None, "error": None,
                             "workflow_type": body.workflow_type}

    logger.info("task.received", task_id=body.task_id, workflow=body.workflow_type)

    asyncio.create_task(
        _run_task(supervisor, body.task_id, body.workflow_type, body.input_data, body.user_key)
    )
    return {"task_id": body.task_id, "status": "accepted"}


async def _run_task(supervisor, task_id: str, workflow_type: str, input_data: dict, user_key: str):
    try:
        result = await supervisor.run(
            task_id=task_id,
            workflow_type=workflow_type,
            input_data=input_data,
            user_key=user_key,
        )
        _tasks[task_id] = {
            "status": "completed",
            "result": result,
            "error": None,
            "workflow_type": workflow_type,
        }
        logger.info("task.completed", task_id=task_id)
    except Exception as e:
        _tasks[task_id] = {
            "status": "failed",
            "result": None,
            "error": str(e),
            "workflow_type": workflow_type,
        }
        logger.error("task.failed", task_id=task_id, error=str(e))


@router.post("/tasks/run")
async def run_task(body: TaskRequest, request: Request):
    """Alias used by the scheduler for cron-triggered workflows."""
    return await create_task(body, request)


@router.get("/tasks/stats")
async def get_stats():
    """Return aggregate task counts."""
    total = len(_tasks)
    counts = {"total": total, "completed": 0, "running": 0, "failed": 0, "pending": 0}
    for t in _tasks.values():
        status = t.get("status", "pending")
        if status in counts:
            counts[status] += 1
    return counts


@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = Query(None),
    workflow_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List tasks with optional status/workflow filter."""
    tasks = []
    for task_id, task in _tasks.items():
        if status and task.get("status") != status:
            continue
        if workflow_type and task.get("workflow_type") != workflow_type:
            continue
        tasks.append({"id": task_id, **task})

    # Most recent first (reverse insertion order)
    tasks = list(reversed(tasks))[:limit]
    return {"tasks": tasks, "total": len(tasks)}


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, **task}
