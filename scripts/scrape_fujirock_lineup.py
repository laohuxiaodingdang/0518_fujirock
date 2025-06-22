import requests
from bs4 import BeautifulSoup
import logging
from pathlib import Path
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
# The actual data is on the Japanese site, even when navigating from the English one.
LINEUP_URL = "https://www.fujirockfestival.com/artist/" 
OUTPUT_FILE = Path("fujirock_lineup.txt")

def scrape_fujirock_lineup():
    """
    Scrapes the Fuji Rock Festival lineup website to extract artist names and their performance dates.
    """
    logging.info(f"Attempting to scrape lineup from: {LINEUP_URL}")
    try:
        response = requests.get(LINEUP_URL, timeout=20)
        response.raise_for_status()
        logging.info("Successfully fetched the lineup page.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch lineup page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # The data is inside a <script> tag as a JSON object.
    # We need to find the correct script tag.
    script_tags = soup.find_all('script')
    
    lineup_data = None
    for script in script_tags:
        if script.string and 'window.artistData' in script.string:
            # Found the script. Let's extract the JSON part.
            logging.info("Found the artist data script tag.")
            # Use regex to find the JSON object assigned to window.artistData
            match = re.search(r'window\.artistData\s*=\s*(\{.*?\});', script.string, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    lineup_data = json.loads(json_str)
                    logging.info("Successfully parsed artist JSON data.")
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to parse JSON from script tag: {e}")
                    # Log the problematic string for debugging
                    logging.debug(f"Problematic JSON string: {json_str[:500]}...")
            break
            
    if not lineup_data or 'artists' not in lineup_data:
        logging.error("Could not extract or parse artist data from any script tag. Website structure may have changed.")
        return

    all_artists_by_date = {}
    date_map = {
        '25': '7.25 FRI',
        '26': '7.26 SAT',
        '27': '7.27 SUN'
    }

    for artist in lineup_data['artists']:
        day_code = artist.get('day')
        artist_name = artist.get('artist')
        
        if day_code and artist_name:
            date_key = date_map.get(day_code)
            if date_key:
                if date_key not in all_artists_by_date:
                    all_artists_by_date[date_key] = []
                all_artists_by_date[date_key].append(artist_name)

    if not all_artists_by_date:
        logging.warning("No artists were processed. Check the JSON structure.")
        return

    output_content = "Fuji Rock Festival 2025 Lineup\n"
    output_content += "=" * 40 + "\n\n"

    # Sort by date to ensure consistent order
    for date_key in sorted(all_artists_by_date.keys()):
        output_content += f"## {date_key}\n"
        output_content += "-" * len(date_key) + "\n"
        # Sort artists alphabetically for consistency
        for artist in sorted(all_artists_by_date[date_key]):
            output_content += f"- {artist}\n"
        output_content += "\n"

    try:
        OUTPUT_FILE.write_text(output_content, encoding='utf-8')
        logging.info(f"Successfully saved lineup information to {OUTPUT_FILE}")
        print(f"Scraped data saved to {OUTPUT_FILE}")
    except IOError as e:
        logging.error(f"Failed to write to file {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    scrape_fujirock_lineup() 