
import pytest
from datetime import datetime, timedelta
from worker.scorer import should_analyze

class MockSettings:
    def __init__(self, min_subs=500, min_freq=30, re_analyze=14):
        self.min_subscribers = min_subs
        self.min_upload_freq_days = min_freq
        self.re_analyze_days = re_analyze

def test_should_analyze_basic():
    settings = MockSettings()
    
    # Case 1: Pass
    snapshot = {"subscribers": 1000, "upload_freq_days": 5}
    should, reason = should_analyze(snapshot, None, settings)
    assert should is True
    assert reason is None

    # Case 2: Low Subscribers
    snapshot = {"subscribers": 400, "upload_freq_days": 5}
    should, reason = should_analyze(snapshot, None, settings)
    assert should is False
    assert "Low subscribers" in reason

    # Case 3: Inactive
    snapshot = {"subscribers": 1000, "upload_freq_days": 40}
    should, reason = should_analyze(snapshot, None, settings)
    assert should is False
    assert "Inactive" in reason

def test_should_analyze_last_score():
    settings = MockSettings()
    snapshot = {"subscribers": 1000, "upload_freq_days": 5}
    
    # Case 4: Recently analyzed with Normal score
    last_score = {
        "category": "normal",
        "created_at": (datetime.now() - timedelta(days=5)).isoformat()
    }
    should, reason = should_analyze(snapshot, last_score, settings)
    assert should is False
    assert "Recently analyzed" in reason

    # Case 5: Recently analyzed with Top/Hot score (should re-analyze)
    last_score = {
        "category": "top",
        "created_at": (datetime.now() - timedelta(days=5)).isoformat()
    }
    should, reason = should_analyze(snapshot, last_score, settings)
    assert should is True

    # Case 6: Analyzed long ago
    last_score = {
        "category": "normal",
        "created_at": (datetime.now() - timedelta(days=20)).isoformat()
    }
    should, reason = should_analyze(snapshot, last_score, settings)
    assert should is True
