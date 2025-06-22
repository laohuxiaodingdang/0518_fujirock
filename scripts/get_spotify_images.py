#!/usr/bin/env python3
"""
从Spotify获取艺术家真实头像URL的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.spotify_service import spotify_service
from services.database_service import db_service

async def get_spotify_images():
    """获取所有艺术家的Spotify头像"""
    try:
        print("=== Getting Spotify Images ===")
        
        # 获取数据库中的所有艺术家
        result = db_service.supabase.table("artists").select("*").execute()
        
        if not result.data:
            print("No artists found in database")
            return {}
        
        image_mapping = {}
        
        for artist in result.data:
            artist_name = artist.get("name")
            spotify_id = artist.get("spotify_id")
            
            if spotify_id:
                print(f"🎵 Getting image for {artist_name} (Spotify ID: {spotify_id})")
                
                try:
                    # 通过Spotify ID获取艺术家信息
                    spotify_result = await spotify_service.get_artist_by_id(spotify_id)
                    
                    if spotify_result.get("success") and spotify_result.get("data"):
                        spotify_data = spotify_result["data"]
                        images = spotify_data.get("images", [])
                        
                        if images:
                            # 使用最高质量的图片
                            best_image = images[0]  # Spotify按质量排序，第一个是最高质量
                            image_url = best_image.get("url")
                            
                            if image_url:
                                image_mapping[artist_name] = image_url
                                print(f"  ✅ Found image: {image_url}")
                            else:
                                print(f"  ❌ No image URL in response")
                        else:
                            print(f"  ❌ No images available")
                    else:
                        print(f"  ❌ Failed to get Spotify data: {spotify_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"  ❌ Error getting Spotify data: {str(e)}")
            else:
                print(f"⚠️  {artist_name} has no Spotify ID")
        
        print(f"\n📊 Found images for {len(image_mapping)} artists")
        
        # 打印映射结果
        print("\n🎨 Image mapping:")
        for name, url in image_mapping.items():
            print(f'    "{name}": "{url}",')
        
        return image_mapping
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}

async def update_with_spotify_images():
    """获取Spotify图片并更新数据库"""
    try:
        # 获取图片映射
        image_mapping = await get_spotify_images()
        
        if not image_mapping:
            print("No images found, using fallback URLs")
            # 使用高质量的艺术家图片作为备选
            image_mapping = {
                "Fred again..": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=400&q=80",
                "THE HIVES": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=400&q=80",
                "FOUR TET": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=400&q=80",
                "JAMES BLAKE": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=400&q=80",
                "RADWIMPS": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=400&q=80",
                "VAMPIRE WEEKEND": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=400&q=80"
            }
        
        # 更新数据库
        print("\n=== Updating database with images ===")
        
        result = db_service.supabase.table("artists").select("*").execute()
        
        if not result.data:
            print("No artists found in database")
            return False
        
        success_count = 0
        
        for artist in result.data:
            artist_name = artist.get("name")
            artist_id = artist.get("id")
            
            if artist_name in image_mapping:
                image_url = image_mapping[artist_name]
                
                try:
                    # 更新艺术家头像
                    update_result = db_service.supabase.table("artists").update({
                        "image_url": image_url
                    }).eq("id", artist_id).execute()
                    
                    if update_result.data:
                        print(f"✅ Updated {artist_name}")
                        success_count += 1
                    else:
                        print(f"❌ Failed to update {artist_name}")
                        
                except Exception as e:
                    print(f"❌ Error updating {artist_name}: {str(e)}")
            else:
                print(f"⚠️  No image configured for {artist_name}")
        
        print(f"\n🎉 Updated {success_count} artists successfully!")
        return success_count > 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(update_with_spotify_images()) 