import sys
import os
import argparse
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from event_manager.upload_scores.uploader import main
from event_manager.upload_scores.exceptions import DatabaseConnectionError

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Upload player scores to MongoDB.")
        parser.add_argument("--dry-run", action="store_true", help="Run without writing to database")
        args = parser.parse_args()

        main(dry_run=args.dry_run)

    except DatabaseConnectionError as e:
        logging.critical(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"❌ Unexpected error: {e}")
        sys.exit(1)
