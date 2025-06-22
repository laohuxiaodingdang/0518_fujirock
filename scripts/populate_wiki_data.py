import asyncio
import logging
import sys
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.wikipedia_service import WikipediaService
from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WikiPopulator:
    """填充 Wikipedia 数据到数据库"""
    
    def __init__(self):
        self.wikipedia_service = WikipediaService()
        self.artist_db_service = artist_db_service
        
        # 主要舞台列表
        self.major_stages = [
            "GREEN STAGE", "WHITE STAGE", "RED MARQUEE", 
            "ORANGE GROOVE", "FIELD OF HEAVEN"
        ]
        
    def is_japanese_artist(self, artist_name: str) -> bool:
        """检测是否为日文艺术家"""
        return any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff' for char in artist_name)
    
    def generate_search_variations(self, artist_name: str) -> List[str]:
        """生成搜索变体"""
        variations = []
        clean_name = re.sub(r'[^\w\s]', '', artist_name).strip()
        no_dots = artist_name.replace('.', '').replace('..', '').strip()
        no_parens = re.sub(r'\s*\([^)]*\)', '', artist_name).strip()
        
        base_names = list(dict.fromkeys([artist_name, clean_name, no_dots, no_parens]))
        
        for name in base_names:
            if name: variations.append(name)
        
        parens_only = re.findall(r'\(([^)]+)\)', artist_name)
        for paren in parens_only:
            variations.append(paren.strip())
            
        suffixes = [' (musician)', ' (band)', ' (artist)']
        for name in base_names:
            if name:
                for suffix in suffixes:
                    variations.append(name + suffix)

        if '&' in artist_name:
            parts = [part.strip() for part in artist_name.split('&')]
            variations.extend(parts)
            
        return list(dict.fromkeys(var for var in variations if var))[:10]

    async def get_missing_wiki_artists(self) -> List[Dict[str, Any]]:
        """获取所有缺少 Wikipedia 数据的主舞台艺术家"""
        logging.info("Fetching artists missing Wikipedia data...")
        
        all_artists_resp = await self.artist_db_service.get_fuji_rock_artists(limit=500)
        if not all_artists_resp.get("success"):
            logging.error("Failed to fetch artists.")
            return []
            
        all_artists = all_artists_resp.get("data", [])
        
        missing_artists = []
        for artist in all_artists:
            # 检查是否已有 wiki_extract
            if not artist.get("wiki_extract"):
                # 获取演出信息并判断是否是主舞台
                performances_resp = await self.artist_db_service.get_artist_performances(artist["id"])
                if performances_resp.get("success"):
                    stages = [p["stage_name"] for p in performances_resp.get("data", [])]
                    is_major = any(s.upper() in self.major_stages for s in stages)
                    if is_major:
                        missing_artists.append(artist)
        
        logging.info(f"Found {len(missing_artists)} major stage artists missing Wikipedia data.")
        return missing_artists

    async def populate_all(self):
        """为所有缺失的艺术家填充 Wikipedia 数据"""
        artists_to_update = await self.get_missing_wiki_artists()
        
        if not artists_to_update:
            logging.info("No artists to update. All major stage artists have Wikipedia data.")
            return
            
        total = len(artists_to_update)
        updated_count = 0
        
        logging.info(f"=== Starting Wikipedia Population for {total} Artists ===")
        
        for i, artist in enumerate(artists_to_update, 1):
            artist_name = artist["name"]
            artist_id = artist["id"]
            
            logging.info(f"\n[{i}/{total}] Processing: {artist_name}")
            
            # 搜索 Wikipedia
            is_japanese = self.is_japanese_artist(artist_name)
            languages = ["ja", "en"] if is_japanese else ["en"]
            variations = self.generate_search_variations(artist_name)
            
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
                    except Exception:
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
            else:
                logging.warning(f"  ⚠️ No Wikipedia entry found for {artist_name}")

            await asyncio.sleep(1) # 避免API限流

        logging.info("\n" + "="*60)
        logging.info("=== Wikipedia Population Complete ===")
        logging.info(f"  Total artists processed: {total}")
        logging.info(f"  Successfully updated: {updated_count}")
        logging.info(f"  Failed to find: {total - updated_count}")
        logging.info("="*60)

async def main():
    populator = WikiPopulator()
    await populator.populate_all()

if __name__ == "__main__":
    asyncio.run(main()) 