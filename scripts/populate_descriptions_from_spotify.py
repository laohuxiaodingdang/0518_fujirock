import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.spotify_service import spotify_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotifyDescriptionGenerator:
    """
    使用 Spotify 的 'genres' 数据来填充艺术家的 'description' 字段。
    """
    def __init__(self):
        self.db_service = artist_db_service
        self.spotify_service = spotify_service

    def format_genres_as_description(self, genres: List[str]) -> str:
        """
        将流派列表格式化为适合展示的描述字符串。
        - 首字母大写
        - 用逗号和空格连接
        - 添加 "Genres: " 前缀
        """
        if not genres:
            return ""
        
        # 将每个流派的单词首字母大写
        formatted_genres = [genre.replace('-', ' ').title() for genre in genres]
        
        return f"Genres: {', '.join(formatted_genres)}"

    async def run(self):
        """执行从 Spotify genres 生成描述的流程"""
        logging.info("--- Starting Description Generation from Spotify Genres ---")

        # 1. 检查 Spotify 服务是否可用
        if not self.spotify_service.is_available():
            logging.error("Spotify service is not available. Please check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")
            return

        # 获取所有有 Spotify ID、无 Wiki、无 description 的艺术家
        logging.info("Fetching artists with Spotify ID, no Wiki, and no description...")
        response = self.db_service.db.supabase.table("artists").select("id, name, spotify_id, wiki_data, description").execute()
        if not response.data:
            logging.info("No artists found in database.")
            return
        # Python 过滤
        artists_to_update = [
            artist for artist in response.data
            if artist.get("spotify_id")
            and not artist.get("wiki_data")
            and (not artist.get("description") or artist.get("description") == "")
        ]
        if not artists_to_update:
            logging.info("No artists to update. All descriptions seem to be populated.")
            return

        total = len(artists_to_update)
        logging.info(f"Found {total} artists to generate descriptions for from Spotify.")

        updated_count = 0
        failed_artists = []
        for i, artist in enumerate(artists_to_update, 1):
            artist_id = artist['id']
            artist_name = artist['name']
            spotify_id = artist['spotify_id']

            logging.info(f"[{i}/{total}] Processing '{artist_name}' (Spotify ID: {spotify_id})...")

            try:
                # 3. 从 Spotify 获取完整的艺术家信息
                # 我们直接用 spotify_id 获取，比用名字搜索更准确
                artist_info = await self.spotify_service.get_artist_info(spotify_id)

                if not artist_info:
                    logging.warning(f"  - Could not retrieve Spotify info for '{artist_name}'. Skipping.")
                    failed_artists.append(artist_name)
                    continue

                # 修复：直接访问SpotifyArtist对象的属性，而不是使用.get()
                genres = artist_info.genres if hasattr(artist_info, 'genres') else []
                if not genres:
                    logging.warning(f"  - No genres found for '{artist_name}' on Spotify. Skipping.")
                    failed_artists.append(artist_name)
                    continue

                # 4. 生成描述并更新数据库
                description = self.format_genres_as_description(genres)
                logging.info(f"  - Generated description: \"{description}\"")

                update_data = {"description": description}
                update_response = await self.db_service.update_artist_simple(artist_id, update_data)

                if update_response.get("success"):
                    logging.info(f"  - ✅ Successfully updated '{artist_name}'.")
                    updated_count += 1
                else:
                    logging.error(f"  - ❌ Failed to update '{artist_name}': {update_response.get('error')}")
                    failed_artists.append(artist_name)

            except Exception as e:
                logging.error(f"  - ❌ An unexpected error occurred for '{artist_name}': {e}")
                failed_artists.append(artist_name)
            
            await asyncio.sleep(0.2) # 轻微延迟，避免瞬间请求过多，遵守API礼仪

        logging.info("\n--- Spotify Description Generation Complete ---")
        logging.info(f"  Total processed: {total}")
        logging.info(f"  Successfully updated: {updated_count}")
        logging.info(f"  Failed or skipped: {len(failed_artists)}")
        if failed_artists:
            logging.warning(f"  Failed/Skipped artists: {', '.join(failed_artists)}")


async def main():
    generator = SpotifyDescriptionGenerator()
    await generator.run()

if __name__ == "__main__":
    asyncio.run(main()) 