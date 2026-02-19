"""Manual test for Phase 2 Collector."""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.queries import insert_run, update_run_status
from worker.collector import YouTubeCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()

    # 1. Create a run
    try:
        run_id = insert_run("manual", {"keywords": ["vtuber", "cover song"]})
        logger.info(f"Created run: {run_id}")

        # 2. Run Collector
        collector = YouTubeCollector()
        result = collector.collect_and_save(run_id, ["vtuber cover song"])

        logger.info(f"Collection finished. Entities: {result.entity_count}, Snapshots: {result.snapshot_count}")
        if result.errors:
            logger.error(f"Errors: {result.errors}")

        # 3. Update run status
        status = "success" if result.entity_count > 0 else "failed"
        update_run_status(run_id, status, summary={
            "entities": result.entity_count,
            "snapshots": result.snapshot_count,
            "errors": len(result.errors)
        })
        logger.info(f"Run status updated to {status}")

    except Exception as e:
        logger.exception("Manual test failed")

if __name__ == "__main__":
    main()
