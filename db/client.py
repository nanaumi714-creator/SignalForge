"""Supabase client singleton provider."""

from __future__ import annotations

import logging
from typing import Any

from config import get_settings

logger = logging.getLogger(__name__)

_client: Any | None = None


def get_supabase_client() -> Any:
    """Return singleton Supabase client."""

    global _client

    if _client is not None:
        return _client

    try:
        from supabase import create_client

        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_key)
        return _client
    except Exception:
        logger.exception("Failed to initialize Supabase client.")
        raise
