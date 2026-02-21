"""Scoring and classification logic for SCOUT SYSTEM."""

from typing import Any


def classify_scores(scores: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Classify scores into top, hot, watch, and normal categories.

    Rules:
    - top: top 10 by total_score
    - hot: total_score >= 85 and score_delta >= 5 (can overlap with top)
    - watch: total_score >= 60 and (not top and not hot)
    - normal: total_score < 60
    """

    # Sort by total_score descending
    sorted_scores = sorted(scores, key=lambda x: x["total_score"], reverse=True)

    top_list = sorted_scores[:10]
    top_ids = {s["entity_id"] for s in top_list}

    hot_list = [
        s for s in scores if s["total_score"] >= 85 and s.get("score_delta", 0) >= 5
    ]
    hot_ids = {s["entity_id"] for s in hot_list}

    # Watchlist: total_score >= 60 but NOT in top and NOT in hot
    watch_list = [
        s
        for s in scores
        if s["total_score"] >= 60
        and s["entity_id"] not in top_ids
        and s["entity_id"] not in hot_ids
    ]

    # Normal: the rest (not top, not hot, not watch)
    all_assigned_ids = top_ids | hot_ids | {s["entity_id"] for s in watch_list}
    normal_list = [s for s in scores if s["entity_id"] not in all_assigned_ids]

    return {
        "top": top_list,
        "hot": hot_list,
        "watch": watch_list,
        "normal": normal_list,
    }
