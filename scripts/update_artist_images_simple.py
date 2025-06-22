#!/usr/bin/env python3
"""
更新艺术家头像的简化脚本
直接使用高质量图片URL
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import db_service

# 高质量艺术家头像映射
ARTIST_IMAGES = {
    "Fred again..": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=400&q=80",
    "THE HIVES": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=400&q=80", 
    "FOUR TET": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=400&q=80",
    "JAMES BLAKE": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=400&q=80",
    "RADWIMPS": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=400&q=80",
    "VAMPIRE WEEKEND": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=400&q=80"
}

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
        if "image_url" in str(e):
            print("❌ image_url column does not exist. Please add it first:")
            print("   1. Go to your Supabase dashboard")
            print("   2. Open the Table Editor")
            print("   3. Select the 'artists' table")
            print("   4. Click 'Add Column'")
            print("   5. Name: 'image_url', Type: 'text', Nullable: true")
            print("   6. Save the changes")
            print("\n   Or run this SQL command:")
            print("   ALTER TABLE artists ADD COLUMN image_url TEXT;")
            return False
        else:
            print(f"❌ Error accessing database: {str(e)}")
            return False

async def update_artist_images():
    """更新所有艺术家的头像"""
    try:
        print("=== Updating artist images ===")
        
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
                        print(f"✅ Updated {artist_name}")
                        print(f"   Image: {image_url}")
                        success_count += 1
                    else:
                        print(f"❌ Failed to update {artist_name}")
                        
                except Exception as e:
                    print(f"❌ Error updating {artist_name}: {str(e)}")
            else:
                print(f"⚠️  No image configured for {artist_name}")
        
        print(f"\n📊 Summary: {success_count}/{total_count} artists updated successfully")
        return success_count > 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def verify_updates():
    """验证更新结果"""
    try:
        print("\n=== Verifying updates ===")
        
        result = db_service.supabase.table("artists").select("name, image_url").execute()
        
        if result.data:
            for artist in result.data:
                name = artist.get("name", "Unknown")
                image_url = artist.get("image_url", "None")
                status = "✅" if image_url and image_url != "None" else "❌"
                print(f"{status} {name}: {image_url}")
        
    except Exception as e:
        print(f"Error verifying updates: {str(e)}")

async def main():
    """主函数"""
    print("🎨 Artist Image Update Script (Simple Version)")
    print("==============================================")
    
    # 首先测试列是否存在
    column_exists = await test_image_column()
    
    if not column_exists:
        print("\n⚠️  Please add the image_url column first as shown above.")
        return
    
    # 如果列存在，继续更新
    success = await update_artist_images()
    
    if success:
        print("\n🎉 Artist images updated successfully!")
        await verify_updates()
    else:
        print("\n😞 Some updates failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 