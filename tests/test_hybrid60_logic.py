"""Unit tests for Hybrid 60 selection logic."""

import pytest
from unittest.mock import patch, MagicMock
from worker.orchestrator import get_tracked_platform_ids

@patch("worker.orchestrator.get_last_success_run_id")
@patch("worker.orchestrator.get_entities_by_classification")
@patch("worker.orchestrator.get_pinned_entity_ids")
@patch("worker.orchestrator.get_supabase_client")
def test_get_tracked_platform_ids(mock_get_sb, mock_get_pins, mock_get_class, mock_get_run):
    """Test that selection logic picks correct counts for each category."""
    
    # Setup mocks
    mock_get_run.return_value = "prev-run-id"
    
    # 10 Top, 8 Hot, 7 Watch
    mock_get_class.side_effect = [
        ["top-1", "top-2", "top-3", "top-4", "top-5", "top-6", "top-7", "top-8", "top-9", "top-10"],
        ["hot-1", "hot-2", "hot-3", "hot-4", "hot-5", "hot-6", "hot-7", "hot-8"],
        ["watch-1", "watch-2", "watch-3", "watch-4", "watch-5", "watch-6", "watch-7"]
    ]
    
    # 5 Pins
    mock_get_pins.return_value = ["pin-1", "pin-2", "pin-3", "pin-4", "pin-5", "pin-extra"]
    
    # Mock SB response for entity -> platform mapping
    mock_sb = MagicMock()
    mock_get_sb.return_value = mock_sb
    
    # Total entities: 10 + 8 + 7 + 5 = 30
    mock_data = [{"platform_id": f"pid-{i}"} for i in range(30)]
    mock_sb.table.return_value.select.return_value.in_.return_value.execute.return_value.data = mock_data
    
    platform_ids = get_tracked_platform_ids()
    
    assert len(platform_ids) == 30
    assert "pid-0" in platform_ids
    assert "pid-29" in platform_ids
    
    # Verify mock calls
    assert mock_get_class.call_count == 3
    mock_get_class.assert_any_call("prev-run-id", "top", 10)
    mock_get_class.assert_any_call("prev-run-id", "hot", 8)
    mock_get_class.assert_any_call("prev-run-id", "watch", 7)
    mock_get_pins.assert_called_once()
