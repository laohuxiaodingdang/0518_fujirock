#!/usr/bin/env python3
"""
检查数据库中艺术家的wiki和image_url缺失情况
"""
import asyncio
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_supabase_client() -> Client:
    """获取Supabase客户端"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials")
    
    return create_client(url, key)

async def check_artists_data():
    """检查艺术家数据缺失情况"""
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
        good_data = []
        
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
                missing_both.append({
                    'name': name,
                    'id': artist.get('id'),
                    'spotify_id': artist.get('spotify_id'),
                    'image_url': image_url
                })
            elif not has_wiki:
                missing_wiki.append({
                    'name': name,
                    'id': artist.get('id'),
                    'spotify_id': artist.get('spotify_id'),
                    'image_url': image_url
                })
            elif not has_image:
                missing_image.append({
                    'name': name,
                    'id': artist.get('id'),
                    'spotify_id': artist.get('spotify_id'),
                    'image_url': image_url
                })
            else:
                good_data.append({
                    'name': name,
                    'id': artist.get('id')
                })
        
        # 显示统计结果
        print(f"✅ Artists with complete data: {len(good_data)}")
        print(f"❌ Missing both wiki and image: {len(missing_both)}")
        print(f"📝 Missing wiki only: {len(missing_wiki)}")
        print(f"🖼️  Missing image only: {len(missing_image)}")
        print()
        
        # 显示缺失两种数据的艺术家
        if missing_both:
            print("🚨 Artists missing BOTH wiki and image:")
            for i, artist in enumerate(missing_both[:15]):  # 显示前15个
                print(f"  {i+1:2d}. {artist['name']}")
                if artist['spotify_id']:
                    print(f"      Spotify ID: {artist['spotify_id']}")
                if artist['image_url']:
                    print(f"      Current image: {artist['image_url'][:80]}...")
                print()
            if len(missing_both) > 15:
                print(f"      ... and {len(missing_both) - 15} more")
            print()
        
        # 显示只缺少wiki的艺术家
        if missing_wiki:
            print("📝 Artists missing wiki only:")
            for i, artist in enumerate(missing_wiki[:10]):  # 显示前10个
                print(f"  {i+1:2d}. {artist['name']}")
                if artist['spotify_id']:
                    print(f"      Spotify ID: {artist['spotify_id']}")
            if len(missing_wiki) > 10:
                print(f"      ... and {len(missing_wiki) - 10} more")
            print()
        
        # 显示只缺少image的艺术家
        if missing_image:
            print("🖼️  Artists missing image only:")
            for i, artist in enumerate(missing_image[:10]):  # 显示前10个
                print(f"  {i+1:2d}. {artist['name']}")
                if artist['spotify_id']:
                    print(f"      Spotify ID: {artist['spotify_id']}")
                if artist['image_url']:
                    print(f"      Current image: {artist['image_url'][:80]}...")
            if len(missing_image) > 10:
                print(f"      ... and {len(missing_image) - 10} more")
            print()
        
        print("=" * 60)
        print("建议的修复优先级:")
        print("1. 优先修复缺失两种数据的艺术家")
        print("2. 然后修复只缺少wiki的艺术家")
        print("3. 最后修复只缺少image的艺术家")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    asyncio.run(check_artists_data()) 