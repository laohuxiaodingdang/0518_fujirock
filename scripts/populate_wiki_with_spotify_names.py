import asyncio
import logging
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.wikipedia_service import WikipediaService
from services.spotify_service import spotify_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotifyNameWikiPopulator:
    """使用 Spotify 官方名称来填充 Wikipedia 数据"""
    
    def __init__(self):
        self.wikipedia_service = WikipediaService()
        self.artist_db_service = artist_db_service
        self.spotify_service = spotify_service
        
    def is_japanese_artist(self, artist_name: str) -> bool:
        """检测是否为日文艺术家"""
        return any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff' for char in artist_name)
    
    def clean_spotify_name(self, spotify_name: str) -> str:
        """清理 Spotify 名称，移除一些明显不相关的后缀"""
        # 移除一些明显不相关的后缀
        suffixes_to_remove = [
            ' 一部のアニメテーマ専用仮設チャンネル',
            ' (Official)',
            ' (Official Channel)',
            ' - Topic',
            ' - オフィシャル'
        ]
        
        cleaned_name = spotify_name
        for suffix in suffixes_to_remove:
            if cleaned_name.endswith(suffix):
                cleaned_name = cleaned_name[:-len(suffix)].strip()
        
        return cleaned_name

    def generate_search_variations(self, db_name: str, spotify_name: str) -> List[str]:
        """生成搜索变体，优先使用清理后的 Spotify 名称"""
        variations = []
        
        # 清理 Spotify 名称
        clean_spotify_name = self.clean_spotify_name(spotify_name)
        
        # 优先使用清理后的 Spotify 名称
        if clean_spotify_name and clean_spotify_name != db_name:
            variations.append(clean_spotify_name)
        
        # 原始 Spotify 名称
        if spotify_name != clean_spotify_name:
            variations.append(spotify_name)
        
        # 数据库名称
        variations.append(db_name)
        
        # 清理变体
        clean_db_name = re.sub(r'[^\w\s]', '', db_name).strip()
        no_dots = db_name.replace('.', '').replace('..', '').strip()
        no_parens = re.sub(r'\s*\([^)]*\)', '', db_name).strip()
        
        base_names = list(dict.fromkeys([clean_db_name, no_dots, no_parens]))
        
        for name in base_names:
            if name and name not in variations: 
                variations.append(name)
        
        # 括号内的内容
        parens_only = re.findall(r'\(([^)]+)\)', db_name)
        for paren in parens_only:
            if paren.strip() not in variations:
                variations.append(paren.strip())
            
        # 添加后缀
        suffixes = [' (musician)', ' (band)', ' (artist)', ' (singer)', ' (rapper)']
        for name in [db_name, clean_spotify_name]:
            if name:
                for suffix in suffixes:
                    variation = name + suffix
                    if variation not in variations:
                        variations.append(variation)

        # 处理 & 符号
        if '&' in db_name:
            parts = [part.strip() for part in db_name.split('&')]
            for part in parts:
                if part and part not in variations:
                    variations.append(part)
            
        return list(dict.fromkeys(var for var in variations if var))[:20]

    async def get_artists_missing_wiki(self) -> List[Dict[str, Any]]:
        """获取有 Spotify ID 但缺少 Wiki 数据的艺术家"""
        logging.info("Fetching artists with Spotify ID but missing Wiki data...")
        
        response = self.artist_db_service.db.supabase.table("artists").select(
            "id, name, spotify_id, wiki_data, wiki_extract"
        ).execute()
        
        if not response.data:
            logging.error("Could not fetch artists from database.")
            return []
            
        # 过滤：有 spotify_id 但没有 wiki_data 的艺术家
        missing_artists = [
            artist for artist in response.data
            if artist.get("spotify_id") and not artist.get("wiki_data")
        ]
        
        logging.info(f"Found {len(missing_artists)} artists with Spotify ID but missing Wiki data.")
        return missing_artists

    async def get_spotify_artist_info(self, spotify_id: str):
        """获取 Spotify 艺术家信息"""
        try:
            return await self.spotify_service.get_artist_info(spotify_id)
        except Exception as e:
            logging.warning(f"Could not get Spotify info for {spotify_id}: {e}")
            return None

    async def populate_all(self):
        """为所有缺失的艺术家填充 Wikipedia 数据"""
        artists_to_update = await self.get_artists_missing_wiki()
        
        if not artists_to_update:
            logging.info("No artists to update. All artists with Spotify ID have Wikipedia data.")
            return
            
        total = len(artists_to_update)
        updated_count = 0
        failed_artists = []
        
        logging.info(f"=== Starting Wikipedia Population with Spotify Names for {total} Artists ===")
        
        for i, artist in enumerate(artists_to_update, 1):
            artist_name = artist["name"]
            artist_id = artist["id"]
            spotify_id = artist["spotify_id"]
            
            logging.info(f"\n[{i}/{total}] Processing: {artist_name} (Spotify ID: {spotify_id})")
            
            # 获取 Spotify 官方名称
            spotify_info = await self.get_spotify_artist_info(spotify_id)
            if not spotify_info or not hasattr(spotify_info, 'name'):
                logging.warning(f"  ⚠️ Could not get Spotify info for {artist_name}. Skipping.")
                failed_artists.append(artist_name)
                continue
            
            spotify_name = spotify_info.name
            logging.info(f"  Spotify official name: {spotify_name}")
            
            # 搜索 Wikipedia
            is_japanese = self.is_japanese_artist(artist_name) or self.is_japanese_artist(spotify_name)
            languages = ["ja", "en"] if is_japanese else ["en"]
            variations = self.generate_search_variations(artist_name, spotify_name)
            
            found_wiki = None
            for lang in languages:
                if found_wiki: break
                for var in variations:
                    try:
                        logging.info(f"  Trying {lang.upper()}: '{var}'")
                        wiki_data = await self.wikipedia_service.get_real_data(var, lang)
                        if wiki_data and wiki_data.extract:
                            found_wiki = wiki_data
                            logging.info(f"  ✅ Found: '{wiki_data.title}' in {lang.upper()}")
                            break
                    except Exception as e:
                        logging.debug(f"  Failed to search '{var}' in {lang}: {e}")
                        continue
            
            # 如果找到，则更新数据库
            if found_wiki:
                update_response = await self.artist_db_service.update_artist_wikipedia_data(
                    artist_id=artist_id,
                    wiki_data=found_wiki.model_dump(),
                    wiki_extract=found_wiki.extract
                )
                if update_response.get("success"):
                    logging.info(f"  🚀 Successfully updated database for {artist_name}")
                    updated_count += 1
                else:
                    logging.error(f"  ❌ Failed to update database for {artist_name}: {update_response.get('error')}")
                    failed_artists.append(artist_name)
            else:
                logging.warning(f"  ⚠️ No Wikipedia entry found for {artist_name}")
                failed_artists.append(artist_name)

            # 避免 API 限流
            await asyncio.sleep(1)

        logging.info("\n" + "="*60)
        logging.info("=== Wikipedia Population with Spotify Names Complete ===")
        logging.info(f"  Total artists processed: {total}")
        logging.info(f"  Successfully updated: {updated_count}")
        logging.info(f"  Failed to find: {total - updated_count}")
        
        if failed_artists:
            logging.info(f"\nFailed artists ({len(failed_artists)}):")
            for artist in failed_artists[:10]:  # 只显示前10个
                logging.info(f"  - {artist}")
            if len(failed_artists) > 10:
                logging.info(f"  ... and {len(failed_artists) - 10} more")
        
        logging.info("="*60)

async def main():
    populator = SpotifyNameWikiPopulator()
    await populator.populate_all()

if __name__ == "__main__":
    asyncio.run(main()) 