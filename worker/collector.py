"""Collector worker for Scout System."""

import logging
from datetime import datetime, timedelta
from typing import Any

from googleapiclient.discovery import build

from config import get_settings
from db.queries import upsert_entity, insert_snapshot
from models.schemas import YouTubeChannel, YouTubeVideo, CollectorResult

logger = logging.getLogger(__name__)


class YouTubeCollector:
    """Collector for YouTube Data API."""

    def __init__(self):
        settings = get_settings()
        self.youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)

    def search_channels(self, keyword: str, max_results: int = 12) -> list[str]:
        """Search channels by keyword and return list of channel IDs."""
        try:
            request = self.youtube.search().list(
                q=keyword,
                type="channel",
                part="id",
                maxResults=max_results
            )
            response = request.execute()
            channel_ids = [item["id"]["channelId"] for item in response.get("items", [])]
            return channel_ids
        except Exception:
            logger.exception("Failed to search channels for keyword: %s", keyword)
            return []

    def get_channel_details(self, channel_ids: list[str]) -> list[YouTubeChannel]:
        """Get detailed information for a list of channel IDs."""
        if not channel_ids:
            return []

        try:
            # YouTube API allows up to 50 IDs per request
            results = []
            for i in range(0, len(channel_ids), 50):
                chunk = channel_ids[i:i+50]
                request = self.youtube.channels().list(
                    id=",".join(chunk),
                    part="snippet,statistics"
                )
                response = request.execute()

                for item in response.get("items", []):
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})

                    results.append(YouTubeChannel(
                        channel_id=item["id"],
                        title=snippet.get("title", ""),
                        description=snippet.get("description"),
                        published_at=snippet.get("publishedAt"),
                        subscriber_count=int(stats.get("subscriberCount", 0)),
                        view_count=int(stats.get("viewCount", 0)),
                        video_count=int(stats.get("videoCount", 0)),
                        country=snippet.get("country"),
                    ))
            return results
        except Exception:
            logger.exception("Failed to get channel details.")
            return []

    def get_recent_videos(self, channel_id: str, max_results: int = 10) -> list[YouTubeVideo]:
        """Get recent videos for a channel to calculate frequency."""
        try:
            request = self.youtube.search().list(
                channelId=channel_id,
                part="snippet",
                order="date",
                type="video",
                maxResults=max_results
            )
            response = request.execute()

            videos = []
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                videos.append(YouTubeVideo(
                    video_id=item["id"]["videoId"],
                    published_at=snippet.get("publishedAt")
                ))
            return videos
        except Exception:
            logger.exception("Failed to get recent videos for channel: %s", channel_id)
            return []

    def calculate_upload_frequency(self, videos: list[YouTubeVideo]) -> float:
        """Calculate average uploads per week based on recent videos."""
        if len(videos) < 2:
            return 0.0

        # Sort by date
        sorted_videos = sorted(videos, key=lambda x: x.published_at)
        first_date = sorted_videos[0].published_at
        last_date = sorted_videos[-1].published_at

        days_diff = (last_date - first_date).days
        if days_diff == 0:
            return 0.0

        # Uploads per day * 7
        freq = (len(videos) / days_diff) * 7
        return round(freq, 2)

    def collect_and_save(self, run_id: str, keywords: list[str]) -> CollectorResult:
        """Main entry point for collection and saving to DB."""
        entity_count = 0
        snapshot_count = 0
        errors = []

        all_channel_ids = set()
        for kw in keywords:
            ids = self.search_channels(kw)
            all_channel_ids.update(ids)

        channels = self.get_channel_details(list(all_channel_ids))

        for channel in channels:
            try:
                # 1. Upsert Entity
                entity_uuid = upsert_entity(
                    platform="youtube",
                    platform_id=channel.channel_id,
                    channel_title=channel.title,
                    channel_description=channel.description,
                    country=channel.country,
                    published_at=channel.published_at.isoformat() if channel.published_at else None
                )
                entity_count += 1

                # 2. Insert Snapshot
                insert_snapshot(
                    run_id=run_id,
                    entity_id=entity_uuid,
                    subscriber_count=channel.subscriber_count,
                    view_count=channel.view_count,
                    video_count=channel.video_count
                )
                snapshot_count += 1

                # NOTE: Upload frequency calculation (videos.list) will consume more quota.
                # In Phase 2, we might skip it or limit it to avoid quota exhaustion.
                # For now, it's not saved in snapshots table (schema doesn't have it).

            except Exception as e:
                errors.append(f"Failed to process channel {channel.channel_id}: {str(e)}")

        return CollectorResult(
            run_id=run_id,
            entity_count=entity_count,
            snapshot_count=snapshot_count,
            errors=errors
        )
