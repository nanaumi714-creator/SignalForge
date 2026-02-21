"""Unit tests for trend extraction logic."""

import pytest
from unittest.mock import patch, MagicMock
from worker.analyzer import Analyzer

@patch("worker.analyzer.get_scores_by_run")
@patch("worker.analyzer.OpenAI")
def test_extract_trends(mock_openai_class, mock_get_scores):
    """Test that extract_trends calls GPT and parses keywords correctly."""
    
    # Setup OpenAI mock
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    # Mock scores
    mock_get_scores.return_value = [
        {"display_name": "C1", "total_score": 90, "score_delta": 5},
        {"display_name": "C2", "total_score": 85, "score_delta": 10}
    ]
    
    # Mock GPT response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "VTuber, ASMR, Music"
    mock_client.chat.completions.create.return_value = mock_response
    
    analyzer = Analyzer()
    result = analyzer.extract_trends("test-run-id")
    
    assert "keywords" in result
    assert "VTuber" in result["keywords"]
    assert len(result["keywords"]) == 3
    assert result["7d_trends"] == ["VTuber", "ASMR"]
    
    # Verify GPT was called
    mock_client.chat.completions.create.assert_called_once()
