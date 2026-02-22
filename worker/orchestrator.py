"""Orchestrator worker to manage the Scout System flow."""

import logging
from datetime import datetime
from typing import Any

from config import get_settings
from db.queries import (
    get_snapshots_by_run,
    get_scores_by_run,
    update_run_status,
    get_last_success_run_id,
    get_entities_by_classification,
    get_pinned_entity_ids,
    update_score_classification,
)
from worker.collector import YouTubeCollector
from worker.analyzer import Analyzer
from worker.scorer import classify_scores
from worker.notifier import format_report, send_discord
from db.client import get_supabase_client

logger = logging.getLogger(__name__)


def get_tracked_platform_ids() -> list[str]:
    """
    Select 30 entities based on past performance and manual pins.
    Tracked 30: Top10 + Hot8 + Watch7 + Pin5
    """
    prev_run_id = get_last_success_run_id()
    tracked_entities = set()

    if prev_run_id:
        # 1. Top 10
        tracked_entities.update(get_entities_by_classification(prev_run_id, "top", 10))
        # 2. Hot 8
        tracked_entities.update(get_entities_by_classification(prev_run_id, "hot", 8))
        # 3. Watch 7
        tracked_entities.update(get_entities_by_classification(prev_run_id, "watch", 7))

    # 4. Manual Pin 5 (Take first 5)
    pins = get_pinned_entity_ids()
    tracked_entities.update(pins[:5])

    # Convert Entity UUIDs to Platform IDs (YouTube Channel IDs)
    sb = get_supabase_client()
    if not tracked_entities:
        return []

    response = (
        sb.table("scout_entities")
        .select("platform_id")
        .in_("id", list(tracked_entities))
        .execute()
    )
    return [row["platform_id"] for row in response.data or []]


def run_scout(run_id: str, config: dict[str, Any], notify_discord: bool = True) -> None:
    """
    Execute the full Scout System pipeline:
    Collector -> Analyzer -> Scorer -> Notifier
    """
    settings = get_settings()
    summary = {
        "start_time": datetime.now().isoformat(),
        "scanned": 0,
        "errors": []
    }

    try:
        # 1. Discovery (Phase 10: Web Search)
        discovery_ids = []
        if settings.discovery_enabled:
            logger.info("Starting web discovery for run_id=%s", run_id)
            from worker.discovery import DiscoveryWorker
            dw = DiscoveryWorker()
            keywords = config.get("keywords", ["VTuber", "Cover", "Singer"])
            discovered = dw.discover(keywords)
            
            if discovered:
                collector = YouTubeCollector()
                discovery_ids = collector.resolve_discovered_channels(discovered)
                logger.info("Discovered %d new potential channels via web search.", len(discovery_ids))

        # 2. Collection (Hybrid 60)
        logger.info("Starting hybrid collection for run_id=%s", run_id)
        collector = YouTubeCollector()
        
        tracked_pids = get_tracked_platform_ids()
        # Merge discovered IDs into collection
        all_ids_to_collect = list(set(tracked_pids) | set(discovery_ids))
        
        keywords = config.get("keywords", ["VTuber", "Cover", "Singer"])
        
        col_result = collector.collect_multiple_sources(run_id, keywords, all_ids_to_collect)
        
        summary["scanned"] = col_result.entity_count
        if col_result.errors:
            summary["errors"].extend(col_result.errors)

        # 2. GPT Analysis
        logger.info("Starting analyzer for run_id=%s (mode=%s)", run_id, settings.analysis_mode)
        analyzer = Analyzer()
        all_snapshots = get_snapshots_by_run(run_id)
        
        # Filtering logic (Smart Mode / Aggregated Mode)
        to_analyze = []
        skipped_count = 0
        
        for snap in all_snapshots:
            entity_id = snap["entity_id"]
            last_score = get_last_score(entity_id)
            
            should_ana, reason = True, None
            if settings.analysis_mode in ["smart", "aggregated"]:
                from worker.scorer import should_analyze
                should_ana, reason = should_analyze(snap, last_score, settings)
                
            if should_ana:
                to_analyze.append(snap)
            else:
                logger.info("Skipping analysis for entity_id=%s: %s", entity_id, reason)
                skipped_count += 1

        logger.info("Analysis candidates: %d/%d (Skipped: %d)", len(to_analyze), len(all_snapshots), skipped_count)

        if settings.analysis_mode == "aggregated":
            agg_result = analyzer.analyze_aggregated(run_id, to_analyze)
            summary["aggregated_analysis"] = agg_result
            # In aggregated mode, we might not have individual scores for everyone,
            # but we can still extract trends from those analyzed or the list.
        else:
            ana_errors = analyzer.analyze_batch(run_id, to_analyze)
            if ana_errors:
                summary["errors"].extend(ana_errors)

        # 3. Classification
        logger.info("Starting scoring and classification for run_id=%s", run_id)
        scores = get_scores_by_run(run_id)
        if not scores and settings.analysis_mode == "aggregated":
            # For aggregated mode, classification might need a different approach or skip
            classification_result = {"top": [], "hot": [], "watch": [], "normal": []}
        else:
            classification_result = classify_scores(scores)
            
            # Save classifications to DB
            for category, items in classification_result.items():
                for item in items:
                    update_score_classification(item["score_id"], category)

        # 4. Trend Extraction
        logger.info("Starting trend extraction for run_id=%s", run_id)
        trend_result = analyzer.extract_trends(run_id)
        summary["trends"] = trend_result
        summary["skipped_analysis"] = skipped_count

        # 5. Notification
        if notify_discord:
            logger.info("Preparing Discord notification for run_id=%s", run_id)
            run_summary_for_notif = {
                "timestamp_jst": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "run_type": config.get("run_type", "manual"),
                "scanned": col_result.entity_count,
                "hot_threshold": settings.hot_threshold,
            }
            
            report = format_report(
                run_summary_for_notif,
                classification_result["top"],
                classification_result["hot"],
                classification_result["watch"],
                trend_result
            )
            send_discord(settings.discord_webhook_url, report)

        # 6. Finalize
        summary["end_time"] = datetime.now().isoformat()
        update_run_status(run_id, "success", summary)
        logger.info("Scout run completed successfully for run_id=%s", run_id)

    except Exception as e:
        logger.exception("Scout run failed for run_id=%s", run_id)
        summary["end_time"] = datetime.now().isoformat()
        summary["fatal_error"] = str(e)
        update_run_status(run_id, "failed", summary)
