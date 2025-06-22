#!/usr/bin/env python3
"""
更新艺术家数据的脚本
为现有的艺术家添加真实的 Wikipedia 数据
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.artist_db_service import artist_db_service
from services.wikipedia_service import WikipediaService

# 创建 Wikipedia 服务实例
wikipedia_service = WikipediaService()

async def update_artist_wikipedia_data():
    """为所有艺术家更新 Wikipedia 数据"""
    try:
        print("=== Updating artists with real Wikipedia data ===")
        
        # 获取所有艺术家
        result = await artist_db_service.search_artists('', limit=50)
        
        if not result.get('success') or not result.get('data'):
            print("No artists found in database")
            return False
        
        artists = result['data']
        print(f"Found {len(artists)} artists to update")
        
        success_count = 0
        
        for artist in artists:
            artist_name = artist.get("name")
            artist_id = artist.get("id")
            
            print(f"\n🔄 Processing: {artist_name}")
            
            try:
                # 获取英文 Wikipedia 数据
                wiki_data = await wikipedia_service.get_artist_info(artist_name, "en")
                
                if wiki_data and wiki_data.extract:
                    # 更新数据库中的 Wikipedia 数据
                    update_result = await artist_db_service.update_artist_wikipedia_data(
                        artist_id,
                        {
                            "title": wiki_data.title,
                            "extract": wiki_data.extract,
                            "thumbnail": wiki_data.thumbnail.dict() if wiki_data.thumbnail else None,
                            "categories": wiki_data.categories,
                            "references": [ref.dict() for ref in wiki_data.references]
                        },
                        wiki_data.extract
                    )
                    
                    if update_result.get('success'):
                        print(f"✅ Updated {artist_name}")
                        print(f"   Wikipedia extract: {wiki_data.extract[:100]}...")
                        success_count += 1
                    else:
                        print(f"❌ Failed to update database for {artist_name}: {update_result.get('error')}")
                else:
                    print(f"⚠️  No Wikipedia data found for {artist_name}")
                    
            except Exception as e:
                print(f"❌ Error processing {artist_name}: {str(e)}")
        
        print(f"\n📊 Summary: {success_count}/{len(artists)} artists updated successfully")
        return success_count > 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def verify_updates():
    """验证更新结果"""
    try:
        print("\n=== Verifying Wikipedia data updates ===")
        
        result = await artist_db_service.search_artists('', limit=50)
        
        if result.get('success') and result.get('data'):
            for artist in result['data']:
                name = artist.get("name", "Unknown")
                wiki_extract = artist.get("wiki_extract", "None")
                status = "✅" if wiki_extract and wiki_extract != "None" and len(wiki_extract) > 50 else "❌"
                preview = wiki_extract[:80] + "..." if wiki_extract and len(wiki_extract) > 80 else wiki_extract
                print(f"{status} {name}: {preview}")
        
    except Exception as e:
        print(f"Error verifying updates: {str(e)}")

async def main():
    """主函数"""
    print("🔄 Artist Wikipedia Data Update Script")
    print("=====================================")
    
    # 更新艺术家的 Wikipedia 数据
    success = await update_artist_wikipedia_data()
    
    if success:
        print("\n🎉 Wikipedia data updated successfully!")
        await verify_updates()
    else:
        print("\n😞 Some updates failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 