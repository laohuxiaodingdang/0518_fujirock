import asyncio
import logging
import sys
import re
import httpx
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import urllib.parse

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from services.spotify_service import spotify_service
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImprovedWikiSearcher:
    """改进的Wikipedia搜索器，使用多种策略提高成功率"""
    
    def __init__(self):
        self.db_service = artist_db_service
        self.spotify_service = spotify_service
        self.timeout = 30.0
        
        # Wikipedia API endpoints for different languages
        self.wiki_apis = {
            "zh": "https://zh.wikipedia.org/api/rest_v1",
            "en": "https://en.wikipedia.org/api/rest_v1", 
            "ja": "https://ja.wikipedia.org/api/rest_v1"
        }
    
    def clean_search_term(self, name: str) -> str:
        """清理搜索词，移除特殊字符"""
        # 移除括号及其内容
        cleaned = re.sub(r'\([^)]*\)', '', name)
        # 移除特殊字符，保留字母、数字、空格和连字符
        cleaned = re.sub(r'[^\w\s\-]', ' ', cleaned)
        # 移除多余空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def generate_search_variations(self, original_name: str, spotify_name: str = None) -> List[str]:
        """生成多种搜索变体"""
        variations = []
        
        # 1. 原始名称
        variations.append(original_name)
        
        # 2. 清理后的名称
        cleaned_name = self.clean_search_term(original_name)
        if cleaned_name and cleaned_name != original_name:
            variations.append(cleaned_name)
        
        # 3. Spotify官方名称（如果不同）
        if spotify_name and spotify_name != original_name:
            variations.append(spotify_name)
            # Spotify名称的清理版本
            cleaned_spotify = self.clean_search_term(spotify_name)
            if cleaned_spotify and cleaned_spotify != spotify_name:
                variations.append(cleaned_spotify)
        
        # 4. 大小写变体
        if original_name.isupper():
            # 如果全大写，尝试首字母大写
            title_case = original_name.title()
            variations.append(title_case)
        elif original_name.islower():
            # 如果全小写，尝试首字母大写
            title_case = original_name.title()
            variations.append(title_case)
        
        # 5. 移除常见前缀/后缀
        prefixes_to_remove = ["DJ ", "MC ", "Dr. ", "Prof. "]
        suffixes_to_remove = [" (Band)", " (Artist)", " (Musician)", " (Group)"]
        
        for prefix in prefixes_to_remove:
            if original_name.startswith(prefix):
                variations.append(original_name[len(prefix):].strip())
        
        for suffix in suffixes_to_remove:
            if original_name.endswith(suffix):
                variations.append(original_name[:-len(suffix)].strip())
        
        # 6. 处理特殊字符
        # 移除多余的点号和特殊字符
        special_cleaned = re.sub(r'\.{2,}', '', original_name)  # 移除多个连续点号
        special_cleaned = re.sub(r'[^\w\s\-]', ' ', special_cleaned)  # 移除特殊字符
        special_cleaned = re.sub(r'\s+', ' ', special_cleaned).strip()  # 清理空格
        if special_cleaned and special_cleaned != original_name:
            variations.append(special_cleaned)
        
        # 去重并过滤空字符串
        unique_variations = list(set([v for v in variations if v.strip()]))
        return unique_variations
    
    async def search_wikipedia(self, search_term: str, language: str = "zh") -> Optional[Dict[str, Any]]:
        """搜索Wikipedia API"""
        if not search_term.strip():
            return None
            
        api_url = self.wiki_apis.get(language)
        if not api_url:
            return None
        
        # 正确URL编码搜索词
        encoded_search_term = urllib.parse.quote(search_term)
        search_url = f"{api_url}/page/summary/{encoded_search_term}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    data = response.json()
                    extract = data.get("extract", "")
                    # 确保有实际内容
                    if extract and len(extract.strip()) > 10:
                        return {
                            "title": data.get("title", ""),
                            "extract": extract,
                            "thumbnail": data.get("thumbnail"),
                            "language": language,
                            "search_term": search_term
                        }
                    else:
                        logging.debug(f"Found page but no extract for '{search_term}' in {language}")
                        return None
                else:
                    logging.debug(f"Wikipedia search failed for '{search_term}' in {language}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logging.debug(f"Wikipedia search error for '{search_term}' in {language}: {e}")
            return None
    
    async def get_spotify_artist_name(self, spotify_id: str) -> Optional[str]:
        """通过Spotify ID获取艺术家官方名称"""
        try:
            artist_data = await self.spotify_service.get_artist_info(spotify_id)
            return artist_data.name if artist_data else None
        except Exception as e:
            logging.debug(f"Failed to get Spotify artist name for {spotify_id}: {e}")
            return None
    
    async def search_artist_wiki(self, artist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """为单个艺术家搜索Wikipedia，使用多种策略"""
        artist_name = artist["name"]
        spotify_id = artist.get("spotify_id")
        
        logging.info(f"🔍 Searching Wiki for: {artist_name}")
        
        # 获取Spotify官方名称
        spotify_name = None
        if spotify_id:
            spotify_name = await self.get_spotify_artist_name(spotify_id)
            if spotify_name:
                logging.info(f"  📱 Spotify official name: {spotify_name}")
        
        # 生成搜索变体
        search_variations = self.generate_search_variations(artist_name, spotify_name)
        logging.info(f"  🔄 Search variations: {search_variations}")
        
        # 按优先级搜索不同语言版本：英文优先，然后日文
        languages = ["en", "ja"]  # 英文、日文优先级
        
        for language in languages:
            for search_term in search_variations:
                logging.info(f"    🌐 Trying {language} Wiki: '{search_term}'")
                
                result = await self.search_wikipedia(search_term, language)
                if result and result.get("extract"):
                    logging.info(f"    ✅ Found in {language} Wiki!")
                    return result
                
                # 避免请求过于频繁
                await asyncio.sleep(0.5)
        
        logging.info(f"    ❌ No Wiki data found for {artist_name}")
        return None
    
    async def get_artists_without_wiki(self) -> List[Dict[str, Any]]:
        """获取没有Wiki数据的艺术家"""
        response = self.db_service.db.supabase.table("artists").select(
            "id, name, spotify_id, genres"
        ).execute()
        
        if not response.data:
            return []
        
        # 过滤出没有wiki_extract的艺术家
        artists_without_wiki = [
            artist for artist in response.data 
            if not artist.get("wiki_extract")
        ]
        
        return artists_without_wiki
    
    async def update_artist_wiki(self, artist_id: str, wiki_data: Dict[str, Any]) -> bool:
        """更新艺术家的Wiki数据"""
        try:
            # 构建wiki_data JSON对象
            wiki_json = {
                "title": wiki_data["title"],
                "language": wiki_data["language"],
                "search_term": wiki_data["search_term"],
                "thumbnail": wiki_data.get("thumbnail")
            }
            
            # 更新字段
            update_data = {
                "wiki_extract": wiki_data["extract"],
                "wiki_data": wiki_json,
                "wiki_last_updated": "now()"
            }
            
            result = self.db_service.db.supabase.table("artists").update(update_data).eq("id", artist_id).execute()
            
            return bool(result.data)
        except Exception as e:
            logging.error(f"Failed to update Wiki data for artist {artist_id}: {e}")
            return False
    
    async def search_all_missing_wiki(self, limit: int = None):
        """为所有缺少Wiki数据的艺术家进行搜索"""
        artists_to_process = await self.get_artists_without_wiki()
        
        if limit:
            artists_to_process = artists_to_process[:limit]
        
        if not artists_to_process:
            logging.info("No artists without Wiki data found.")
            return
        
        total = len(artists_to_process)
        success_count = 0
        failed_artists = []
        
        logging.info(f"=== Starting Improved Wiki Search for {total} Artists ===")
        
        for i, artist in enumerate(artists_to_process, 1):
            artist_id = artist["id"]
            artist_name = artist["name"]
            
            logging.info(f"\n[{i}/{total}] Processing: {artist_name}")
            
            try:
                wiki_data = await self.search_artist_wiki(artist)
                
                if wiki_data:
                    # 保存到数据库
                    if await self.update_artist_wiki(artist_id, wiki_data):
                        logging.info(f"  🚀 Successfully saved Wiki data for {artist_name}")
                        logging.info(f"     Language: {wiki_data['language']}")
                        logging.info(f"     Title: {wiki_data['title']}")
                        logging.info(f"     Extract: {wiki_data['extract'][:100]}...")
                        success_count += 1
                    else:
                        logging.error(f"  ❌ Failed to save Wiki data for {artist_name}")
                        failed_artists.append(artist_name)
                else:
                    logging.warning(f"  ⚠️ No Wiki data found for {artist_name}")
                    failed_artists.append(artist_name)
                
            except Exception as e:
                logging.error(f"  ❌ Error processing {artist_name}: {e}")
                failed_artists.append(artist_name)
            
            # 避免请求过于频繁
            await asyncio.sleep(1)
        
        # 输出统计结果
        logging.info("\n" + "="*60)
        logging.info("=== Improved Wiki Search Complete ===")
        logging.info(f"  Total artists processed: {total}")
        logging.info(f"  Successfully found Wiki: {success_count}")
        logging.info(f"  Failed: {total - success_count}")
        logging.info(f"  Success rate: {(success_count/total*100):.1f}%")
        
        if failed_artists:
            logging.info(f"\nFailed artists ({len(failed_artists)}):")
            for artist in failed_artists[:10]:
                logging.info(f"  - {artist}")
            if len(failed_artists) > 10:
                logging.info(f"  ... and {len(failed_artists) - 10} more")
        
        logging.info("="*60)

async def main():
    searcher = ImprovedWikiSearcher()
    
    # 先测试 RADWIMPS
    print("🧪 Testing with RADWIMPS specifically...")
    test_artist = {
        "id": "test-id",
        "name": "RADWIMPS",
        "spotify_id": None,
        "genres": []
    }
    
    result = await searcher.search_artist_wiki(test_artist)
    if result:
        print(f"✅ SUCCESS! Found Wiki data for RADWIMPS:")
        print(f"   Language: {result['language']}")
        print(f"   Title: {result['title']}")
        print(f"   Extract: {result['extract'][:200]}...")
    else:
        print("❌ FAILED to find Wiki data for RADWIMPS")
    
    # 然后测试几个艺术家
    print("\n🧪 Testing with first 3 artists...")
    await searcher.search_all_missing_wiki(limit=3)
    
    # 询问是否继续处理所有艺术家
    print("\n" + "="*60)
    print("Do you want to continue with all remaining artists?")
    print("This will process all artists without Wiki data.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main()) 