"""Tests for Discord interactions endpoint routing."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _payload(subcommand: str, options: list[dict] | None = None) -> dict:
    return {
        "id": "123",
        "type": 2,
        "token": "abc",
        "data": {
            "name": "scout",
            "options": [
                {
                    "name": subcommand,
                    "type": 1,
                    "options": options or [],
                }
            ],
        },
    }


@patch("api.discord._verify_discord_signature")
def test_ping(mock_verify):
    """Discord ping returns pong."""
    mock_verify.return_value = b'{"id":"1","type":1,"token":"abc"}'
    response = client.post("/discord/interactions")
    assert response.status_code == 200
    assert response.json() == {"type": 1}


@patch("api.discord.start_run")
@patch("api.discord._verify_discord_signature")
def test_scout_run(mock_verify, mock_start_run):
    """/scout run routes to start_run."""
    mock_verify.return_value = str.encode(
        '{"id":"123","type":2,"token":"abc","data":{"name":"scout","options":[{"name":"run","type":1,"options":[{"name":"notify","type":5,"value":true}]}]}}'
    )
    mock_start_run.return_value = type("RunResp", (), {"run_id": "run-1"})()

    response = client.post("/discord/interactions")

    assert response.status_code == 200
    assert "run-1" in response.json()["data"]["content"]


@patch("api.discord.get_status")
@patch("api.discord._verify_discord_signature")
def test_scout_status(mock_verify, mock_status):
    """/scout status returns latest status text."""
    mock_verify.return_value = str.encode(str(_payload("status")).replace("'", '"'))
    mock_status.return_value = type(
        "StatusResp", (), {"status": "success", "run_id": "r-1", "run_type": "manual"}
    )()

    response = client.post("/discord/interactions")

    assert response.status_code == 200
    assert "status=success" in response.json()["data"]["content"]
