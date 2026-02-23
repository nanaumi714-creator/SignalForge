"""API endpoints for current SCOUT status."""

import logging

from fastapi import APIRouter, HTTPException

from db.queries import get_latest_run
from models.schemas import ScoutStatusResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/scout/status", tags=["status"])


@router.get("", response_model=ScoutStatusResponse)
async def get_status():
    """Return latest run status for operations visibility."""
    try:
        latest = get_latest_run()
        if not latest:
            return ScoutStatusResponse(status="idle")

        return ScoutStatusResponse(
            run_id=str(latest["id"]),
            status=latest["status"],
            run_type=latest.get("run_type"),
            summary=latest.get("summary"),
            started_at=latest.get("started_at"),
            finished_at=latest.get("finished_at"),
        )
    except Exception as exc:
        logger.exception("Failed to fetch latest scout status.")
        raise HTTPException(status_code=500, detail=str(exc))
