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


def get_snapshots_by_run(run_id: str) -> list[dict[str, Any]]:
    """Fetch snapshots and joined entity data for a run."""

    try:
        sb = get_supabase_client()
        response = (
            sb.table("scout_snapshots")
            .select(
                "entity_id, subscriber_count, view_count, "
                "scout_entities!inner(channel_title)"
            )
            .eq("run_id", run_id)
            .execute()
        )
        rows = response.data or []
        results: list[dict[str, Any]] = []

        for row in rows:
            entity = row.get("scout_entities") or {}
            results.append(
                {
                    "entity_id": str(row["entity_id"]),
                    "display_name": entity.get("channel_title") or "Unknown channel",
                    "category": None,
                    "subscribers": row.get("subscriber_count"),
                    "total_views": row.get("view_count"),
                    "upload_freq_days": None,
                    "recent_videos_json": [],
                }
            )

        return results
    except Exception:
        logger.exception("Failed to fetch snapshots by run. run_id=%s", run_id)
        raise


def insert_score(
    run_id: str,
    entity_id: str,
    score_data: dict[str, Any],
    gpt_model: str,
) -> str:
    """Insert or update score row and return score id."""

    try:
        total_score = (
            int(score_data["demand_match"])
            + int(score_data["improvement_potential"])
            + int(score_data["ability_to_pay"])
            + int(score_data["ease_of_contact"])
            + int(score_data["style_fit"])
        )

        score_reason = {
            "demand_match": score_data["demand_match"],
            "improvement_potential": score_data["improvement_potential"],
            "ability_to_pay": score_data["ability_to_pay"],
            "ease_of_contact": score_data["ease_of_contact"],
            "style_fit": score_data["style_fit"],
            "fit_reasons": score_data["fit_reasons"],
            "recommended_offer": score_data["recommended_offer"],
            "gpt_model": gpt_model,
            "score_delta": score_data.get("score_delta", 0),
        }

        payload = {
            "run_id": run_id,
            "entity_id": entity_id,
            "total_score": total_score,
            "category": "unclassified",
            "score_reason": score_reason,
            "trend_summary": score_data["summary"],
        }

        sb = get_supabase_client()
        response = sb.table("scout_scores").upsert(payload, on_conflict="run_id,entity_id").execute()
        data = response.data or []
        if not data or "id" not in data[0]:
            raise ValueError("Insert score response does not include score id.")

        return str(data[0]["id"])
    except Exception:
        logger.exception("Failed to insert score. run_id=%s, entity_id=%s", run_id, entity_id)
        raise


def get_last_score(entity_id: str) -> dict[str, Any] | None:
    """Fetch the most recent prior score for an entity."""

    try:
        sb = get_supabase_client()
        response = (
            sb.table("scout_scores")
            .select("id, total_score, created_at")
            .eq("entity_id", entity_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        rows = response.data or []
        return rows[0] if rows else None
    except Exception:
        logger.exception("Failed to fetch last score. entity_id=%s", entity_id)
        raise


def get_scores_by_run(run_id: str) -> list[dict[str, Any]]:
    """Fetch scores and joined entity data for a run."""

    try:
        sb = get_supabase_client()
        response = (
            sb.table("scout_scores")
            .select(
                "id, entity_id, total_score, category, score_reason, "
                "scout_entities!inner(channel_title)"
            )
            .eq("run_id", run_id)
            .execute()
        )
        rows = response.data or []
        results: list[dict[str, Any]] = []

        for row in rows:
            entity = row.get("scout_entities") or {}
            score_reason = row.get("score_reason") or {}
            results.append(
                {
                    "score_id": str(row["id"]),
                    "entity_id": str(row["entity_id"]),
                    "display_name": entity.get("channel_title") or "Unknown channel",
                    "total_score": float(row["total_score"]),
                    "category": row["category"],
                    "score_delta": score_reason.get("score_delta", 0),
                }
            )

        return results
    except Exception:
        logger.exception("Failed to fetch scores by run. run_id=%s", run_id)
        raise


def update_score_classification(score_id: str, classification: str) -> None:
    """Update the category (classification) for a score."""

    try:
        sb = get_supabase_client()
        sb.table("scout_scores").update({"category": classification}).eq("id", score_id).execute()
    except Exception:
        logger.exception(
            "Failed to update score classification. score_id=%s classification=%s",
            score_id,
            classification,
        )
        raise


def insert_pin(entity_id: str, note: str | None = None, pinned_by: str | None = None) -> str:
    """Insert or update a pin for an entity."""

    try:
        sb = get_supabase_client()
        payload = {"entity_id": entity_id, "note": note, "pinned_by": pinned_by}
        response = sb.table("scout_pins").upsert(payload, on_conflict="entity_id").execute()
        data = response.data or []
        if not data or "id" not in data[0]:
            raise ValueError("Insert pin response does not include pin id.")

        return str(data[0]["id"])
    except Exception:
        logger.exception("Failed to insert pin. entity_id=%s", entity_id)
        raise


def delete_pin(entity_id: str) -> None:
    """Delete a pin for an entity."""

    try:
        sb = get_supabase_client()
        sb.table("scout_pins").delete().eq("entity_id", entity_id).execute()
    except Exception:
        logger.exception("Failed to delete pin. entity_id=%s", entity_id)
        raise


def get_pins() -> list[dict[str, Any]]:
    """Fetch all pins with joined entity data."""

    try:
        sb = get_supabase_client()
        response = (
            sb.table("scout_pins")
            .select("id, entity_id, note, pinned_by, scout_entities(channel_title)")
            .execute()
        )
        rows = response.data or []
        results = []
        for row in rows:
            entity = row.get("scout_entities") or {}
            results.append(
                {
                    "pin_id": str(row["id"]),
                    "entity_id": str(row["entity_id"]),
                    "display_name": entity.get("channel_title") or "Unknown",
                    "note": row.get("note"),
                    "pinned_by": row.get("pinned_by"),
                }
            )
        return results
    except Exception:
        logger.exception("Failed to fetch pins.")
        raise


def get_last_success_run_id() -> str | None:
    """Fetch the ID of the most recent successful run."""

    try:
        sb = get_supabase_client()
        response = (
            sb.table("scout_runs")
            .select("id")
            .eq("status", "success")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return str(rows[0]["id"]) if rows else None
    except Exception:
        logger.exception("Failed to fetch last success run_id.")
        raise


def get_entities_by_classification(run_id: str, category: str, limit: int = 10) -> list[str]:
    """Fetch list of entity IDs for a specific classification in a run."""

    try:
        sb = get_supabase_client()
        response = (
            sb.table("scout_scores")
            .select("entity_id")
            .eq("run_id", run_id)
            .eq("category", category)
            .order("total_score", desc=True)
            .limit(limit)
            .execute()
        )
        rows = response.data or []
        return [str(row["entity_id"]) for row in rows]
    except Exception:
        logger.exception(
            "Failed to fetch entities by classification. run_id=%s, category=%s", run_id, category
        )
        raise


def get_pinned_entity_ids() -> list[str]:
    """Fetch all pinned entity IDs."""

    try:
        sb = get_supabase_client()
        response = sb.table("scout_pins").select("entity_id").execute()
        rows = response.data or []
        return [str(row["entity_id"]) for row in rows]
    except Exception:
        logger.exception("Failed to fetch pinned entity_ids.")
        raise
