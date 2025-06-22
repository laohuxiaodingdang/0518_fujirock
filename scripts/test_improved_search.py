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

async def test_improved_search():
    """测试改进后的搜索策略"""
    
    searcher = ImprovedWikiSearcher()
    
    # 测试之前失败的艺术家
    test_artists = [
        {
            "id": "test-1",
            "name": "FRED AGAIN..",
            "spotify_id": None,
            "genres": []
        },
        {
            "id": "test-2", 
            "name": "LAUSBUB",
            "spotify_id": None,
            "genres": []
        },
        {
            "id": "test-3",
            "name": "ROUTE 17 Rock'n'Roll ORCHESTRA",
            "spotify_id": None,
            "genres": []
        },
        {
            "id": "test-4",
            "name": "FOUR TET",  # 测试大小写问题
            "spotify_id": None,
            "genres": []
        }
    ]
    
    print("🧪 Testing Improved Wiki Search Strategy")
    print("="*60)
    
    for i, artist in enumerate(test_artists, 1):
        print(f"\n[{i}/{len(test_artists)}] Testing: {artist['name']}")
        print("-" * 40)
        
        result = await searcher.search_artist_wiki(artist)
        
        if result:
            print(f"✅ SUCCESS! Found Wiki data:")
            print(f"   Language: {result['language']}")
            print(f"   Title: {result['title']}")
            print(f"   Extract: {result['extract'][:150]}...")
        else:
            print(f"❌ No Wiki data found")
        
        await asyncio.sleep(1)  # 避免请求过于频繁

async def main():
    await test_improved_search()

if __name__ == "__main__":
    asyncio.run(main()) 