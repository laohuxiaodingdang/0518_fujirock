import asyncio
import logging
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def debug_queries():
    """
    A special script to debug why the database queries are not returning the expected artists.
    This will not modify any data.
    """
    db_client = artist_db_service.db.supabase
    logging.info("--- Starting Query Debug ---")

    # Query 1: The exact query from populate_descriptions_from_spotify.py
    logging.info("\n[TEST 1] Running the failing query from the population script...")
    try:
        # We add count='exact' to get the total number of rows without fetching them all
        response1 = db_client.table("artists").select("id, name", count="exact").not_.is_("spotify_id", "null").or_(f"description.is.null,description.eq.''").execute()
        logging.info(f"  - RESULT: Query 1 found {response1.count} artists.")
        if response1.data:
            logging.info(f"  - First artist found: {response1.data[0]['name']}")
        else:
            logging.info("  - No data returned by Query 1.")
    except Exception as e:
        logging.error(f"  - ERROR: Query 1 failed with an exception: {e}")

    # Query 2: Simplified version, only checking the description field
    logging.info("\n[TEST 2] Running a simplified query (only checking description)...")
    try:
        response2 = db_client.table("artists").select("id, name, description", count="exact").or_(f"description.is.null,description.eq.''").execute()
        logging.info(f"  - RESULT: Query 2 found {response2.count} artists.")
        if response2.data:
            logging.info(f"  - First artist found: {response2.data[0]['name']}")
        else:
            logging.info("  - No data returned by Query 2.")
    except Exception as e:
        logging.error(f"  - ERROR: Query 2 failed with an exception: {e}")

    # Query 3: Mimicking the analysis script (fetch all, filter in Python)
    logging.info("\n[TEST 3] Fetching all artists and filtering in Python (like the analysis script)...")
    try:
        response3 = db_client.table("artists").select("id, name, description, spotify_id").execute()
        
        # This logic should match our understanding of what needs to be updated
        filtered_in_py = [
            artist for artist in response3.data
            if artist.get("spotify_id") and (artist.get("description") is None or artist.get("description") == '')
        ]
        logging.info(f"  - RESULT: Query 3 (Python filter) found {len(filtered_in_py)} artists that match the criteria.")
        if filtered_in_py:
            logging.info(f"  - First matching artist found: {filtered_in_py[0]['name']}")

    except Exception as e:
        logging.error(f"  - ERROR: Query 3 failed with an exception: {e}")

    logging.info("\n--- Debug Complete ---")


if __name__ == "__main__":
    asyncio.run(debug_queries()) 