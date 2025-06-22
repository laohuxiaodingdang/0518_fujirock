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

class FailedWikiAnalyzer:
    """分析缺少 Wiki 数据的艺术家"""
    
    def __init__(self):
        self.artist_db_service = artist_db_service
        self.spotify_service = spotify_service
        
    def is_japanese_artist(self, artist_name: str) -> bool:
        """检测是否为日文艺术家"""
        return any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff' for char in artist_name)

    async def get_failed_artists(self) -> List[Dict[str, Any]]:
        """获取有 Spotify ID 但缺少 Wiki 数据的艺术家"""
        logging.info("Fetching artists with Spotify ID but missing Wiki data...")
        
        response = self.artist_db_service.db.supabase.table("artists").select(
            "id, name, spotify_id, wiki_data, wiki_extract"
        ).execute()
        
        if not response.data:
            logging.error("Could not fetch artists from database.")
            return []
            
        # 过滤：有 spotify_id 但没有 wiki_data 的艺术家
        failed_artists = [
            artist for artist in response.data
            if artist.get("spotify_id") and not artist.get("wiki_data")
        ]
        
        logging.info(f"Found {len(failed_artists)} artists with Spotify ID but missing Wiki data.")
        return failed_artists

    async def get_spotify_artist_info(self, spotify_id: str):
        """获取 Spotify 艺术家信息"""
        try:
            return await self.spotify_service.get_artist_info(spotify_id)
        except Exception as e:
            logging.warning(f"Could not get Spotify info for {spotify_id}: {e}")
            return None

    async def analyze_failed_artists(self):
        """分析失败的艺术家"""
        failed_artists = await self.get_failed_artists()
        
        if not failed_artists:
            logging.info("No failed artists to analyze.")
            return
            
        print(f"\n🔍 Analyzing {len(failed_artists)} artists missing Wiki data...")
        
        # 分类统计
        japanese_artists = []
        english_artists = []
        special_char_artists = []
        
        spotify_names = []
        no_spotify_info = []
        
        for artist in failed_artists:
            name = artist["name"]
            spotify_id = artist["spotify_id"]
            
            # 按语言分类
            if self.is_japanese_artist(name):
                japanese_artists.append(artist)
            else:
                english_artists.append(artist)
            
            # 检查特殊字符
            if any(char in name for char in ['&', '(', ')', '.', '..', '/', '&']):
                special_char_artists.append(artist)
            
            # 获取 Spotify 信息
            spotify_info = await self.get_spotify_artist_info(spotify_id)
            if spotify_info and hasattr(spotify_info, 'name'):
                spotify_names.append({
                    'db_name': name,
                    'spotify_name': spotify_info.name,
                    'artist': artist
                })
            else:
                no_spotify_info.append(artist)
            
            # 避免 API 限流
            await asyncio.sleep(0.1)
        
        # 输出分析结果
        print(f"\n📊 Analysis Results:")
        print(f"  - Japanese artists: {len(japanese_artists)}")
        print(f"  - English artists: {len(english_artists)}")
        print(f"  - Artists with special characters: {len(special_char_artists)}")
        print(f"  - Artists with different Spotify names: {len(spotify_names)}")
        print(f"  - Artists with no Spotify info: {len(no_spotify_info)}")
        
        # 显示一些示例
        if spotify_names:
            print(f"\n📝 Examples of name differences:")
            for i, item in enumerate(spotify_names[:10], 1):
                print(f"  {i}. DB: '{item['db_name']}' → Spotify: '{item['spotify_name']}'")
            if len(spotify_names) > 10:
                print(f"  ... and {len(spotify_names) - 10} more")
        
        if special_char_artists:
            print(f"\n🔤 Examples of artists with special characters:")
            for i, artist in enumerate(special_char_artists[:10], 1):
                print(f"  {i}. {artist['name']}")
            if len(special_char_artists) > 10:
                print(f"  ... and {len(special_char_artists) - 10} more")
        
        # 建议下一步行动
        print(f"\n💡 Recommendations:")
        print(f"  1. Focus on artists with different Spotify names ({len(spotify_names)} artists)")
        print(f"  2. Handle special character cases ({len(special_char_artists)} artists)")
        print(f"  3. Manual search for Japanese artists ({len(japanese_artists)} artists)")
        
        return {
            'spotify_names': spotify_names,
            'special_char_artists': special_char_artists,
            'japanese_artists': japanese_artists,
            'english_artists': english_artists
        }

async def main():
    analyzer = FailedWikiAnalyzer()
    await analyzer.analyze_failed_artists()

if __name__ == "__main__":
    asyncio.run(main()) 