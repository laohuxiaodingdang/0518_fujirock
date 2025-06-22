import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.spotify_service import SpotifyService
from services.wikipedia_service import WikipediaService
from services.database_service import db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataPopulator:
    """数据填充器 - 批量填充 Spotify 和 Wikipedia 数据"""
    
    def __init__(self):
        self.spotify_service = SpotifyService()
        self.wikipedia_service = WikipediaService()
        self.artist_db_service = artist_db_service
        
    def generate_search_variations(self, artist_name: str) -> List[str]:
        """生成多种搜索变体来提高 Wikipedia 搜索成功率"""
        variations = [artist_name]
        
        # 移除特殊字符和多余空格
        clean_name = re.sub(r'[^\w\s]', ' ', artist_name).strip()
        if clean_name != artist_name:
            variations.append(clean_name)
        
        # 尝试不同的语言
        if any('\u4e00' <= char <= '\u9fff' for char in artist_name):  # 包含中文字符
            # 对于日文/中文艺术家，尝试英文搜索
            variations.append(f"{artist_name} (musician)")
            variations.append(f"{artist_name} (band)")
        else:
            # 对于英文艺术家，尝试添加音乐相关词汇
            variations.append(f"{artist_name} (musician)")
            variations.append(f"{artist_name} (band)")
            variations.append(f"{artist_name} (artist)")
        
        # 移除重复项
        return list(dict.fromkeys(variations))
    
    async def search_wikipedia_with_variations(self, artist_name: str) -> Dict[str, Any]:
        """使用多种变体搜索 Wikipedia 数据"""
        variations = self.generate_search_variations(artist_name)
        
        for variation in variations:
            try:
                logging.info(f"Trying Wikipedia search: '{variation}'")
                
                # 直接调用 Wikipedia 服务的真实数据方法
                wiki_data = await self.wikipedia_service.get_real_data(variation, "en")
                
                if wiki_data and wiki_data.extract:
                    logging.info(f"✅ Found Wikipedia data for: '{variation}'")
                    return {
                        "success": True,
                        "data": wiki_data,
                        "search_term": variation
                    }
                    
            except Exception as e:
                logging.debug(f"Wikipedia search failed for '{variation}': {str(e)}")
                continue
        
        # 如果所有变体都失败，尝试搜索 API
        try:
            logging.info(f"Trying Wikipedia search API for: '{artist_name}'")
            search_results = await self.wikipedia_service.search_artists(artist_name, language="en", limit=5)
            
            if search_results:
                # 尝试第一个搜索结果
                first_result = search_results[0]
                title = first_result.get("title", "")
                
                if title:
                    try:
                        wiki_data = await self.wikipedia_service.get_real_data(title, "en")
                        if wiki_data and wiki_data.extract:
                            logging.info(f"✅ Found Wikipedia data via search: '{title}'")
                            return {
                                "success": True,
                                "data": wiki_data,
                                "search_term": title
                            }
                    except Exception as e:
                        logging.debug(f"Failed to get data for search result '{title}': {str(e)}")
                        
        except Exception as e:
            logging.debug(f"Wikipedia search API failed: {str(e)}")
        
        logging.warning(f"❌ No Wikipedia data found for: '{artist_name}' after trying all variations")
        return {"success": False, "data": None, "search_term": None}
    
    async def get_artists_needing_data(self) -> List[Dict[str, Any]]:
        """获取需要填充数据的艺术家列表"""
        try:
            # 获取所有 Fuji Rock 艺术家
            response = await self.artist_db_service.get_fuji_rock_artists(limit=500)
            
            if not response.get("success"):
                logging.error(f"Failed to get artists: {response.get('error')}")
                return []
            
            artists = response.get("data", [])
            
            # 过滤出需要数据的艺术家（缺少 spotify_id 或 wiki_extract）
            artists_needing_data = []
            for artist in artists:
                spotify_id = artist.get("spotify_id")
                wiki_extract = artist.get("wiki_extract")
                
                if not spotify_id or not wiki_extract:
                    artists_needing_data.append(artist)
            
            logging.info(f"Found {len(artists_needing_data)} artists needing data out of {len(artists)} total")
            return artists_needing_data
            
        except Exception as e:
            logging.error(f"Error getting artists: {e}")
            return []
    
    async def populate_spotify_data(self, artist: Dict[str, Any]) -> bool:
        """填充 Spotify 数据"""
        try:
            artist_name = artist.get("name", "")
            artist_id = artist.get("id")
            
            if not artist_name or not artist_id:
                logging.error(f"Invalid artist data: {artist}")
                return False
            
            logging.info(f"Getting Spotify data for: {artist_name}")
            
            # 搜索艺术家
            spotify_artists = await self.spotify_service.search_artists(artist_name, limit=1)
            
            if not spotify_artists:
                logging.warning(f"No Spotify data found for: {artist_name}")
                return False
            
            spotify_artist = spotify_artists[0]
            spotify_id = spotify_artist.get("id")
            
            if not spotify_id:
                logging.warning(f"No Spotify ID found for: {artist_name}")
                return False
            
            # 准备更新数据
            update_data = {
                "spotify_id": spotify_id,
                "genres": spotify_artist.get("genres", []),
                "image_url": spotify_artist.get("images", [{}])[0].get("url") if spotify_artist.get("images") else None
            }
            
            # 更新数据库
            update_response = await self.artist_db_service.update_artist_simple(str(artist_id), update_data)
            
            if update_response.get("success"):
                logging.info(f"✅ Spotify data updated for: {artist_name}")
                return True
            else:
                logging.error(f"Failed to update Spotify data for {artist_name}: {update_response.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"Error populating Spotify data for {artist.get('name', 'Unknown')}: {e}")
            return False
    
    async def populate_wikipedia_data(self, artist: Dict[str, Any]) -> bool:
        """填充 Wikipedia 数据"""
        try:
            artist_name = artist.get("name", "")
            artist_id = artist.get("id")
            
            if not artist_name or not artist_id:
                logging.error(f"Invalid artist data: {artist}")
                return False
            
            logging.info(f"Getting Wikipedia data for: {artist_name}")
            
            # 使用改进的搜索策略
            wiki_result = await self.search_wikipedia_with_variations(artist_name)
            
            if not wiki_result["success"]:
                logging.warning(f"No Wikipedia data found for: {artist_name}")
                return False
            
            wiki_data = wiki_result["data"]
            
            # 准备更新数据
            update_data = {
                "wiki_extract": wiki_data.extract,
                "wiki_data": {
                    "title": wiki_data.title,
                    "categories": wiki_data.categories,
                    "references": [ref.model_dump() for ref in wiki_data.references] if wiki_data.references else []
                },
                "wiki_last_updated": datetime.now().isoformat()
            }
            
            # 如果没有 image_url，使用 Wikipedia 的图片
            if not artist.get("image_url") and wiki_data.thumbnail:
                update_data["image_url"] = wiki_data.thumbnail.source
            
            # 更新数据库
            update_response = await self.artist_db_service.update_artist_simple(str(artist_id), update_data)
            
            if update_response.get("success"):
                logging.info(f"✅ Wikipedia data updated for: {artist_name} (via '{wiki_result['search_term']}')")
                return True
            else:
                logging.error(f"Failed to update Wikipedia data for {artist_name}: {update_response.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"Error populating Wikipedia data for {artist.get('name', 'Unknown')}: {e}")
            return False
    
    async def populate_artist_data(self, artist: Dict[str, Any]) -> Dict[str, bool]:
        """为单个艺术家填充所有数据"""
        results = {
            "spotify": False,
            "wikipedia": False
        }
        
        artist_name = artist.get("name", "Unknown")
        logging.info(f"\n--- Processing: {artist_name} ---")
        
        # 检查是否需要 Spotify 数据
        if not artist.get("spotify_id"):
            results["spotify"] = await self.populate_spotify_data(artist)
        else:
            logging.info(f"Spotify data already exists for: {artist_name}")
            results["spotify"] = True
        
        # 检查是否需要 Wikipedia 数据
        if not artist.get("wiki_extract"):
            results["wikipedia"] = await self.populate_wikipedia_data(artist)
        else:
            logging.info(f"Wikipedia data already exists for: {artist_name}")
            results["wikipedia"] = True
        
        # 添加延迟以避免 API 限制
        await asyncio.sleep(1)
        
        return results
    
    async def run_population(self, max_artists: int = 10):
        """运行数据填充流程"""
        logging.info("=== Starting Spotify & Wikipedia Data Population ===")
        
        # 获取需要数据的艺术家
        artists = await self.get_artists_needing_data()
        
        if not artists:
            logging.info("No artists need data population")
            return
        
        # 限制处理数量（避免 API 限制）
        artists_to_process = artists[:max_artists]
        logging.info(f"Processing {len(artists_to_process)} artists (limited from {len(artists)})")
        
        # 统计结果
        total_processed = 0
        spotify_success = 0
        wikipedia_success = 0
        
        # 处理每个艺术家
        for i, artist in enumerate(artists_to_process, 1):
            logging.info(f"\n[{i}/{len(artists_to_process)}] Processing artist...")
            
            try:
                results = await self.populate_artist_data(artist)
                
                total_processed += 1
                if results["spotify"]:
                    spotify_success += 1
                if results["wikipedia"]:
                    wikipedia_success += 1
                    
            except Exception as e:
                logging.error(f"Error processing artist {artist.get('name', 'Unknown')}: {e}")
                continue
        
        # 输出统计结果
        logging.info("\n=== Population Complete ===")
        logging.info(f"Total artists processed: {total_processed}")
        logging.info(f"Spotify data success: {spotify_success}/{total_processed}")
        logging.info(f"Wikipedia data success: {wikipedia_success}/{total_processed}")
        logging.info("==========================")

async def main():
    """主函数"""
    populator = DataPopulator()
    
    # 设置处理数量（避免 API 限制）
    max_artists = 10  # 先处理10个艺术家测试新策略
    
    await populator.run_population(max_artists)

if __name__ == "__main__":
    asyncio.run(main()) 