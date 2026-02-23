"""API endpoints for scout reports."""

import logging

from fastapi import APIRouter, HTTPException, Query

from db.queries import get_last_success_run_id, get_top_scores_for_run
from models.schemas import LatestReportResponse, ReportItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/scout/reports", tags=["reports"])


@router.get("/latest", response_model=LatestReportResponse)
async def get_latest_report(n: int = Query(default=10, ge=1, le=20)):
    """Return latest successful run summary for chat surfaces."""
    try:
        run_id = get_last_success_run_id()
        if not run_id:
            raise HTTPException(status_code=404, detail="No successful run found")

        items_raw = get_top_scores_for_run(run_id=run_id, limit=n)
        items = [ReportItem(**item) for item in items_raw]
        return LatestReportResponse(run_id=run_id, item_count=len(items), items=items)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch latest report.")
        raise HTTPException(status_code=500, detail=str(exc))
