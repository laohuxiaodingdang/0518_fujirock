import asyncio
import logging
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def quick_check():
    """快速检查数据库状态"""
    try:
        logging.info("Quick database status check...")
        
        # 获取所有艺术家
        response = artist_db_service.db.supabase.table("artists").select(
            "name, wiki_data, wiki_extract, spotify_id, description"
        ).execute()
        
        if not response.data:
            logging.error("No data found")
            return
            
        artists = response.data
        total = len(artists)
        
        # 统计各字段的覆盖率
        with_wiki_data = sum(1 for a in artists if a.get('wiki_data'))
        with_wiki_extract = sum(1 for a in artists if a.get('wiki_extract'))
        with_spotify_id = sum(1 for a in artists if a.get('spotify_id'))
        with_description = sum(1 for a in artists if a.get('description'))
        
        print(f"\n📊 Database Status Summary")
        print(f"Total Artists: {total}")
        print(f"")
        print(f"📚 Wiki Data: {with_wiki_data}/{total} ({with_wiki_data/total*100:.1f}%)")
        print(f"📖 Wiki Extract: {with_wiki_extract}/{total} ({with_wiki_extract/total*100:.1f}%)")
        print(f"🎵 Spotify ID: {with_spotify_id}/{total} ({with_spotify_id/total*100:.1f}%)")
        print(f"📝 Description: {with_description}/{total} ({with_description/total*100:.1f}%)")
        
        # 检查缺失情况
        missing_wiki = total - with_wiki_data
        missing_description = total - with_description
        
        print(f"\n❌ Missing Data:")
        print(f"  - Wiki Data: {missing_wiki} artists")
        print(f"  - Description: {missing_description} artists")
        
        # 检查有Spotify但没有Wiki的
        with_spotify_no_wiki = sum(1 for a in artists if a.get('spotify_id') and not a.get('wiki_data'))
        print(f"  - Has Spotify but no Wiki: {with_spotify_no_wiki} artists")
        
    except Exception as e:
        logging.error(f"Error during quick check: {e}")

if __name__ == "__main__":
    asyncio.run(quick_check()) 