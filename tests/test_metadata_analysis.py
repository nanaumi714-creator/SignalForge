
import pytest
from unittest.mock import MagicMock, patch
from worker.collector import YouTubeCollector
from models.schemas import YouTubeVideo

@pytest.fixture
def mock_youtube_client():
    with patch("worker.collector.build") as mock:
        yield mock.return_value

def test_get_recent_videos_detection(mock_youtube_client):
    # Mock activities.list
    mock_youtube_client.activities().list().execute.return_value = {
        "items": [
            {"contentDetails": {"upload": {"videoId": "v1"}}},
            {"contentDetails": {"upload": {"videoId": "v2"}}},
            {"contentDetails": {"upload": {"videoId": "v3"}}},
        ]
    }
    
    # Mock videos.list for details
    mock_youtube_client.videos().list().execute.return_value = {
        "items": [
            # Live Video
            {
                "id": "v1",
                "snippet": {"publishedAt": "2024-01-01T00:00:00Z"},
                "contentDetails": {"duration": "PT1H"},
                "liveStreamingDetails": {"actualStartTime": "..."}
            },
            # Shorts Video (< 60s)
            {
                "id": "v2",
                "snippet": {"publishedAt": "2024-01-01T00:00:00Z"},
                "contentDetails": {"duration": "PT45S"}
            },
            # Normal Video
            {
                "id": "v3",
                "snippet": {"publishedAt": "2024-01-01T00:00:00Z"},
                "contentDetails": {"duration": "PT10M"}
            }
        ]
    }
    
    with patch("worker.collector.get_settings") as mock_set:
        mock_set.return_value.youtube_api_key = "test"
        collector = YouTubeCollector()
        videos = collector.get_recent_videos("channel_id", max_results=3)
        
        assert len(videos) == 3
        # Check types
        assert videos[0].video_type == "live"
        assert videos[1].video_type == "shorts"
        assert videos[2].video_type == "normal"
