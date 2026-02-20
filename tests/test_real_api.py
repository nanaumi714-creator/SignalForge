"""Real API test for Phase 3 Analyzer."""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from worker.analyzer import Analyzer
from models.schemas import ScoreInput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_api():
    print("--- Starting Real OpenAI API Test ---")
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set in .env")
        return

    try:
        analyzer = Analyzer()
        
        # Test input
        test_input = ScoreInput(
            entity_id="test-uuid",
            display_name="MrBeast",
            category="Entertainment",
            subscribers=300000000,
            total_views=50000000000,
            upload_freq_days=7.0,
            recent_videos_json=[
                {"title": "I Built A House Out Of LEGO", "views": 100000000},
                {"title": "Extreme Hide And Seek", "views": 150000000}
            ]
        )

        prompt = analyzer.build_prompt(test_input)
        print("INFO: Calling OpenAI API (gpt-5-nano)...")
        
        score_output = analyzer.call_gpt(prompt)
        
        print("\n--- API Response Validated ---")
        print(f"Total Score: {score_output.total_score}")
        print(f"Summary: {score_output.summary}")
        print(f"Fit Reasons: {', '.join(score_output.fit_reasons)}")
        print(f"Recommended Offer: {score_output.recommended_offer}")
        print("--- Test SUCCESS ---")

    except Exception as e:
        print(f"\n--- Test FAILED ---")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_real_api()
