#!/usr/bin/env python3
"""
列出数据库中所有艺术家的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.artist_db_service import artist_db_service

async def list_artists():
    """列出所有艺术家"""
    try:
        result = await artist_db_service.search_artists('', limit=50)
        if result.get('success') and result.get('data'):
            print('=== Current artists in database ===')
            for i, artist in enumerate(result['data'], 1):
                print(f'{i}. Name: {artist.get("name", "Unknown")}')
                print(f'   ID: {artist.get("id", "Unknown")}')
                print(f'   Spotify ID: {artist.get("spotify_id", "None")}')
                print(f'   Genres: {artist.get("genres", [])}')
                print(f'   Has image_url field: {"image_url" in artist}')
                if "image_url" in artist:
                    print(f'   Image URL: {artist.get("image_url", "None")}')
                print(f'   Description: {artist.get("description", "No description")[:100]}...')
                print()
        else:
            print('No artists found or error occurred:', result.get('error'))
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == "__main__":
    asyncio.run(list_artists()) 