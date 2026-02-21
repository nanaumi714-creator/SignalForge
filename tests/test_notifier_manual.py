"""Manual test for worker/notifier.py."""

import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker.notifier import format_report, send_discord
from config import get_settings


def test_manual_notification():
    settings = get_settings()
    webhook_url = settings.discord_webhook_url

    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL":
        print("Error: DISCORD_WEBHOOK_URL not set in .env")
        return

    run_summary = {
        "timestamp_jst": "2024-02-20 22:30:00",
        "run_type": "manual",
        "scanned": 50,
        "hot_threshold": 85,
    }

    top10 = [
        {"entity_id": "e1", "display_name": "Creator A", "total_score": 95, "score_delta": 5},
        {"entity_id": "e2", "display_name": "Creator B", "total_score": 92, "score_delta": -2},
    ]

    hot10 = [
        {"entity_id": "e1", "display_name": "Creator A", "total_score": 95, "score_delta": 5},
        {"entity_id": "e3", "display_name": "Creator C", "total_score": 86, "score_delta": 10},
    ]

    watchlist = [
        {"entity_id": "e4", "display_name": "Creator D", "total_score": 75, "score_delta": 0},
    ]

    trends = {
        "7d": [{"keyword": "AI"}, {"keyword": "SaaS"}],
        "30d": [{"keyword": "Python"}, {"keyword": "NoCode"}],
    }

    report = format_report(run_summary, top10, hot10, watchlist, trends)
    print("--- Formatted Report ---")
    print(report)
    print("------------------------")

    print("\nSending to Discord...")
    send_discord(webhook_url, report)
    print("Done. Please check your Discord channel.")


if __name__ == "__main__":
    test_manual_notification()
