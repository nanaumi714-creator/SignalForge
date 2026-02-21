"""Manual test for worker/scorer.py."""

import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker.scorer import classify_scores


def test_scorer_manual():
    print("Running manual verification for classify_scores...")
    
    scores = [
        {"entity_id": f"id_{i}", "total_score": 100 - i, "score_delta": 0, "display_name": f"Name{i}"}
        for i in range(15)
    ]
    # top: id_0 to id_9
    # hot: empty (delta=0)
    # watch: id_10 to id_15 (scores 90 to 85)
    # wait, id_10 has score 90. watch is >= 60. 

    # Let's add specific cases
    scores.extend([
        {"entity_id": "hot_item", "total_score": 86, "score_delta": 10, "display_name": "HotItem"},
        {"entity_id": "watch_item", "total_score": 70, "score_delta": 0, "display_name": "WatchItem"},
        {"entity_id": "normal_item", "total_score": 40, "score_delta": 0, "display_name": "NormalItem"},
    ])

    result = classify_scores(scores)
    
    top_ids = {s["entity_id"] for s in result["top"]}
    hot_ids = {s["entity_id"] for s in result["hot"]}
    watch_ids = {s["entity_id"] for s in result["watch"]}
    normal_ids = {s["entity_id"] for s in result["normal"]}

    print(f"Top IDs: {top_ids}")
    print(f"Hot IDs: {hot_ids}")
    print(f"Watch IDs: {watch_ids}")
    print(f"Normal IDs: {normal_ids}")

    # Verification
    try:
        assert len(result["top"]) == 10
        assert "hot_item" in hot_ids
        assert "watch_item" in watch_ids
        assert "normal_item" in normal_ids
        # Ensure priority: if top, not watch
        assert "id_0" in top_ids
        assert "id_0" not in watch_ids
    except AssertionError as e:
        print(f"Assertion failed!")
        raise e

    print("Success: Classification logic verified.")


if __name__ == "__main__":
    try:
        test_scorer_manual()
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)
