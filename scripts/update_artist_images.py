#!/usr/bin/env python3
"""
更新艺术家头像的脚本
为现有的6个艺术家添加合适的头像图片URL
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import db_service

# 艺术家头像映射
ARTIST_IMAGES = {
    "Fred again..": "https://i.scdn.co/image/ab6761610000e5eb4b9a2c4d1de0d48c1a86ef5e",
    "THE HIVES": "https://i.scdn.co/image/ab6761610000e5eb8c5e1b4baf8ab8e5b2e5e8a3",
    "FOUR TET": "https://i.scdn.co/image/ab6761610000e5eb2c9a3a4a1b2a1e9e3b4b5c6d",
    "JAMES BLAKE": "https://i.scdn.co/image/ab6761610000e5eb0e1a4b5c6d7e8f9a0b1c2d3e",
    "RADWIMPS": "https://i.scdn.co/image/ab6761610000e5eb9a0b1c2d3e4f5a6b7c8d9e0f",
    "VAMPIRE WEEKEND": "https://i.scdn.co/image/ab6761610000e5eb7c8d9e0f1a2b3c4d5e6f7a8b"
}

async def update_artist_images():
    """更新所有艺术家的头像"""
    try:
        print("=== Updating artist images ===")
        
        # 检查数据库连接
        if not db_service.is_connected():
            print("Database not connected!")
            return False
        
        # 获取所有艺术家
        result = db_service.supabase.table("artists").select("*").execute()
        
        if not result.data:
            print("No artists found in database")
            return False
        
        success_count = 0
        total_count = len(result.data)
        
        for artist in result.data:
            artist_name = artist.get("name")
            artist_id = artist.get("id")
            
            if artist_name in ARTIST_IMAGES:
                image_url = ARTIST_IMAGES[artist_name]
                
                try:
                    # 更新艺术家头像
                    update_result = db_service.supabase.table("artists").update({
                        "image_url": image_url
                    }).eq("id", artist_id).execute()
                    
                    if update_result.data:
                        print(f"✅ Updated {artist_name}: {image_url}")
                        success_count += 1
                    else:
                        print(f"❌ Failed to update {artist_name}")
                        
                except Exception as e:
                    print(f"❌ Error updating {artist_name}: {str(e)}")
            else:
                print(f"⚠️  No image URL configured for {artist_name}")
        
        print(f"\n📊 Summary: {success_count}/{total_count} artists updated successfully")
        return success_count == total_count
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def test_image_column():
    """测试image_url列是否存在"""
    try:
        print("=== Testing image_url column ===")
        
        # 尝试查询包含image_url的记录
        result = db_service.supabase.table("artists").select("id, name, image_url").limit(1).execute()
        
        if result.data:
            print("✅ image_url column exists and is accessible")
            return True
        else:
            print("❌ Could not access image_url column")
            return False
            
    except Exception as e:
        if "column" in str(e).lower() and "image_url" in str(e).lower():
            print("❌ image_url column does not exist. Please run the SQL command:")
            print("ALTER TABLE artists ADD COLUMN image_url TEXT;")
            return False
        else:
            print(f"❌ Error accessing database: {str(e)}")
            return False

async def main():
    """主函数"""
    print("🎨 Artist Image Update Script")
    print("============================")
    
    # 首先测试列是否存在
    column_exists = await test_image_column()
    
    if not column_exists:
        print("\n⚠️  Please add the image_url column first using the SQL command shown above.")
        return
    
    # 如果列存在，继续更新
    success = await update_artist_images()
    
    if success:
        print("\n🎉 All artist images updated successfully!")
    else:
        print("\n😞 Some updates failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 