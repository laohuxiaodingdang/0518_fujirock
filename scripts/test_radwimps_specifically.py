import asyncio
import logging
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from scripts.improved_wiki_search import ImprovedWikiSearcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_radwimps_specifically():
    """专门测试RADWIMPS的搜索"""
    
    searcher = ImprovedWikiSearcher()
    
    # 测试RADWIMPS
    test_artist = {
        "id": "test-radwimps",
        "name": "RADWIMPS",
        "spotify_id": None,
        "genres": []
    }
    
    print("🧪 Testing RADWIMPS specifically with improved search")
    print("="*60)
    
    result = await searcher.search_artist_wiki(test_artist)
    
    if result:
        print(f"✅ SUCCESS! Found Wiki data for RADWIMPS:")
        print(f"   Language: {result['language']}")
        print(f"   Title: {result['title']}")
        print(f"   Extract: {result['extract'][:200]}...")
        
        # 测试数据库更新
        print(f"\n🔧 Testing database update...")
        success = await searcher.update_artist_wiki("test-radwimps", result)
        if success:
            print("✅ Database update successful!")
        else:
            print("❌ Database update failed!")
    else:
        print("❌ FAILED to find Wiki data for RADWIMPS")

async def main():
    await test_radwimps_specifically()

if __name__ == "__main__":
    asyncio.run(main()) 