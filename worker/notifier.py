"""Discord notification logic for SCOUT SYSTEM."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

MAX_DISCORD_LEN = 2000


def format_report(
    run_summary: dict[str, Any],
    top10: list[dict[str, Any]],
    hot10: list[dict[str, Any]],
    watchlist: list[dict[str, Any]],
    trends: dict[str, Any],
) -> str:
    """Format the scout report for Discord."""
    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🔍 SCOUT REPORT | {run_summary.get('timestamp_jst', 'N/A')}")
    lines.append(
        f"Type: {run_summary.get('run_type', 'N/A')} | "
        f"Scanned: {run_summary.get('scanned', 0)} | "
        f"Hot Threshold: {run_summary.get('hot_threshold', 85)}"
    )
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    lines.append("🏆 TOP 10")
    if not top10:
        lines.append("(None)")
    for i, item in enumerate(top10, 1):
        lines.append(
            f"{i}. @{item['display_name']}  ⭐{item['total_score']}  ({item['score_delta']:+d})"
        )

    lines.append("\n🔥 HOT 10  (85+・急上昇)")
    if not hot10:
        lines.append("(None)")
    top_ids = {t["entity_id"] for t in top10}
    for i, item in enumerate(hot10[:10], 1): # Limit to 10 as per spec
        if item["entity_id"] in top_ids:
            lines.append(f"{i}. @{item['display_name']}  ↑ Top参照")
        else:
            lines.append(
                f"{i}. @{item['display_name']}  ⭐{item['total_score']}  ({item['score_delta']:+d})"
            )

    lines.append("\n👀 WATCHLIST")
    if not watchlist:
        lines.append("(None)")
    for i, item in enumerate(watchlist, 1):
        lines.append(
            f"{i}. @{item['display_name']}  ⭐{item['total_score']}  ({item['score_delta']:+d})"
        )

    lines.append("\n📈 TREND KEYWORDS")
    trends_7d = ", ".join(t.get("keyword", "") for t in trends.get("7d", [])) or "None"
    trends_30d = ", ".join(t.get("keyword", "") for t in trends.get("30d", [])) or "None"
    lines.append(f"7d burst : {trends_7d}")
    lines.append(f"30d growth: {trends_30d}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def split_report(text: str) -> list[str]:
    """Split report into chunks of max 2000 characters."""
    if len(text) <= MAX_DISCORD_LEN:
        return [text]

    chunks = []
    buffer = ""
    # Split by double newline to preserve section boundaries if possible
    sections = text.split("\n\n")
    for section in sections:
        candidate = section if not buffer else f"{buffer}\n\n{section}"
        if len(candidate) <= MAX_DISCORD_LEN:
            buffer = candidate
        else:
            if buffer:
                chunks.append(buffer)
                buffer = section
            else:
                # If a single section is too long, split it by line
                lines = section.split("\n")
                for line in lines:
                    if len(buffer) + len(line) + 1 <= MAX_DISCORD_LEN:
                        buffer = f"{buffer}\n{line}" if buffer else line
                    else:
                        if buffer:
                            chunks.append(buffer)
                        buffer = line
    if buffer:
        chunks.append(buffer)
    return chunks


def send_discord(webhook_url: str, message: str) -> None:
    """Send a message to Discord via Webhook."""
    if not webhook_url:
        logger.info("Discord Webhook URL not configured. Skipping notification.")
        return

    chunks = split_report(message)
    try:
        with httpx.Client(timeout=10.0) as client:
            for chunk in chunks:
                resp = client.post(webhook_url, json={"content": chunk})
                resp.raise_for_status()
    except Exception:
        logger.exception("Failed to send Discord notification.")
        # We don't raise here to avoid stopping the entire run if notification fails
