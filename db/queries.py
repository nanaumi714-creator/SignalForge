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


def upsert_entity(
    platform: str,
    platform_id: str,
    channel_title: str | None = None,
    channel_description: str | None = None,
    country: str | None = None,
    language: str | None = None,
    published_at: str | None = None,
) -> str:
    """Upsert entity (creator) and return its UUID."""

    try:
        sb = get_supabase_client()
        payload = {
            "platform": platform,
            "platform_id": platform_id,
        }
        if channel_title:
            payload["channel_title"] = channel_title
        if channel_description:
            payload["channel_description"] = channel_description
        if country:
            payload["country"] = country
        if language:
            payload["language"] = language
        if published_at:
            payload["published_at"] = published_at

        # Use ON CONFLICT (platform, platform_id) DO UPDATE implicitly via upsert
        response = sb.table("scout_entities").upsert(
            payload, on_conflict="platform,platform_id"
        ).execute()

        data = response.data or []
        if not data or "id" not in data[0]:
            raise ValueError("Upsert entity response does not include entity id.")

        return str(data[0]["id"])
    except Exception:
        logger.exception("Failed to upsert entity. platform=%s, id=%s", platform, platform_id)
        raise


def insert_snapshot(
    run_id: str,
    entity_id: str,
    subscriber_count: int | None = None,
    view_count: int | None = None,
    video_count: int | None = None,
) -> str:
    """Insert a snapshot for an entity."""

    try:
        sb = get_supabase_client()
        payload = {
            "run_id": run_id,
            "entity_id": entity_id,
            "subscriber_count": subscriber_count,
            "view_count": view_count,
            "video_count": video_count,
        }
        response = sb.table("scout_snapshots").insert(payload).execute()

        data = response.data or []
        if not data or "id" not in data[0]:
            raise ValueError("Insert snapshot response does not include snapshot id.")

        return str(data[0]["id"])
    except Exception:
        logger.exception("Failed to insert snapshot. run_id=%s, entity_id=%s", run_id, entity_id)
        raise
