#!/usr/bin/env python3
"""
批量修复艺术家数据脚本 V2 - 改进版本
处理Wikipedia搜索失败的情况，并尝试多种搜索策略
"""
import asyncio
import os
import httpx
import json
import urllib.parse
from typing import Optional, Dict, Any
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

async def search_wikipedia_enhanced(artist_name: str) -> Optional[Dict[str, Any]]:
    """增强的Wikipedia搜索，尝试多种策略"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "User-Agent": "FujiRock2025API/1.0 (https://github.com/example/fujirock)"
            }
            
            # 策略1: 直接搜索艺术家名称
            search_url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(artist_name)}"
            print(f"      尝试直接搜索: {artist_name}")
            
            response = await client.get(search_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("extract") and len(data["extract"].strip()) > 20:
                    print(f"      ✅ 直接搜索成功")
                    return {
                        "extract": data["extract"],
                        "title": data.get("title", artist_name),
                        "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else ""
                    }
            
            # 策略2: 使用搜索API
            print(f"      尝试搜索API")
            search_api_url = "https://zh.wikipedia.org/api/rest_v1/page/search"
            search_response = await client.get(
                search_api_url,
                params={"q": artist_name, "limit": 3},
                headers=headers
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data.get("pages"):
                    for page in search_data["pages"][:2]:  # 尝试前2个结果
                        page_title = page["title"]
                        print(f"      尝试页面: {page_title}")
                        
                        detail_url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_title)}"
                        detail_response = await client.get(detail_url, headers=headers)
                        
                        if detail_response.status_code == 200:
                            data = detail_response.json()
                            if data.get("extract") and len(data["extract"].strip()) > 20:
                                print(f"      ✅ 搜索API成功: {page_title}")
                                return {
                                    "extract": data["extract"],
                                    "title": data.get("title", page_title),
                                    "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                                    "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else ""
                                }
            
            # 策略3: 尝试英文Wikipedia
            print(f"      尝试英文Wikipedia")
            en_search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(artist_name)}"
            en_response = await client.get(en_search_url, headers=headers)
            
            if en_response.status_code == 200:
                data = en_response.json()
                if data.get("extract") and len(data["extract"].strip()) > 20:
                    print(f"      ✅ 英文Wikipedia成功")
                    return {
                        "extract": data["extract"],
                        "title": data.get("title", artist_name),
                        "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else ""
                    }
            
            print(f"      ❌ 所有Wikipedia搜索策略都失败")
            return None
            
    except Exception as e:
        print(f"      Wikipedia搜索错误: {str(e)}")
        return None

async def get_spotify_artist_image(spotify_id: str) -> Optional[str]:
    """从Spotify获取艺术家图片 - 需要实现Spotify API调用"""
    # 这里需要实现Spotify API调用
    # 暂时返回None，但保留接口供后续实现
    return None

async def update_artist_data_v2(supabase: Client, artist_id: str, wiki_data: Dict[str, Any] = None, image_url: str = None, mark_attempted: bool = False):
    """更新艺术家数据到数据库 - 改进版本"""
    try:
        update_data = {}
        current_time = datetime.now(timezone.utc).isoformat()
        
        if wiki_data:
            update_data.update({
                "wiki_extract": wiki_data["extract"],
                "wiki_data": wiki_data,
                "wiki_last_updated": current_time
            })
        
        if image_url:
            update_data["image_url"] = image_url
        
        # 如果标记为已尝试但失败，记录尝试时间
        if mark_attempted and not wiki_data:
            update_data["wiki_last_updated"] = current_time
        
        # 总是更新 updated_at
        update_data["updated_at"] = current_time
        
        if update_data:
            result = supabase.table("artists").update(update_data).eq("id", artist_id).execute()
            return result.data is not None
        
        return False
        
    except Exception as e:
        print(f"      数据库更新错误: {str(e)}")
        return False

async def fix_artist_missing_both_v2(supabase: Client, artist: Dict[str, Any]):
    """修复缺失wiki和image的艺术家 - 改进版本"""
    name = artist["name"]
    artist_id = artist["id"]
    spotify_id = artist.get("spotify_id")
    
    print(f"🔧 修复艺术家: {name}")
    
    # 获取Wikipedia数据
    wiki_data = await search_wikipedia_enhanced(name)
    
    # 从Wikipedia获取图片（如果有）
    image_url = None
    if wiki_data and wiki_data.get("thumbnail"):
        image_url = wiki_data["thumbnail"]
        print(f"      🖼️  从Wikipedia获取图片")
    
    # 如果Wikipedia没有图片，尝试从Spotify获取
    if not image_url and spotify_id:
        print(f"      尝试从Spotify获取图片")
        spotify_image = await get_spotify_artist_image(spotify_id)
        if spotify_image:
            image_url = spotify_image
            print(f"      🖼️  从Spotify获取图片")
    
    # 显示获取到的数据
    if wiki_data:
        print(f"      📝 Wiki: {wiki_data['extract'][:80]}...")
    else:
        print(f"      📝 Wiki: 未找到")
    
    if image_url:
        print(f"      🖼️  Image: {image_url[:80]}...")
    else:
        print(f"      🖼️  Image: 未找到")
    
    # 更新数据库 - 即使没有找到数据也要标记尝试过
    success = await update_artist_data_v2(
        supabase, 
        artist_id, 
        wiki_data, 
        image_url, 
        mark_attempted=True
    )
    
    if success:
        wiki_status = "✅" if wiki_data else "🔍"
        image_status = "✅" if image_url else "🔍"
        print(f"      结果 - Wiki: {wiki_status}, Image: {image_status}")
    else:
        print(f"      ❌ 数据库更新失败")
    
    return success

async def fix_artist_missing_wiki_v2(supabase: Client, artist: Dict[str, Any]):
    """修复只缺少wiki的艺术家 - 改进版本"""
    name = artist["name"]
    artist_id = artist["id"]
    
    print(f"📝 获取Wiki: {name}")
    
    # 获取Wikipedia数据
    wiki_data = await search_wikipedia_enhanced(name)
    
    if wiki_data:
        print(f"      📝 Wiki: {wiki_data['extract'][:80]}...")
    else:
        print(f"      📝 Wiki: 未找到")
    
    # 更新数据库
    success = await update_artist_data_v2(
        supabase, 
        artist_id, 
        wiki_data=wiki_data, 
        mark_attempted=True
    )
    
    if success:
        status = "✅" if wiki_data else "🔍"
        print(f"      结果 - Wiki: {status}")
    else:
        print(f"      ❌ 数据库更新失败")
    
    return success

async def main():
    """主函数"""
    try:
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
        
        # 修复缺失两种数据的艺术家（优先级最高）
        if missing_both:
            print("🚨 修复缺失两种数据的艺术家:")
            success_count = 0
            for i, artist in enumerate(missing_both):
                print(f"   [{i+1}/{len(missing_both)}]", end=" ")
                success = await fix_artist_missing_both_v2(supabase, artist)
                if success:
                    success_count += 1
                await asyncio.sleep(2)  # 避免请求过于频繁
                print()
            print(f"   完成: {success_count}/{len(missing_both)} 成功")
            print()
        
        # 修复只缺少wiki的艺术家（前5个）
        if missing_wiki:
            print("📝 修复缺少wiki的艺术家（前5个）:")
            success_count = 0
            for i, artist in enumerate(missing_wiki[:5]):
                print(f"   [{i+1}/5]", end=" ")
                success = await fix_artist_missing_wiki_v2(supabase, artist)
                if success:
                    success_count += 1
                await asyncio.sleep(2)  # 避免请求过于频繁
                print()
            print(f"   完成: {success_count}/5 成功")
            print()
        
        print("=" * 60)
        print("✅ 修复完成！")
        print("📊 运行 python check_artists_data.py 查看更新后的状态")
        print("🔄 如需继续修复更多艺术家，可再次运行此脚本")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    asyncio.run(main()) 