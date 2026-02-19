"""Pydantic schemas for SCOUT SYSTEM."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class YouTubeChannel(BaseModel):
    """Schema for YouTube channel data from API."""

    channel_id: str
    title: str
    description: str | None = None
    published_at: datetime | None = None
    subscriber_count: int | None = None
    view_count: int | None = None
    video_count: int | None = None
    country: str | None = None
    language: str | None = None


class YouTubeVideo(BaseModel):
    """Schema for YouTube video data from API."""

    video_id: str
    published_at: datetime


class CollectorResult(BaseModel):
    """Summary of collection result."""

    run_id: str
    entity_count: int
    snapshot_count: int
    errors: list[str] = Field(default_factory=list)


class EntityRecord(BaseModel):
    """Schema for scout_entities table."""

    model_config = ConfigDict(from_attributes=True)

    id: Any | None = None
    platform: str
    platform_id: str
    channel_title: str | None = None
    channel_description: str | None = None
    country: str | None = None
    language: str | None = None
    published_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SnapshotRecord(BaseModel):
    """Schema for scout_snapshots table."""

    model_config = ConfigDict(from_attributes=True)

    id: Any | None = None
    run_id: str
    entity_id: str
    subscriber_count: int | None = None
    view_count: int | None = None
    video_count: int | None = None
    collected_at: datetime | None = None
    created_at: datetime | None = None
