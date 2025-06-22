#!/usr/bin/env python3
"""
检查 artists 表结构和数据
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import asyncio
sys.path.append('.')

from services.database_service import db_service

async def check_table():
    """检查表结构和数据"""
    if not db_service.is_connected():
        print("❌ 数据库未连接")
        return
    
    try:
        # 查看当前数据
        result = db_service.supabase.table('artists').select('*').limit(3).execute()
        
        print("📊 当前 artists 表数据示例:")
        print("=" * 80)
        
        for i, item in enumerate(result.data, 1):
            print(f"\n🎤 艺术家 {i}: {item.get('name')}")
            print(f"   ID: {item.get('id')}")
            print(f"   Spotify ID: {item.get('spotify_id')}")
            print(f"   Name ZH: {item.get('name_zh')}")
            print(f"   Name EN: {item.get('name_en')}")
            print(f"   Name JA: {item.get('name_ja')}")
            print(f"   Popularity: {item.get('popularity')}")
            print(f"   Followers: {item.get('followers_count')}")
            print(f"   Image URL: {item.get('image_url')}")
            print(f"   External URLs: {item.get('external_urls')}")
            print(f"   Has Spotify Data: {'是' if item.get('spotify_data') else '否'}")
            print(f"   Has Images: {'是' if item.get('images') else '否'}")
            
        print(f"\n📈 总记录数: {len(result.data)}")
        
        # 检查 spotify_data 中是否有 spotify_id
        if result.data:
            first_item = result.data[0]
            spotify_data = first_item.get('spotify_data')
            if spotify_data:
                print(f"\n🔍 Spotify Data 示例结构:")
                print(f"   包含的字段: {list(spotify_data.keys()) if isinstance(spotify_data, dict) else 'Not a dict'}")
                if isinstance(spotify_data, dict) and 'id' in spotify_data:
                    print(f"   Spotify ID 在 spotify_data 中: {spotify_data['id']}")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    asyncio.run(check_table()) 