"""Database query layer for SCOUT SYSTEM."""

from __future__ import annotations

import logging
from typing import Any

from db.client import get_supabase_client

logger = logging.getLogger(__name__)

ALLOWED_RUN_STATUS = {"running", "success", "failed"}
ALLOWED_RUN_TYPE = {"manual", "scheduled"}


def insert_run(run_type: str, config: dict[str, Any]) -> str:
    """Insert a run row and return run_id (UUID string)."""

    try:
        if run_type not in ALLOWED_RUN_TYPE:
            raise ValueError(f"Invalid run_type: {run_type}")

        sb = get_supabase_client()
        response = (
            sb.table("scout_runs")
            .insert({"run_type": run_type, "status": "running", "config": config})
            .execute()
        )

        data = response.data or []
        if not data or "id" not in data[0]:
            raise ValueError("Insert run response does not include run id.")

        return str(data[0]["id"])
    except Exception:
        logger.exception("Failed to insert run. run_type=%s", run_type)
        raise


def update_run_status(run_id: str, status: str, summary: dict[str, Any] | None = None) -> None:
    """Update run status and optional summary."""

    try:
        if status not in ALLOWED_RUN_STATUS:
            raise ValueError(f"Invalid status: {status}")

        payload: dict[str, Any] = {"status": status}
        if summary is not None:
            payload["summary"] = summary

        sb = get_supabase_client()
        sb.table("scout_runs").update(payload).eq("id", run_id).execute()
    except Exception:
        logger.exception("Failed to update run status. run_id=%s status=%s", run_id, status)
        raise
