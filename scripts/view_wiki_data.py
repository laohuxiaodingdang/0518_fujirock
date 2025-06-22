import asyncio
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.database_service import db_service

async def view_wiki_data():
    """查看数据库中的 Wikipedia 信息"""
    print("=== 查看数据库中的 Wikipedia 信息 ===\n")
    
    # 查看有 Wikipedia 数据的艺术家
    print("📚 有 Wikipedia 数据的艺术家:")
    print("-" * 50)
    
    try:
        response = db_service.supabase.table("artists").select(
            "name, wiki_extract, wiki_data"
        ).not_.is_("wiki_extract", "null").execute()
        
        if response.data:
            for i, artist in enumerate(response.data, 1):
                name = artist.get("name", "Unknown")
                extract = artist.get("wiki_extract", "")
                wiki_data = artist.get("wiki_data", {})
                
                # 只显示前100个字符
                extract_preview = extract[:100] + "..." if len(extract) > 100 else extract
                
                print(f"{i:2d}. {name}")
                if wiki_data:
                    print(f"    Wiki Data: {wiki_data}")
                print(f"    Extract: {extract_preview}")
                print()
        else:
            print("没有找到有 Wikipedia 数据的艺术家")
            
    except Exception as e:
        print(f"查询错误: {e}")
    
    # 查看没有 Wikipedia 数据的艺术家数量
    print("\n📊 统计信息:")
    print("-" * 30)
    
    try:
        # 总数
        total_response = db_service.supabase.table("artists").select("id", count="exact").execute()
        total = total_response.count if total_response.count else 0
        
        # 有 Wikipedia 数据的数量
        with_wiki_response = db_service.supabase.table("artists").select(
            "id", count="exact"
        ).not_.is_("wiki_extract", "null").execute()
        with_wiki = with_wiki_response.count if with_wiki_response.count else 0
        
        # 没有 Wikipedia 数据的数量
        without_wiki = total - with_wiki
        
        print(f"总艺术家数量: {total}")
        print(f"有 Wikipedia 数据: {with_wiki}")
        print(f"没有 Wikipedia 数据: {without_wiki}")
        print(f"覆盖率: {with_wiki/total*100:.1f}%")
        
    except Exception as e:
        print(f"统计查询错误: {e}")

if __name__ == "__main__":
    asyncio.run(view_wiki_data()) 