"""Authentication dependencies for SCOUT SYSTEM."""

from fastapi import Header, HTTPException, status
from config import get_settings

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify the X-API-KEY header against the configured secret."""
    settings = get_settings()
    if x_api_key != settings.scout_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key"
        )
    return x_api_key
