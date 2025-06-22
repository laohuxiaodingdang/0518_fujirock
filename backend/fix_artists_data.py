#!/usr/bin/env python3
"""
批量修复艺术家数据脚本 - 自动获取缺失的wiki和image_url
"""
import asyncio
import os
import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_supabase_client() -> Client:
    """获取Supabase客户端"""
    url = os.getenv("SUPABASE_URL")
    # 使用 SERVICE_ROLE_KEY 而不是 ANON_KEY 来获得更高权限
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials")
    
    return create_client(url, key)

async def search_wikipedia(artist_name: str) -> Optional[Dict[str, Any]]:
    """搜索Wikipedia获取艺术家信息"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 首先搜索页面
            search_url = "https://zh.wikipedia.org/api/rest_v1/page/summary/" + artist_name
            headers = {
                "User-Agent": "FujiRock2025API/1.0 (https://github.com/example/fujirock)"
            }
            
            response = await client.get(search_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("extract"):
                    return {
                        "extract": data["extract"],
                        "title": data.get("title", artist_name),
                        "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else ""
                    }
            
            # 如果直接搜索失败，尝试搜索API
            search_api_url = "https://zh.wikipedia.org/api/rest_v1/page/search"
            search_response = await client.get(
                search_api_url,
                params={"q": artist_name, "limit": 1},
                headers=headers
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data.get("pages") and len(search_data["pages"]) > 0:
                    page_title = search_data["pages"][0]["title"]
                    # 再次获取页面详情
                    detail_url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{page_title}"
                    detail_response = await client.get(detail_url, headers=headers)
                    
                    if detail_response.status_code == 200:
                        data = detail_response.json()
                        if data.get("extract"):
                            return {
                                "extract": data["extract"],
                                "title": data.get("title", page_title),
                                "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                                "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else ""
                            }
            
            return None
            
    except Exception as e:
        print(f"Wikipedia search error for {artist_name}: {str(e)}")
        return None

async def get_spotify_image(spotify_id: str) -> Optional[str]:
    """从Spotify获取艺术家图片"""
    try:
        # 这里需要Spotify API token，暂时返回None
        # 实际实现需要先获取access token
        return None
    except Exception as e:
        print(f"Spotify image error for {spotify_id}: {str(e)}")
        return None

async def update_artist_data(supabase: Client, artist_id: str, wiki_data: Dict[str, Any] = None, image_url: str = None):
    """更新艺术家数据到数据库"""
    try:
        update_data = {}
        
        if wiki_data:
            # 使用正确的时间戳格式
            current_time = datetime.now(timezone.utc).isoformat()
            update_data.update({
                "wiki_extract": wiki_data["extract"],
                "wiki_data": wiki_data,
                "wiki_last_updated": current_time,
                "updated_at": current_time
            })
        
        if image_url:
            update_data["image_url"] = image_url
            if "updated_at" not in update_data:
                update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        if not update_data:
            return False
        
        print(f"      Updating with data: {list(update_data.keys())}")
        result = supabase.table("artists").update(update_data).eq("id", artist_id).execute()
        
        if result.data:
            return True
        else:
            print(f"      No data returned from update operation")
            return False
        
    except Exception as e:
        print(f"      Database update error: {str(e)}")
        # 尝试打印更详细的错误信息
        if hasattr(e, 'response'):
            print(f"      Response: {e.response}")
        return False

async def fix_artist_missing_both(supabase: Client, artist: Dict[str, Any]):
    """修复缺失wiki和image的艺术家"""
    name = artist["name"]
    artist_id = artist["id"]
    spotify_id = artist.get("spotify_id")
    
    print(f"🔧 修复艺术家: {name}")
    print(f"   Artist ID: {artist_id}")
    
    # 获取Wikipedia数据
    wiki_data = await search_wikipedia(name)
    
    # 从Wikipedia获取图片（如果有）
    image_url = None
    if wiki_data and wiki_data.get("thumbnail"):
        image_url = wiki_data["thumbnail"]
    
    # 如果Wikipedia没有图片，尝试从Spotify获取
    if not image_url and spotify_id:
        spotify_image = await get_spotify_image(spotify_id)
        if spotify_image:
            image_url = spotify_image
    
    # 显示获取到的数据
    if wiki_data:
        print(f"   📝 Wiki found: {wiki_data['extract'][:100]}...")
    if image_url:
        print(f"   🖼️  Image found: {image_url}")
    
    # 更新数据库
    success = await update_artist_data(supabase, artist_id, wiki_data, image_url)
    
    if success:
        wiki_status = "✅" if wiki_data else "❌"
        image_status = "✅" if image_url else "❌"
        print(f"   Result - Wiki: {wiki_status}, Image: {image_status}")
    else:
        print(f"   ❌ 数据库更新失败")
    
    return success

async def fix_artist_missing_wiki(supabase: Client, artist: Dict[str, Any]):
    """修复只缺少wiki的艺术家"""
    name = artist["name"]
    artist_id = artist["id"]
    
    print(f"📝 获取Wiki: {name}")
    print(f"   Artist ID: {artist_id}")
    
    # 获取Wikipedia数据
    wiki_data = await search_wikipedia(name)
    
    if wiki_data:
        print(f"   📝 Wiki found: {wiki_data['extract'][:100]}...")
    
    # 更新数据库
    success = await update_artist_data(supabase, artist_id, wiki_data=wiki_data)
    
    if success:
        status = "✅" if wiki_data else "❌"
        print(f"   Result - Wiki: {status}")
    else:
        print(f"   ❌ 数据库更新失败")
    
    return success

async def fix_artist_missing_image(supabase: Client, artist: Dict[str, Any]):
    """修复只缺少image的艺术家"""
    name = artist["name"]
    artist_id = artist["id"]
    spotify_id = artist.get("spotify_id")
    
    print(f"🖼️  获取图片: {name}")
    print(f"   Artist ID: {artist_id}")
    
    # 先尝试从Wikipedia获取图片
    wiki_data = await search_wikipedia(name)
    image_url = None
    
    if wiki_data and wiki_data.get("thumbnail"):
        image_url = wiki_data["thumbnail"]
    
    # 如果Wikipedia没有图片，尝试从Spotify获取
    if not image_url and spotify_id:
        spotify_image = await get_spotify_image(spotify_id)
        if spotify_image:
            image_url = spotify_image
    
    if image_url:
        print(f"   🖼️  Image found: {image_url}")
    
    # 更新数据库
    success = await update_artist_data(supabase, artist_id, image_url=image_url)
    
    if success:
        status = "✅" if image_url else "❌"
        print(f"   Result - Image: {status}")
    else:
        print(f"   ❌ 数据库更新失败")
    
    return success

async def test_database_connection():
    """测试数据库连接和权限"""
    try:
        supabase = get_supabase_client()
        
        # 尝试简单的查询
        result = supabase.table("artists").select("id, name").limit(1).execute()
        
        if result.data:
            print("✅ 数据库连接成功")
            
            # 尝试简单的更新操作
            test_artist_id = result.data[0]["id"]
            test_update = supabase.table("artists").update({"updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", test_artist_id).execute()
            
            if test_update.data:
                print("✅ 数据库更新权限正常")
                return True
            else:
                print("❌ 数据库更新权限不足")
                return False
        else:
            print("❌ 数据库查询失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {str(e)}")
        return False

async def main():
    """主函数"""
    try:
        # 首先测试数据库连接
        print("🔍 测试数据库连接...")
        if not await test_database_connection():
            print("数据库连接或权限有问题，请检查配置")
            return
        
        print()
        
        supabase = get_supabase_client()
        
        # 获取所有Fuji Rock艺术家
        response = supabase.table("artists").select("*").eq("is_fuji_rock_artist", True).execute()
        
        if not response.data:
            print("No Fuji Rock artists found in database")
            return
        
        artists = response.data
        print(f"Found {len(artists)} Fuji Rock artists in database")
        print("=" * 60)
        
        missing_wiki = []
        missing_image = []
        missing_both = []
        
        for artist in artists:
            name = artist.get('name', 'Unknown')
            wiki_extract = artist.get('wiki_extract')
            image_url = artist.get('image_url')
            
            # 检查wiki数据
            has_wiki = (wiki_extract and 
                       wiki_extract.strip() and 
                       wiki_extract.strip() != "" and
                       len(wiki_extract.strip()) > 10)
            
            # 检查image数据
            has_image = (image_url and 
                        image_url.strip() and 
                        image_url.strip() != "" and
                        "placeholder" not in image_url.lower() and
                        image_url != "https://via.placeholder.com/300x300?text=No+Image")
            
            if not has_wiki and not has_image:
                missing_both.append(artist)
            elif not has_wiki:
                missing_wiki.append(artist)
            elif not has_image:
                missing_image.append(artist)
        
        print(f"需要修复的艺术家: {len(missing_both) + len(missing_wiki) + len(missing_image)}")
        print(f"- 缺失两种数据: {len(missing_both)}")
        print(f"- 只缺少wiki: {len(missing_wiki)}")
        print(f"- 只缺少image: {len(missing_image)}")
        print()
        
        # 只修复缺失两种数据的艺术家（优先级最高，数量较少）
        if missing_both:
            print("🚨 修复缺失两种数据的艺术家:")
            for artist in missing_both:
                await fix_artist_missing_both(supabase, artist)
                await asyncio.sleep(2)  # 增加等待时间，避免请求过于频繁
                print()
        
        print("=" * 60)
        print("✅ 修复完成！请运行 python check_artists_data.py 查看更新后的状态")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    asyncio.run(main()) 