import asyncio
import logging
import sys
import httpx
import urllib.parse
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_wiki_search():
    """测试Wikipedia搜索功能"""
    
    # 测试艺术家列表
    test_artists = [
        "Four Tet",
        "FRED AGAIN..",
        "BRAHMAN", 
        "LAUSBUB",
        "ROUTE 17 Rock'n'Roll ORCHESTRA"
    ]
    
    # Wikipedia API endpoints
    wiki_apis = {
        "zh": "https://zh.wikipedia.org/api/rest_v1",
        "en": "https://en.wikipedia.org/api/rest_v1", 
        "ja": "https://ja.wikipedia.org/api/rest_v1"
    }
    
    print("🧪 Testing Wikipedia Search for Known Artists")
    print("="*60)
    
    for artist_name in test_artists:
        print(f"\n🔍 Testing: {artist_name}")
        
        for language, api_url in wiki_apis.items():
            # URL编码搜索词
            encoded_name = urllib.parse.quote(artist_name)
            search_url = f"{api_url}/page/summary/{encoded_name}"
            
            print(f"  🌐 Trying {language} Wiki: {search_url}")
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(search_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        title = data.get("title", "")
                        extract = data.get("extract", "")
                        print(f"    ✅ FOUND! Title: {title}")
                        print(f"    📝 Extract: {extract[:100]}...")
                        break  # 找到就停止搜索其他语言
                    else:
                        print(f"    ❌ Status: {response.status_code}")
                        
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            # 避免请求过于频繁
            await asyncio.sleep(0.5)
        
        print("-" * 40)

async def test_alternative_search():
    """测试替代搜索方法"""
    
    print("\n🔄 Testing Alternative Search Methods")
    print("="*60)
    
    # 测试不同的搜索变体
    artist_name = "Four Tet"
    search_variations = [
        "Four Tet",
        "Four_Tet", 
        "Fourtet",
        "Four Tet (musician)",
        "Four Tet (artist)"
    ]
    
    api_url = "https://en.wikipedia.org/api/rest_v1"
    
    for variation in search_variations:
        encoded_name = urllib.parse.quote(variation)
        search_url = f"{api_url}/page/summary/{encoded_name}"
        
        print(f"\n🔍 Trying variation: '{variation}'")
        print(f"  URL: {search_url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    data = response.json()
                    title = data.get("title", "")
                    print(f"    ✅ SUCCESS! Title: {title}")
                    break
                else:
                    print(f"    ❌ Status: {response.status_code}")
                    
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        await asyncio.sleep(0.5)

async def main():
    await test_wiki_search()
    await test_alternative_search()

if __name__ == "__main__":
    asyncio.run(main()) 