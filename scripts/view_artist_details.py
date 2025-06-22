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

async def view_artist_details(artist_name: str):
    """查看艺术家的详细信息"""
    logging.info(f"Viewing details for artist: '{artist_name}'")
    
    # 获取艺术家信息
    response = artist_db_service.db.supabase.table("artists").select("*").eq("name", artist_name).execute()
    
    if not response.data:
        logging.error(f"Artist '{artist_name}' not found.")
        return
    
    artist = response.data[0]
    
    print(f"\n🎵 Artist Details for '{artist['name']}':")
    print(f"  ID: {artist['id']}")
    print(f"  Name: {artist['name']}")
    print(f"  Spotify ID: {artist.get('spotify_id', 'N/A')}")
    print(f"  Has Wiki Data: {'Yes' if artist.get('wiki_data') else 'No'}")
    print(f"  Has Wiki Extract: {'Yes' if artist.get('wiki_extract') else 'No'}")
    print(f"  Has Description: {'Yes' if artist.get('description') else 'No'}")
    
    if artist.get('description'):
        print(f"  Description: {artist['description']}")
    
    if artist.get('wiki_extract'):
        print(f"  Wiki Extract Preview: {artist['wiki_extract'][:200]}...")
    
    if artist.get('wiki_data'):
        wiki_data = artist['wiki_data']
        if isinstance(wiki_data, dict):
            print(f"  Wiki Data Keys: {list(wiki_data.keys())}")
            if 'title' in wiki_data:
                print(f"  Wiki Title: {wiki_data['title']}")

async def main():
    artist_name = "Fred again.."
    await view_artist_details(artist_name)

if __name__ == "__main__":
    asyncio.run(main()) 