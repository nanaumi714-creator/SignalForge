"""Unit tests for worker/scorer.py."""

import pytest
from worker.scorer import classify_scores


def test_classify_scores_basic():
    scores = [
        {"entity_id": f"id_{i}", "total_score": 100 - i, "score_delta": 10}
        for i in range(15)
    ]
    # ids: id_0 (100), id_1 (99), ..., id_14 (86)
    # All have delta 10, so all >= 85 are also hot.

    result = classify_scores(scores)

    assert len(result["top"]) == 10
    assert result["top"][0]["entity_id"] == "id_0"
    assert result["top"][9]["entity_id"] == "id_9"

    # id_0 to id_14 are all >= 85 and delta >= 5, so all are hot
    assert len(result["hot"]) == 15
    assert result["hot"][0]["total_score"] == 100

    # watch should be empty because all are in top or hot
    assert len(result["watch"]) == 0
    assert len(result["normal"]) == 0


def test_classify_scores_mixed():
    # To test watch and normal, we need more than 10 items in top
    scores = [
        {"entity_id": f"top_{i}", "total_score": 100 - i, "score_delta": 0}
        for i in range(11)
    ]
    # top: top_0 to top_9 (10 items)
    # top_10 (score 90) will be watch/hot depending on delta. 
    # Let's adjust top_10 to be watch
    scores[10]["entity_id"] = "watch_item"
    scores[10]["total_score"] = 70
    
    # Add a hot item that is NOT in top 10
    scores.append({"entity_id": "hot_item", "total_score": 85, "score_delta": 10})
    
    # Add a normal item
    scores.append({"entity_id": "normal_item", "total_score": 30, "score_delta": 0})

    result = classify_scores(scores)

    assert len(result["top"]) == 10
    assert "top_0" in [s["entity_id"] for s in result["top"]]
    
    hot_ids = {s["entity_id"] for s in result["hot"]}
    assert "hot_item" in hot_ids
    
    watch_ids = {s["entity_id"] for s in result["watch"]}
    assert "watch_item" in watch_ids
    
    normal_ids = {s["entity_id"] for s in result["normal"]}
    assert "normal_item" in normal_ids


def test_classify_scores_empty():
    result = classify_scores([])
    assert result["top"] == []
    assert result["hot"] == []
    assert result["watch"] == []
    assert result["normal"] == []
