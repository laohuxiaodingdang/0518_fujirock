import asyncio
import logging
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def search_artist_by_name(search_name: str):
    """搜索艺术家，支持部分匹配"""
    logging.info(f"Searching for artist: '{search_name}'")
    
    # 获取所有艺术家
    response = artist_db_service.db.supabase.table("artists").select(
        "id, name, spotify_id, wiki_data, description"
    ).execute()
    
    if not response.data:
        logging.error("No data found in database.")
        return
    
    artists = response.data
    search_name_lower = search_name.lower()
    
    # 精确匹配
    exact_matches = []
    # 包含匹配
    partial_matches = []
    # 相似匹配（包含关键词）
    similar_matches = []
    
    for artist in artists:
        artist_name = artist.get("name", "")
        artist_name_lower = artist_name.lower()
        
        # 精确匹配
        if artist_name_lower == search_name_lower:
            exact_matches.append(artist)
        # 包含匹配
        elif search_name_lower in artist_name_lower:
            partial_matches.append(artist)
        # 相似匹配（检查是否包含关键词）
        elif any(keyword in artist_name_lower for keyword in search_name_lower.split()):
            similar_matches.append(artist)
    
    # 输出结果
    print(f"\n🔍 Search Results for '{search_name}':")
    
    if exact_matches:
        print(f"\n✅ Exact Matches ({len(exact_matches)}):")
        for artist in exact_matches:
            print(f"  - {artist['name']} (ID: {artist['id']})")
            print(f"    Spotify ID: {artist.get('spotify_id', 'N/A')}")
            print(f"    Has Wiki: {'Yes' if artist.get('wiki_data') else 'No'}")
            print(f"    Has Description: {'Yes' if artist.get('description') else 'No'}")
    
    if partial_matches:
        print(f"\n🔍 Partial Matches ({len(partial_matches)}):")
        for artist in partial_matches[:10]:  # 只显示前10个
            print(f"  - {artist['name']} (ID: {artist['id']})")
        if len(partial_matches) > 10:
            print(f"  ... and {len(partial_matches) - 10} more")
    
    if similar_matches:
        print(f"\n📝 Similar Matches ({len(similar_matches)}):")
        for artist in similar_matches[:10]:  # 只显示前10个
            print(f"  - {artist['name']} (ID: {artist['id']})")
        if len(similar_matches) > 10:
            print(f"  ... and {len(similar_matches) - 10} more")
    
    if not exact_matches and not partial_matches and not similar_matches:
        print("❌ No matches found.")
        
        # 显示一些包含 "fred" 的艺术家
        fred_related = [a for a in artists if "fred" in a.get("name", "").lower()]
        if fred_related:
            print(f"\n💡 Artists containing 'fred':")
            for artist in fred_related:
                print(f"  - {artist['name']}")

async def main():
    search_name = "fred again"
    await search_artist_by_name(search_name)

if __name__ == "__main__":
    asyncio.run(main()) 