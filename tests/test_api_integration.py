"""Integration tests for SignalForge API with authentication."""

import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from api.deps import verify_api_key

client = TestClient(app)
TEST_API_KEY = "test-secret-key"

@pytest.fixture(autouse=True)
def mock_settings():
    with patch("api.deps.get_settings") as mock:
        mock.return_value.scout_api_key = TEST_API_KEY
        yield mock

def test_root_health_check():
    """Test the root endpoint for application availability (No Auth required)."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

@patch("api.runs.insert_run")
@patch("api.runs.run_scout")
def test_start_run(mock_run_scout, mock_insert_run):
    """Test starting a scout run with valid API key."""
    mock_insert_run.return_value = "test-run-id"
    
    payload = {
        "run_type": "manual",
        "config": {"keywords": ["test"]},
        "notify_discord": False
    }
    response = client.post(
        "/v1/scout/runs", 
        json=payload, 
        headers={"X-API-KEY": TEST_API_KEY}
    )
    
    assert response.status_code == 200
    assert response.json()["run_id"] == "test-run-id"
    assert response.json()["status"] == "running"

@patch("api.runs.get_supabase_client")
def test_get_run_status(mock_get_sb):
    """Test fetching run status with valid API key."""
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
    
    response = client.get(
        "/v1/scout/runs/test-run-id", 
        headers={"X-API-KEY": TEST_API_KEY}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@patch("api.pins.insert_pin")
def test_add_pin(mock_insert_pin):
    """Test adding a pin with valid API key."""
    mock_insert_pin.return_value = "pin-uuid"
    
    payload = {"entity_id": "creator-uuid", "note": "Interesting"}
    response = client.post(
        "/v1/scout/pins", 
        json=payload, 
        headers={"X-API-KEY": TEST_API_KEY}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == "pin-uuid"

@patch("api.commands.start_run")
def test_handle_command_run(mock_start_run):
    """Test slash command /scout run with valid API key."""
    mock_start_run.return_value = {"run_id": "cmd-run-id", "status": "running"}
    
    payload = {"text": "/scout run VTuber Anime"}
    response = client.post(
        "/v1/scout/commands", 
        json=payload, 
        headers={"X-API-KEY": TEST_API_KEY}
    )
    
    assert response.status_code == 200

def test_api_unauthorized():
    """Test that requests without or with invalid API key are rejected."""
    # No header
    response = client.get("/v1/scout/runs/some-id")
    assert response.status_code == 422 # FastAPI returns 422 if required header is missing
    
    # Invalid key
    response = client.get("/v1/scout/runs/some-id", headers={"X-API-KEY": "wrong-key"})
    assert response.status_code == 403
