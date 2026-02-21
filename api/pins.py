"""API endpoints for managing creator pins."""

import logging
from fastapi import APIRouter, HTTPException

from db.queries import insert_pin, delete_pin, get_pins
from models.schemas import PinRequest, PinResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/scout/pins", tags=["pins"])


@router.post("", response_model=PinResponse)
async def add_pin(request: PinRequest):
    """Pin an entity with a note."""
    try:
        pin_id = insert_pin(request.entity_id, request.note, request.pinned_by)
        return PinResponse(id=pin_id, entity_id=request.entity_id)
    except Exception as e:
        logger.exception("Failed to add pin.")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_pins():
    """List all pinned entities."""
    try:
        return get_pins()
    except Exception as e:
        logger.exception("Failed to list pins.")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entity_id}")
async def remove_pin(entity_id: str):
    """Remove a pin for an entity."""
    try:
        delete_pin(entity_id)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("Failed to remove pin.")
        raise HTTPException(status_code=500, detail=str(e))
