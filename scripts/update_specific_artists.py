#!/usr/bin/env python3
"""
手动更新特定艺术家的 Wikipedia 数据脚本
使用正确的艺术家名字格式
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

# 映射数据库中的名字到正确的 Wikipedia 名字
ARTIST_NAME_MAPPING = {
    "THE HIVES": "The Hives",
    "FOUR TET": "Four Tet", 
    "JAMES BLAKE": "James Blake (musician)",
    "VAMPIRE WEEKEND": "Vampire Weekend",
    "RADWIMPS": "Radwimps",  # 已经是正确的
    "Fred again..": "Fred again.."  # 已经是正确的
}

async def update_specific_artists():
    """手动更新特定艺术家的 Wikipedia 数据"""
    try:
        print("=== Updating specific artists with correct Wikipedia data ===")
        
        # 获取所有艺术家
        result = await artist_db_service.search_artists('', limit=50)
        
        if not result.get('success') or not result.get('data'):
            print("No artists found in database")
            return False
        
        artists = result['data']
        success_count = 0
        
        for artist in artists:
            db_name = artist.get("name")
            artist_id = artist.get("id")
            
            # 检查是否在我们的映射中
            if db_name not in ARTIST_NAME_MAPPING:
                print(f"⏭️  Skipping {db_name} (not in mapping)")
                continue
                
            wikipedia_name = ARTIST_NAME_MAPPING[db_name]
            print(f"\n🔄 Processing: {db_name} -> {wikipedia_name}")
            
            try:
                # 获取英文 Wikipedia 数据
                wiki_data = await wikipedia_service.get_artist_info(wikipedia_name, "en")
                
                if wiki_data and wiki_data.extract and len(wiki_data.extract) > 50:
                    # 确保不是模糊的消歧义页面
                    if "may refer to" not in wiki_data.extract.lower():
                        # 更新数据库中的 Wikipedia 数据
                        update_result = await artist_db_service.update_artist_wikipedia_data(
                            artist_id,
                            {
                                "title": wiki_data.title,
                                "extract": wiki_data.extract,
                                "thumbnail": wiki_data.thumbnail.model_dump() if wiki_data.thumbnail else None,
                                "categories": wiki_data.categories,
                                "references": [ref.model_dump() for ref in wiki_data.references]
                            },
                            wiki_data.extract
                        )
                        
                        if update_result.get('success'):
                            print(f"✅ Updated {db_name}")
                            print(f"   Wikipedia title: {wiki_data.title}")
                            print(f"   Extract: {wiki_data.extract[:100]}...")
                            success_count += 1
                        else:
                            print(f"❌ Failed to update database for {db_name}: {update_result.get('error')}")
                    else:
                        print(f"⚠️  Disambiguation page found for {wikipedia_name}, skipping")
                else:
                    print(f"⚠️  No valid Wikipedia data found for {wikipedia_name}")
                    
            except Exception as e:
                print(f"❌ Error processing {db_name}: {str(e)}")
        
        print(f"\n📊 Summary: {success_count} artists updated successfully")
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
                
                # 检查是否是真实的英文数据
                is_real_data = (
                    wiki_extract and 
                    wiki_extract != "None" and 
                    len(wiki_extract) > 50 and
                    not wiki_extract.startswith(name + "是一位知名的音乐艺术家")  # 不是中文模板
                )
                
                status = "✅" if is_real_data else "❌"
                preview = wiki_extract[:80] + "..." if wiki_extract and len(wiki_extract) > 80 else wiki_extract
                print(f"{status} {name}: {preview}")
        
    except Exception as e:
        print(f"Error verifying updates: {str(e)}")

async def main():
    """主函数"""
    print("🔄 Specific Artist Wikipedia Data Update Script")
    print("===============================================")
    
    # 更新特定艺术家的 Wikipedia 数据
    success = await update_specific_artists()
    
    if success:
        print("\n🎉 Specific artists updated successfully!")
        await verify_updates()
    else:
        print("\n😞 Some updates failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 