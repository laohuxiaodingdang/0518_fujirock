#!/usr/bin/env python3
"""
调试数据库更新问题的脚本
"""
import asyncio
import os
import httpx
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_supabase_client() -> Client:
    """获取Supabase客户端"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials")
    
    return create_client(url, key)

async def test_wikipedia_search(artist_name: str):
    """测试Wikipedia搜索"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            search_url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{artist_name}"
            headers = {
                "User-Agent": "FujiRock2025API/1.0 (https://github.com/example/fujirock)"
            }
            
            print(f"🔍 搜索Wikipedia: {search_url}")
            response = await client.get(search_url, headers=headers)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   找到页面: {data.get('title', 'Unknown')}")
                if data.get("extract"):
                    print(f"   摘要: {data['extract'][:100]}...")
                    return {
                        "extract": data["extract"],
                        "title": data.get("title", artist_name),
                        "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else ""
                    }
                else:
                    print("   没有找到摘要内容")
            else:
                print(f"   搜索失败: {response.text}")
            
            return None
            
    except Exception as e:
        print(f"   Wikipedia搜索错误: {str(e)}")
        return None

async def test_database_update(supabase: Client, artist_id: str, test_data: dict):
    """测试数据库更新"""
    try:
        print(f"🔧 测试更新艺术家 {artist_id}")
        print(f"   更新数据: {test_data}")
        
        # 尝试更新
        result = supabase.table("artists").update(test_data).eq("id", artist_id).execute()
        
        print(f"   返回结果: {result}")
        print(f"   数据: {result.data}")
        print(f"   错误: {getattr(result, 'error', None)}")
        
        if result.data:
            print("   ✅ 更新成功")
            return True
        else:
            print("   ❌ 更新失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 更新异常: {str(e)}")
        print(f"   异常类型: {type(e)}")
        if hasattr(e, '__dict__'):
            print(f"   异常详情: {e.__dict__}")
        return False

async def main():
    """主函数"""
    try:
        supabase = get_supabase_client()
        
        # 获取一个缺失数据的艺术家进行测试
        print("🔍 获取测试艺术家...")
        response = supabase.table("artists").select("*").eq("name", "ROUTE 17 Rock'n'Roll ORCHESTRA").execute()
        
        if not response.data:
            print("❌ 找不到测试艺术家")
            return
        
        artist = response.data[0]
        artist_id = artist["id"]
        artist_name = artist["name"]
        
        print(f"✅ 找到艺术家: {artist_name}")
        print(f"   ID: {artist_id}")
        print(f"   当前wiki_extract: {artist.get('wiki_extract', 'None')}")
        print(f"   当前image_url: {artist.get('image_url', 'None')}")
        print()
        
        # 测试Wikipedia搜索
        print("📝 测试Wikipedia搜索...")
        wiki_data = await test_wikipedia_search(artist_name)
        print()
        
        # 测试简单的数据库更新
        print("🔧 测试简单更新...")
        simple_update = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await test_database_update(supabase, artist_id, simple_update)
        print()
        
        # 测试wiki数据更新
        if wiki_data:
            print("🔧 测试Wiki数据更新...")
            wiki_update = {
                "wiki_extract": wiki_data["extract"],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await test_database_update(supabase, artist_id, wiki_update)
            print()
        
        # 测试完整数据更新
        print("🔧 测试完整数据更新...")
        full_update = {}
        
        if wiki_data:
            current_time = datetime.now(timezone.utc).isoformat()
            full_update.update({
                "wiki_extract": wiki_data["extract"],
                "wiki_data": wiki_data,
                "wiki_last_updated": current_time,
                "updated_at": current_time
            })
        
        if wiki_data and wiki_data.get("thumbnail"):
            full_update["image_url"] = wiki_data["thumbnail"]
        
        if full_update:
            await test_database_update(supabase, artist_id, full_update)
        else:
            print("   没有数据可更新")
        
    except Exception as e:
        print(f"❌ 主函数错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 