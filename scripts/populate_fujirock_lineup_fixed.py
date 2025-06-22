import asyncio
import logging
import sys
from pathlib import Path
from typing import Union
from datetime import datetime, date

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_date_string(date_str: str) -> date:
    """
    Parse date string like "7/25 (FRI)" to a date object
    """
    try:
        # Extract the date part (before the space)
        date_part = date_str.split(' ')[0]  # "7/25"
        month, day = map(int, date_part.split('/'))
        # Assume year 2025 for Fuji Rock
        return date(2025, month, day)
    except Exception as e:
        logging.error(f"Error parsing date '{date_str}': {e}")
        return date(2025, 7, 25)  # Default fallback

async def create_performance_record(artist_id: str, stage_name: str, performance_date: date) -> bool:
    """
    Create a performance record for an artist
    """
    try:
        # Prepare performance data
        performance_data = {
            "artist_id": artist_id,
            "stage_name": stage_name,
            "performance_date": performance_date.isoformat(),
            "start_time": "20:00:00",  # Default time, we don't have specific times
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert into performances table
        result = db_service.supabase.table("performances").insert(performance_data).execute()
        
        if result.data:
            logging.info(f"Performance record created for artist {artist_id}")
            return True
        else:
            logging.error(f"Failed to create performance record for artist {artist_id}")
            return False
            
    except Exception as e:
        logging.error(f"Error creating performance record: {e}")
        return False

async def populate_lineup_fixed():
    """
    Reads the lineup from fujirock_lineup_from_image.txt,
    creates artists and their performance records correctly.
    """
    lineup_file = project_root / "fujirock_lineup_from_image.txt"
    if not lineup_file.exists():
        logging.error(f"Lineup file not found at: {lineup_file}")
        return

    logging.info(f"Reading artists from {lineup_file}")
    with open(lineup_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_artists_added = 0
    artists_skipped = 0
    performances_created = 0
    total_artists_processed = 0
    
    current_date = ""
    current_stage = ""

    logging.info("Processing artists with correct database schema...")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Update date
        if "FRI JULY 25" in line:
            current_date = "7/25 (FRI)"
            continue
        elif "SAT JULY 26" in line:
            current_date = "7/26 (SAT)"
            continue
        elif "SUN JULY 27" in line:
            current_date = "7/27 (SUN)"
            continue
        
        # Update stage
        if line.startswith("###"):
            current_stage = line.replace("###", "").strip()
            continue

        # Process artist line
        if line.startswith("-"):
            artist_name = line.replace("-", "").strip()
            if not artist_name:
                continue

            total_artists_processed += 1
            logging.info(f"Processing: {artist_name} [{current_date} at {current_stage}]")

            # 1. Check if artist exists
            existing_artist_response = await artist_db_service.get_artist_by_name(artist_name)

            artist_id = None
            
            # Check if artist was not found
            is_artist_not_found = (
                not existing_artist_response.get("success") and
                "not found" in existing_artist_response.get("error", "").lower()
            )

            if is_artist_not_found:
                # 2. Artist does not exist, create
                logging.info(f"'{artist_name}' not found. Adding to database...")
                create_response = await artist_db_service.create_artist({
                    "name": artist_name,
                    "is_fuji_rock_artist": True,
                })
                if create_response.get("success"):
                    new_artists_added += 1
                    artist_id = create_response["data"]["id"]
                    logging.info(f"Successfully added '{artist_name}' with ID: {artist_id}")
                else:
                    logging.error(f"Failed to add '{artist_name}'. Error: {create_response.get('error')}")
                    continue
            elif existing_artist_response.get("success"):
                # 3. Artist already exists
                artists_skipped += 1
                artist_id = existing_artist_response["data"]["id"]
                logging.info(f"'{artist_name}' already exists with ID: {artist_id}. Skipping artist creation.")
            else:
                # Handle other, unexpected errors
                logging.error(f"An unexpected database error occurred for '{artist_name}'. Error: {existing_artist_response.get('error')}")
                continue

            # 4. Create performance record if we have an artist_id
            if artist_id and current_date and current_stage:
                performance_date = parse_date_string(current_date)
                if await create_performance_record(artist_id, current_stage, performance_date):
                    performances_created += 1
                    logging.info(f"Performance record created for '{artist_name}'")

    logging.info("--- Population Complete ---")
    logging.info(f"Total artists processed from file: {total_artists_processed}")
    logging.info(f"New artists added: {new_artists_added}")
    logging.info(f"Artists skipped (already existed): {artists_skipped}")
    logging.info(f"Performance records created: {performances_created}")
    logging.info("---------------------------")

if __name__ == "__main__":
    asyncio.run(populate_lineup_fixed()) 