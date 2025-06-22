import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def analyze_missing_wiki():
    """分析没有Wiki数据的艺术家，找出搜索失败的原因"""
    logging.info("=== Missing Wiki Data Analysis ===")
    
    try:
        # 获取所有艺术家
        all_artists_response = artist_db_service.db.supabase.table("artists").select(
            "id, name, wiki_extract, spotify_id, genres"
        ).execute()
        
        if not all_artists_response.data:
            logging.error("Could not fetch artists from database.")
            return
        
        # 分离有Wiki和没有Wiki的艺术家
        artists_with_wiki = [a for a in all_artists_response.data if a.get("wiki_extract")]
        artists_without_wiki = [a for a in all_artists_response.data if not a.get("wiki_extract")]
        
        logging.info(f"📊 Total artists: {len(all_artists_response.data)}")
        logging.info(f"📚 Artists with Wiki: {len(artists_with_wiki)}")
        logging.info(f"❌ Artists without Wiki: {len(artists_without_wiki)}")
        
        # 分析没有Wiki数据的艺术家特征
        print("\n" + "="*80)
        print("🔍 ANALYSIS OF ARTISTS WITHOUT WIKI DATA")
        print("="*80)
        
        # 1. 检查Spotify数据情况
        artists_with_spotify = [a for a in artists_without_wiki if a.get("spotify_id")]
        artists_without_spotify = [a for a in artists_without_wiki if not a.get("spotify_id")]
        
        print(f"\n🎵 Spotify Data Analysis:")
        print(f"   Artists with Spotify ID: {len(artists_with_spotify)}")
        print(f"   Artists without Spotify ID: {len(artists_without_spotify)}")
        
        # 2. 分析名称特征
        print(f"\n📝 Name Analysis:")
        
        # 检查日文名称
        japanese_names = []
        english_names = []
        mixed_names = []
        
        for artist in artists_without_wiki:
            name = artist["name"]
            has_japanese = any(ord(char) > 127 for char in name if char.isalpha())
            has_english = any(char.isascii() and char.isalpha() for char in name)
            
            if has_japanese and has_english:
                mixed_names.append(name)
            elif has_japanese:
                japanese_names.append(name)
            else:
                english_names.append(name)
        
        print(f"   Japanese names: {len(japanese_names)}")
        print(f"   English names: {len(english_names)}")
        print(f"   Mixed names: {len(mixed_names)}")
        
        # 3. 检查特殊字符
        special_char_names = []
        for artist in artists_without_wiki:
            name = artist["name"]
            if any(char in name for char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']):
                special_char_names.append(name)
        
        print(f"   Names with special characters: {len(special_char_names)}")
        
        # 4. 检查名称长度
        short_names = [a["name"] for a in artists_without_wiki if len(a["name"]) <= 3]
        long_names = [a["name"] for a in artists_without_wiki if len(a["name"]) > 20]
        
        print(f"   Very short names (≤3 chars): {len(short_names)}")
        print(f"   Very long names (>20 chars): {len(long_names)}")
        
        # 5. 显示具体例子
        print(f"\n📋 EXAMPLES BY CATEGORY:")
        
        if japanese_names:
            print(f"\n🇯🇵 Japanese names (first 10):")
            for i, name in enumerate(japanese_names[:10], 1):
                spotify_status = "🎵" if any(a["name"] == name and a.get("spotify_id") for a in artists_without_wiki) else "❌"
                print(f"  {i:2d}. {name} {spotify_status}")
        
        if english_names:
            print(f"\n🇺🇸 English names (first 10):")
            for i, name in enumerate(english_names[:10], 1):
                spotify_status = "🎵" if any(a["name"] == name and a.get("spotify_id") for a in artists_without_wiki) else "❌"
                print(f"  {i:2d}. {name} {spotify_status}")
        
        if mixed_names:
            print(f"\n🌍 Mixed names (first 10):")
            for i, name in enumerate(mixed_names[:10], 1):
                spotify_status = "🎵" if any(a["name"] == name and a.get("spotify_id") for a in artists_without_wiki) else "❌"
                print(f"  {i:2d}. {name} {spotify_status}")
        
        if special_char_names:
            print(f"\n🔤 Names with special characters (first 10):")
            for i, name in enumerate(special_char_names[:10], 1):
                spotify_status = "🎵" if any(a["name"] == name and a.get("spotify_id") for a in artists_without_wiki) else "❌"
                print(f"  {i:2d}. {name} {spotify_status}")
        
        # 6. 检查Spotify名称vs数据库名称
        print(f"\n🔄 Spotify Name vs Database Name Analysis:")
        print(f"   Note: spotify_name column not available in database")
        print(f"   Cannot compare database names with Spotify official names")
        
        # 7. 建议改进策略
        print(f"\n" + "="*80)
        print("💡 RECOMMENDATIONS FOR WIKI SEARCH IMPROVEMENT")
        print("="*80)
        
        print(f"\n🔍 Search Strategy Improvements:")
        print(f"1. Use Spotify official names for Wikipedia search")
        print(f"2. Try multiple search variations (original name, Spotify name, etc.)")
        print(f"3. Handle special characters in names")
        print(f"4. Use different language Wikipedia versions (en, ja, zh)")
        print(f"5. Implement fuzzy matching for similar names")
        
        print(f"\n📊 Priority Groups:")
        print(f"1. Artists with Spotify data but no Wiki: {len(artists_with_spotify)}")
        print(f"2. Artists without Spotify data: {len(artists_without_spotify)}")
        
        print(f"\n🎯 Immediate Actions:")
        print(f"1. Test Wikipedia search with Spotify official names")
        print(f"2. Create a script to search multiple Wikipedia language versions")
        print(f"3. Implement fallback search strategies")
        
        print("="*80)
        
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        raise

async def main():
    await analyze_missing_wiki()

if __name__ == "__main__":
    asyncio.run(main()) 