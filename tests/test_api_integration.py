"""Integration tests for SignalForge API."""

import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)


def test_root_health_check():
    """Test the root endpoint for application availability."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


@patch("api.runs.insert_run")
@patch("api.runs.run_scout")
def test_start_run(mock_run_scout, mock_insert_run):
    """Test starting a scout run via POST /v1/scout/runs."""
    mock_insert_run.return_value = "test-run-id"
    
    payload = {
        "run_type": "manual",
        "config": {"keywords": ["test"]},
        "notify_discord": False
    }
    response = client.post("/v1/scout/runs", json=payload)
    
    assert response.status_code == 200
    assert response.json()["run_id"] == "test-run-id"
    assert response.json()["status"] == "running"
    
    # Verify insert_run was called correctly
    mock_insert_run.assert_called_once_with("manual", {"keywords": ["test"]})


@patch("api.runs.get_supabase_client")
def test_get_run_status(mock_get_sb):
    """Test fetching run status via GET /v1/scout/runs/{id}."""
    mock_sb = MagicMock()
    mock_get_sb.return_value = mock_sb
    mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": "test-run-id",
            "status": "success",
            "summary": {"scanned": 10},
            "started_at": "2024-02-21T00:00:00",
            "finished_at": "2024-02-21T00:05:00"
        }
    ]
    
    response = client.get("/v1/scout/runs/test-run-id")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["summary"]["scanned"] == 10


@patch("api.pins.insert_pin")
def test_add_pin(mock_insert_pin):
    """Test adding a pin via POST /v1/scout/pins."""
    mock_insert_pin.return_value = "pin-uuid"
    
    payload = {"entity_id": "creator-uuid", "note": "Interesting"}
    response = client.post("/v1/scout/pins", json=payload)
    
    assert response.status_code == 200
    assert response.json()["id"] == "pin-uuid"


@patch("api.commands.start_run")
def test_handle_command_run(mock_start_run):
    """Test slash command /scout run."""
    mock_start_run.return_value = {"run_id": "cmd-run-id", "status": "running"}
    
    payload = {"text": "/scout run VTuber Anime"}
    response = client.post("/v1/scout/commands", json=payload)
    
    assert response.status_code == 200
    assert response.json()["run_id"] == "cmd-run-id"
