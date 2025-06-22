import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.spotify_service import SpotifyService
from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotifyPopulator:
    """批量补全 Spotify 数据"""
    def __init__(self):
        self.spotify_service = SpotifyService()
        self.artist_db_service = artist_db_service

    async def get_artists_missing_spotify(self) -> List[Dict[str, Any]]:
        """获取所有缺少 spotify_id 的艺术家"""
        logging.info("Fetching artists missing Spotify ID...")
        response = db_service.supabase.table("artists").select("*").is_("spotify_id", "null").execute()
        return response.data if response.data else []

    async def populate_all(self):
        """为所有缺失的艺术家补全 Spotify 数据"""
        artists = await self.get_artists_missing_spotify()
        total = len(artists)
        logging.info(f"Total artists missing Spotify ID: {total}")
        if not artists:
            logging.info("No artists to update.")
            return
        updated = 0
        for i, artist in enumerate(artists, 1):
            name = artist["name"]
            artist_id = artist["id"]
            logging.info(f"[{i}/{total}] Searching Spotify for: {name}")
            try:
                # 搜索 Spotify - 使用正确的方法名
                result = await self.spotify_service.get_artist_by_name(name)
                if not result or not result.get("id"):
                    logging.warning(f"  ⚠️ No Spotify result for {name}")
                    continue
                spotify_id = result["id"]
                genres = result.get("genres", [])
                images = result.get("images", [])
                image_url = images[0]["url"] if images else None
                # 更新数据库
                update_data = {
                    "spotify_id": spotify_id,
                    "genres": genres,
                    "image_url": image_url,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                resp = await self.artist_db_service.update_artist_simple(artist_id, update_data)
                if resp.get("success"):
                    logging.info(f"  ✅ Updated {name} with Spotify ID: {spotify_id}")
                    updated += 1
                else:
                    logging.warning(f"  ❌ Failed to update {name}: {resp.get('error')}")
            except Exception as e:
                logging.error(f"  ❌ Error for {name}: {str(e)}")
            await asyncio.sleep(0.5)  # 防止API限流
        logging.info(f"\n=== Spotify Population Complete ===\n  Total: {total}\n  Updated: {updated}\n  Failed: {total - updated}")

async def main():
    populator = SpotifyPopulator()
    await populator.populate_all()

if __name__ == "__main__":
    asyncio.run(main()) 