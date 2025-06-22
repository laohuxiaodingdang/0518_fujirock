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

async def debug_radwimps_search():
    """专门调试RADWIMPS的搜索问题"""
    
    print("🔍 Debugging RADWIMPS Wikipedia Search")
    print("="*60)
    
    # 测试不同的搜索变体
    search_variations = [
        "RADWIMPS",           # 数据库中的原始名称
        "Radwimps",           # Wikipedia中的正确名称
        "radwimps",           # 小写
        "RADWIMPS (band)",    # 带后缀
        "Radwimps (band)",    # 正确名称带后缀
    ]
    
    api_url = "https://en.wikipedia.org/api/rest_v1"
    
    for variation in search_variations:
        # URL编码搜索词
        encoded_name = urllib.parse.quote(variation)
        search_url = f"{api_url}/page/summary/{encoded_name}"
        
        print(f"\n🔍 Testing: '{variation}'")
        print(f"  URL: {search_url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(search_url)
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    title = data.get("title", "")
                    extract = data.get("extract", "")
                    print(f"    ✅ SUCCESS! Title: {title}")
                    print(f"    📝 Extract: {extract[:150]}...")
                    return True  # 找到就返回
                else:
                    print(f"    ❌ Not found")
                    
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        await asyncio.sleep(0.5)
    
    return False

async def test_other_languages():
    """测试其他语言版本的RADWIMPS"""
    
    print("\n🌐 Testing RADWIMPS in other languages")
    print("="*60)
    
    search_term = "Radwimps"  # 使用正确的Wikipedia名称
    
    wiki_apis = {
        "zh": "https://zh.wikipedia.org/api/rest_v1",
        "en": "https://en.wikipedia.org/api/rest_v1", 
        "ja": "https://ja.wikipedia.org/api/rest_v1"
    }
    
    for language, api_url in wiki_apis.items():
        encoded_name = urllib.parse.quote(search_term)
        search_url = f"{api_url}/page/summary/{encoded_name}"
        
        print(f"\n🔍 Testing {language} Wiki: {search_url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    data = response.json()
                    title = data.get("title", "")
                    extract = data.get("extract", "")
                    print(f"    ✅ FOUND! Title: {title}")
                    print(f"    📝 Extract: {extract[:100]}...")
                else:
                    print(f"    ❌ Status: {response.status_code}")
                    
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        await asyncio.sleep(0.5)

async def main():
    # 先测试英文搜索
    found = await debug_radwimps_search()
    
    if not found:
        print("\n❌ RADWIMPS not found in English Wikipedia!")
        print("This is strange since it should exist...")
    
    # 测试其他语言
    await test_other_languages()

if __name__ == "__main__":
    asyncio.run(main()) 