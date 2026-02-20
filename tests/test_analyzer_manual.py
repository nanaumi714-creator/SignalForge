"""Manual test for Phase 3 Analyzer."""

import os
import sys
import logging
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from worker.analyzer import Analyzer
from models.schemas import ScoreOutput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_analyzer_logic():
    print("--- Starting Analyzer Logic Test (Implementation Check) ---")

    # Mock settings and OpenAI client
    with patch("worker.analyzer.get_settings") as mock_settings, \
         patch("worker.analyzer.OpenAI") as mock_openai, \
         patch("worker.analyzer.insert_score") as mock_insert_score, \
         patch("worker.analyzer.get_last_score") as mock_get_last_score:

        # 1. Setup Mock Settings
        mock_settings.return_value.openai_api_key = "fake_key"
        mock_settings.return_value.openai_model = "gpt-4o-mini"
        mock_settings.return_value.batch_size = 5

        # 2. Setup Mock OpenAI Response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='''
            {
                "demand_match": 25,
                "improvement_potential": 15,
                "ability_to_pay": 10,
                "ease_of_contact": 10,
                "style_fit": 18,
                "summary": "非常にマッチ度の高いチャンネルです。",
                "fit_reasons": ["高い再生数", "投稿頻度が安定", "ブランドイメージに合致"],
                "recommended_offer": "スタンダードプランの提案"
            }
            '''))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        # 3. Setup Mock DB response for last score
        mock_get_last_score.return_value = {"total_score": 70}

        # 4. Initialize Analyzer
        analyzer = Analyzer()
        
        # 5. Prepare Dummy Data
        dummy_snapshots = [
            {
                "entity_id": "dummy-uuid-1",
                "display_name": "Test Creator",
                "category": "Education",
                "subscribers": 100000,
                "total_views": 5000000,
                "upload_freq_days": 3.5,
                "recent_videos_json": []
            }
        ]

        # 6. Run Analysis
        run_id = "test-run-id"
        errors = analyzer.analyze_batch(run_id, dummy_snapshots)

        # 7. Verifications
        if errors:
            print(f"FAILED: Errors occurred: {errors}")
            return

        print("SUCCESS: analyze_batch executed without errors.")

        # Check if insert_score was called
        if mock_insert_score.called:
            args, kwargs = mock_insert_score.call_args
            print(f"INFO: insert_score called with run_id={kwargs['run_id']}")
            score_data = kwargs['score_data']
            print(f"INFO: Validated Total Score: {score_data['demand_match'] + score_data['improvement_potential'] + score_data['ability_to_pay'] + score_data['ease_of_contact'] + score_data['style_fit']}")
            print(f"INFO: Score Delta: {score_data['score_delta']} (Calculated: (25+15+10+10+18) - 70 = 78 - 70 = 8)")
            
            if score_data['score_delta'] == 8:
                print("SUCCESS: Score delta calculation is correct.")
            else:
                print(f"FAILED: Score delta mismatch. Expected 8, got {score_data['score_delta']}")
        else:
            print("FAILED: insert_score was not called.")

    print("--- Test Finished ---")

if __name__ == "__main__":
    test_analyzer_logic()
