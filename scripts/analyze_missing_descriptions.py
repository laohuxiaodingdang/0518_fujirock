import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MissingDescriptionAnalyzer:
    """分析缺少 Description 的艺术家"""
    
    def __init__(self):
        self.artist_db_service = artist_db_service
        
    def is_japanese_artist(self, artist_name: str) -> bool:
        """检测是否为日文艺术家"""
        return any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' or '\u4e00' <= char <= '\u9fff' for char in artist_name)

    async def get_artists_missing_description(self) -> List[Dict[str, Any]]:
        """获取缺少 Description 的艺术家"""
        logging.info("Fetching artists missing descriptions...")
        
        response = self.artist_db_service.db.supabase.table("artists").select(
            "id, name, spotify_id, wiki_data, wiki_extract, description"
        ).execute()
        
        if not response.data:
            logging.error("Could not fetch artists from database.")
            return []
            
        # 过滤：没有 description 的艺术家
        missing_artists = [
            artist for artist in response.data
            if not artist.get("description") or artist.get("description") == ""
        ]
        
        logging.info(f"Found {len(missing_artists)} artists missing descriptions.")
        return missing_artists

    async def analyze_missing_descriptions(self):
        """分析缺少 Description 的艺术家"""
        missing_artists = await self.get_artists_missing_description()
        
        if not missing_artists:
            logging.info("No artists missing descriptions.")
            return
            
        print(f"\n🔍 Analyzing {len(missing_artists)} artists missing descriptions...")
        
        # 分类统计
        japanese_artists = []
        english_artists = []
        
        with_spotify_no_wiki = []
        with_wiki_no_spotify = []
        with_both = []
        with_neither = []
        
        for artist in missing_artists:
            name = artist["name"]
            has_spotify = bool(artist.get("spotify_id"))
            has_wiki = bool(artist.get("wiki_data"))
            
            # 按语言分类
            if self.is_japanese_artist(name):
                japanese_artists.append(artist)
            else:
                english_artists.append(artist)
            
            # 按数据源分类
            if has_spotify and not has_wiki:
                with_spotify_no_wiki.append(artist)
            elif has_wiki and not has_spotify:
                with_wiki_no_spotify.append(artist)
            elif has_spotify and has_wiki:
                with_both.append(artist)
            else:
                with_neither.append(artist)
        
        # 输出分析结果
        print(f"\n📊 Analysis Results:")
        print(f"  - Japanese artists: {len(japanese_artists)}")
        print(f"  - English artists: {len(english_artists)}")
        print(f"")
        print(f"  - Has Spotify but no Wiki: {len(with_spotify_no_wiki)}")
        print(f"  - Has Wiki but no Spotify: {len(with_wiki_no_spotify)}")
        print(f"  - Has both Spotify and Wiki: {len(with_both)}")
        print(f"  - Has neither: {len(with_neither)}")
        
        # 显示一些示例
        if with_spotify_no_wiki:
            print(f"\n🎵 Artists with Spotify but no Wiki ({len(with_spotify_no_wiki)}):")
            for i, artist in enumerate(with_spotify_no_wiki[:10], 1):
                print(f"  {i}. {artist['name']}")
            if len(with_spotify_no_wiki) > 10:
                print(f"  ... and {len(with_spotify_no_wiki) - 10} more")
        
        if with_wiki_no_spotify:
            print(f"\n📚 Artists with Wiki but no Spotify ({len(with_wiki_no_spotify)}):")
            for i, artist in enumerate(with_wiki_no_spotify[:10], 1):
                print(f"  {i}. {artist['name']}")
            if len(with_wiki_no_spotify) > 10:
                print(f"  ... and {len(with_wiki_no_spotify) - 10} more")
        
        if with_both:
            print(f"\n✅ Artists with both Spotify and Wiki ({len(with_both)}):")
            for i, artist in enumerate(with_both[:10], 1):
                print(f"  {i}. {artist['name']}")
            if len(with_both) > 10:
                print(f"  ... and {len(with_both) - 10} more")
        
        if with_neither:
            print(f"\n❌ Artists with neither Spotify nor Wiki ({len(with_neither)}):")
            for i, artist in enumerate(with_neither, 1):
                print(f"  {i}. {artist['name']}")
        
        # 建议下一步行动
        print(f"\n💡 Recommendations:")
        print(f"  1. Generate descriptions from Wiki data ({len(with_wiki_no_spotify)} artists)")
        print(f"  2. Generate descriptions from Spotify genres ({len(with_spotify_no_wiki)} artists)")
        print(f"  3. Generate descriptions from both sources ({len(with_both)} artists)")
        print(f"  4. Manual descriptions for artists with no data ({len(with_neither)} artists)")
        
        return {
            'with_spotify_no_wiki': with_spotify_no_wiki,
            'with_wiki_no_spotify': with_wiki_no_spotify,
            'with_both': with_both,
            'with_neither': with_neither
        }

async def main():
    analyzer = MissingDescriptionAnalyzer()
    await analyzer.analyze_missing_descriptions()

if __name__ == "__main__":
    asyncio.run(main()) 