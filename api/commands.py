"""API endpoint for slash-command style interactions."""

import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException

from models.schemas import CommandRequest, RunRequest
from api.runs import start_run

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/scout/commands", tags=["commands"])


@router.post("")
async def handle_command(request: CommandRequest, background_tasks: BackgroundTasks):
    """
    Handle slash-style commands.
    Supported: 
    - /scout run [keywords...]
    """
    text = request.text.strip()
    if not text.startswith("/scout"):
        raise HTTPException(status_code=400, detail="Invalid command prefix. Use /scout")

    parts = text.split()
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Incomplete command")

    cmd = parts[1]
    
    if cmd == "run":
        # Keywords are parts[2:]
        keywords = parts[2:] if len(parts) > 2 else ["VTuber", "Cover", "Singer"]
        run_req = RunRequest(
            run_type="manual",
            config={"keywords": keywords},
            notify_discord=True
        )
        # Reuse start_run logic
        return await start_run(run_req, background_tasks)
    
    # Placeholder for trends and analyze commands
    elif cmd == "trends":
        return {"message": "Trends command is not yet fully implemented in this phase's API."}
    
    elif cmd == "analyze":
        return {"message": "Analyze command is not yet fully implemented in this phase's API."}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown command: {cmd}")
