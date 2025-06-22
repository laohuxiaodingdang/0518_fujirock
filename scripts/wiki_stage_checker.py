import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.wikipedia_service import WikipediaService
from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WikiStageChecker:
    """检查主要舞台艺术家的 Wikipedia 状态"""
    
    def __init__(self):
        self.wikipedia_service = WikipediaService()
        
        # 主要舞台列表
        self.major_stages = [
            "GREEN STAGE",
            "WHITE STAGE", 
            "RED MARQUEE",
            "ORANGE GROOVE",
            "FIELD OF HEAVEN"
        ]
        
    def is_japanese_artist(self, artist_name: str) -> bool:
        """检测是否为日文艺术家"""
        return any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff' for char in artist_name)
    
    async def get_artist_stages(self, artist_id: str) -> List[str]:
        """获取艺术家的演出舞台"""
        try:
            response = db_service.supabase.table("performances").select("stage_name").eq("artist_id", artist_id).execute()
            return [perf["stage_name"] for perf in response.data] if response.data else []
        except Exception as e:
            logging.error(f"Error getting stages for artist {artist_id}: {e}")
            return []
    
    def is_major_stage_artist(self, stages: List[str]) -> bool:
        """检查是否来自主要舞台"""
        if not stages:
            return False
        return any(stage.upper() in [s.upper() for s in self.major_stages] for stage in stages)
    
    async def search_wikipedia(self, artist_name: str) -> Dict[str, Any]:
        """搜索 Wikipedia 条目"""
        result = {
            "found": False,
            "language": None,
            "title": None
        }
        
        # 搜索变体
        variations = [
            artist_name,
            f"{artist_name} (musician)",
            f"{artist_name} (band)",
            f"{artist_name} (artist)"
        ]
        
        # 根据艺术家类型选择语言
        is_japanese = self.is_japanese_artist(artist_name)
        languages = ["ja", "en"] if is_japanese else ["en"]
        
        for language in languages:
            for variation in variations:
                try:
                    logging.info(f"Trying {language.upper()} Wikipedia: '{variation}'")
                    wiki_data = await self.wikipedia_service.get_real_data(variation, language)
                    
                    if wiki_data and wiki_data.extract:
                        result["found"] = True
                        result["language"] = language
                        result["title"] = wiki_data.title
                        logging.info(f"✅ Found: '{wiki_data.title}' in {language.upper()}")
                        return result
                        
                except Exception as e:
                    logging.debug(f"Failed: '{variation}' in {language}")
                    continue
        
        return result
    
    async def check_all_artists(self):
        """检查所有艺术家"""
        logging.info("=== Checking Wikipedia Status for All Artists ===")
        
        # 获取所有艺术家
        response = await artist_db_service.get_fuji_rock_artists(limit=500)
        if not response.get("success"):
            logging.error("Failed to get artists")
            return
        
        artists = response.get("data", [])
        logging.info(f"Total artists: {len(artists)}")
        
        # 统计结果
        stats = {
            "total": len(artists),
            "with_wiki": 0,
            "major_stage_missing": [],
            "minor_stage_missing": []
        }
        
        for i, artist in enumerate(artists, 1):
            name = artist.get("name", "Unknown")
            artist_id = artist.get("id")
            
            logging.info(f"\n[{i}/{len(artists)}] {name}")
            
            # 检查是否已有 Wikipedia 数据
            if artist.get("wiki_extract"):
                logging.info(f"✅ Already has Wikipedia data")
                stats["with_wiki"] += 1
                continue
            
            # 获取舞台信息
            stages = await self.get_artist_stages(artist_id)
            is_major = self.is_major_stage_artist(stages)
            
            logging.info(f"Stages: {stages} | Major: {is_major}")
            
            # 搜索 Wikipedia
            wiki_result = await self.search_wikipedia(name)
            
            if wiki_result["found"]:
                stats["with_wiki"] += 1
                logging.info(f"✅ Found Wikipedia data")
            else:
                missing_info = {
                    "name": name,
                    "stages": stages,
                    "is_japanese": self.is_japanese_artist(name)
                }
                
                if is_major:
                    stats["major_stage_missing"].append(missing_info)
                    logging.warning(f"⚠️ Major stage artist missing Wikipedia")
                else:
                    stats["minor_stage_missing"].append(missing_info)
                    logging.info(f"ℹ️ Minor stage artist - no Wikipedia needed")
            
            await asyncio.sleep(0.5)
        
        # 打印结果
        self.print_results(stats)
    
    def print_results(self, stats: Dict[str, Any]):
        """打印结果"""
        logging.info("\n" + "="*60)
        logging.info("=== WIKIPEDIA STATUS REPORT ===")
        logging.info("="*60)
        
        total = stats["total"]
        with_wiki = stats["with_wiki"]
        major_missing = stats["major_stage_missing"]
        minor_missing = stats["minor_stage_missing"]
        
        logging.info(f"📊 SUMMARY:")
        logging.info(f"   Total artists: {total}")
        logging.info(f"   With Wikipedia: {with_wiki}")
        logging.info(f"   Coverage: {with_wiki/total*100:.1f}%")
        
        if major_missing:
            logging.info(f"\n⚠️ MAJOR STAGE ARTISTS MISSING WIKIPEDIA ({len(major_missing)}):")
            logging.info("-" * 50)
            for i, artist in enumerate(major_missing, 1):
                stages_str = ", ".join(artist["stages"]) if artist["stages"] else "Unknown"
                lang = "Japanese" if artist["is_japanese"] else "English"
                logging.info(f"{i:2d}. {artist['name']} ({lang}) - {stages_str}")
        else:
            logging.info(f"\n✅ ALL MAJOR STAGE ARTISTS HAVE WIKIPEDIA!")
        
        if minor_missing:
            logging.info(f"\nℹ️ MINOR STAGE ARTISTS WITHOUT WIKIPEDIA ({len(minor_missing)}):")
            logging.info("-" * 50)
            for i, artist in enumerate(minor_missing[:10], 1):
                stages_str = ", ".join(artist["stages"]) if artist["stages"] else "Unknown"
                logging.info(f"{i:2d}. {artist['name']} - {stages_str}")
            if len(minor_missing) > 10:
                logging.info(f"   ... and {len(minor_missing) - 10} more")
        
        logging.info("\n" + "="*60)

async def main():
    checker = WikiStageChecker()
    await checker.check_all_artists()

if __name__ == "__main__":
    asyncio.run(main()) 