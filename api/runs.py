"""API endpoints for managing Scout Runs."""

import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException

from db.queries import insert_run, update_run_status # Note: insert_run/update_run_status already exist
from models.schemas import RunRequest, RunResponse, RunStatusResponse
from worker.orchestrator import run_scout
from db.client import get_supabase_client # To fetch status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/scout/runs", tags=["runs"])


@router.post("", response_model=RunResponse)
async def start_run(request: RunRequest, background_tasks: BackgroundTasks):
    """Start a new scout run asynchronously."""
    try:
        run_id = insert_run(request.run_type, request.config)
        background_tasks.add_task(
            run_scout, 
            run_id=run_id, 
            config=request.config, 
            notify_discord=request.notify_discord
        )
        return RunResponse(run_id=run_id, status="running")
    except Exception as e:
        logger.exception("Failed to start scout run.")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{run_id}", response_model=RunStatusResponse)
async def get_run_status(run_id: str):
    """Get the status and summary of a scout run."""
    try:
        sb = get_supabase_client()
        response = sb.table("scout_runs").select("*").eq("id", run_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Run not found")
        
        row = response.data[0]
        return RunStatusResponse(
            run_id=str(row["id"]),
            status=row["status"],
            summary=row.get("summary"),
            started_at=row.get("started_at"),
            finished_at=row.get("finished_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch run status.")
        raise HTTPException(status_code=500, detail=str(e))
