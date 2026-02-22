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
    video_type: str = "normal"  # normal, live, shorts


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


class ScoreInput(BaseModel):
    """Input payload used for GPT scoring prompt."""

    entity_id: str
    display_name: str
    category: str | None = None
    subscribers: int | None = None
    total_views: int | None = None
    upload_freq_days: float | None = None
    recent_videos_json: list[dict[str, Any]] = Field(default_factory=list)


class ScoreOutput(BaseModel):
    """Validated GPT scoring output."""

    demand_match: int = Field(ge=0, le=30)
    improvement_potential: int = Field(ge=0, le=20)
    ability_to_pay: int = Field(ge=0, le=15)
    ease_of_contact: int = Field(ge=0, le=15)
    style_fit: int = Field(ge=0, le=20)
    summary: str = Field(min_length=1, max_length=200)
    fit_reasons: list[str] = Field(min_length=1)
    recommended_offer: str = Field(min_length=1)

    @property
    def total_score(self) -> int:
        """Return summed total score."""

        return (
            self.demand_match
            + self.improvement_potential
            + self.ability_to_pay
            + self.ease_of_contact
            + self.style_fit
        )


class RunRequest(BaseModel):
    """Request payload to start a new scout run."""

    run_type: str = Field("manual", pattern="^(manual|scheduled)$")
    config: dict[str, Any] = Field(default_factory=dict)
    notify_discord: bool = True


class RunResponse(BaseModel):
    """Response identifying a newly created run."""

    run_id: str
    status: str


class RunStatusResponse(BaseModel):
    """Response for checking run status and summary."""

    run_id: str
    status: str
    summary: dict[str, Any] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class PinRequest(BaseModel):
    """Request payload to pin an entity."""

    entity_id: str
    note: str | None = None
    pinned_by: str | None = None


class PinResponse(BaseModel):
    """Response for pinning operation."""

    id: str
    entity_id: str


class CommandRequest(BaseModel):
    """Slash command request payload."""

    text: str
