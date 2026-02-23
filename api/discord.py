"""Discord Interactions endpoint and command routing."""

import json
import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from api.reports import get_latest_report
from api.runs import start_run
from api.status import get_status
from config import get_settings
from models.schemas import DiscordInteractionRequest, RunRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/discord", tags=["discord"])

DISCORD_PING_TYPE = 1
DISCORD_APPLICATION_COMMAND_TYPE = 2
DISCORD_RESPONSE_PONG = 1
DISCORD_RESPONSE_CHANNEL_MESSAGE = 4


async def _verify_discord_signature(
    request: Request,
    x_signature_ed25519: str | None,
    x_signature_timestamp: str | None,
) -> bytes:
    """Verify Discord request signature and return raw request body."""
    try:
        settings = get_settings()
        if not settings.discord_public_key:
            raise HTTPException(status_code=500, detail="DISCORD_PUBLIC_KEY is not configured")

        if not x_signature_ed25519 or not x_signature_timestamp:
            raise HTTPException(status_code=401, detail="Missing Discord signature headers")

        body = await request.body()
        verify_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(settings.discord_public_key))
        message = x_signature_timestamp.encode() + body
        verify_key.verify(bytes.fromhex(x_signature_ed25519), message)
        return body
    except HTTPException:
        raise
    except InvalidSignature as exc:
        logger.exception("Invalid Discord signature.")
        raise HTTPException(status_code=401, detail="Invalid request signature") from exc
    except Exception as exc:
        logger.exception("Failed to verify Discord signature.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _extract_subcommand(payload: DiscordInteractionRequest) -> tuple[str | None, dict[str, object]]:
    """Extract subcommand and options from Discord command payload."""
    if not payload.data or payload.data.name != "scout":
        return None, {}

    for option in payload.data.options:
        if option.type == 1:  # SUB_COMMAND
            values: dict[str, object] = {}
            for sub_opt in option.options:
                values[sub_opt.name] = sub_opt.value
            return option.name, values

    return None, {}


@router.post("/interactions")
async def handle_discord_interactions(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature_ed25519: str | None = Header(default=None),
    x_signature_timestamp: str | None = Header(default=None),
):
    """Receive Discord interactions and route scout commands."""
    try:
        raw_body = await _verify_discord_signature(
            request,
            x_signature_ed25519=x_signature_ed25519,
            x_signature_timestamp=x_signature_timestamp,
        )
        payload = DiscordInteractionRequest.model_validate(json.loads(raw_body))

        if payload.type == DISCORD_PING_TYPE:
            return {"type": DISCORD_RESPONSE_PONG}

        if payload.type != DISCORD_APPLICATION_COMMAND_TYPE:
            raise HTTPException(status_code=400, detail="Unsupported interaction type")

        subcommand, options = _extract_subcommand(payload)

        if subcommand == "run":
            notify = bool(options.get("notify", True))
            dry_run = bool(options.get("dry_run", False))
            scope = str(options.get("scope", "weekly"))
            run_request = RunRequest(
                run_type="manual",
                notify_discord=notify and not dry_run,
                config={"dry_run": dry_run, "scope": scope},
            )
            run_response = await start_run(request=run_request, background_tasks=background_tasks)
            return {
                "type": DISCORD_RESPONSE_CHANNEL_MESSAGE,
                "data": {
                    "content": (
                        f"✅ Scout run started. run_id={run_response.run_id} "
                        f"(notify={run_request.notify_discord}, dry_run={dry_run}, scope={scope})"
                    )
                },
            }

        if subcommand == "status":
            status = await get_status()
            return {
                "type": DISCORD_RESPONSE_CHANNEL_MESSAGE,
                "data": {
                    "content": (
                        f"📊 status={status.status} run_id={status.run_id or '-'} "
                        f"run_type={status.run_type or '-'}"
                    )
                },
            }

        if subcommand == "latest":
            latest = await get_latest_report(n=5)
            lines = [f"• {item.display_name}: score={item.total_score} category={item.category}" for item in latest.items]
            body = "\n".join(lines) if lines else "No items in latest report"
            return {
                "type": DISCORD_RESPONSE_CHANNEL_MESSAGE,
                "data": {"content": f"📰 latest run={latest.run_id}\n{body}"},
            }

        if subcommand == "health":
            return {
                "type": DISCORD_RESPONSE_CHANNEL_MESSAGE,
                "data": {"content": "🟢 SignalForge API is online."},
            }

        return {
            "type": DISCORD_RESPONSE_CHANNEL_MESSAGE,
            "data": {
                "content": "Unsupported /scout subcommand. Supported: run, status, latest, health"
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to handle Discord interaction.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
