
import pytest
from unittest.mock import MagicMock, patch
from worker.discovery import DiscoveryWorker

@pytest.fixture
def mock_settings():
    with patch("worker.discovery.get_settings") as mock:
        settings = MagicMock()
        settings.openai_api_key = "test_key"
        settings.openai_search_model = "gpt-4o-search-preview"
        mock.return_value = settings
        yield settings

def test_discovery_worker_discover_native(mock_settings):
    with patch("worker.discovery.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        # Mock single LLM call with search results
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content=
                '{"discovered_channels": [{"name": "Search Result Creator", "handle": "@found", "justification": "found via openai search"}]}'
            ))
        ]
        
        dw = DiscoveryWorker()
        results = dw.discover(["keyword"])
        
        assert len(results) == 1
        assert results[0]["name"] == "Search Result Creator"
        assert results[0]["handle"] == "@found"
        
        # Verify call parameters (model selection)
        args, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == "gpt-4o-search-preview"
