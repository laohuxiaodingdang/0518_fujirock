import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def analyze_ai_descriptions():
    """分析 AI 描述的覆盖率和统计信息"""
    logging.info("=== AI Descriptions Analysis ===")
    
    try:
        # 1. 获取所有艺术家总数
        all_artists_response = artist_db_service.db.supabase.table("artists").select(
            "id, name, wiki_extract, spotify_id, genres"
        ).execute()
        
        if not all_artists_response.data:
            logging.error("Could not fetch artists from database.")
            return
        
        total_artists = len(all_artists_response.data)
        logging.info(f"📊 Total artists in database: {total_artists}")
        
        # 2. 获取有 AI 描述的艺术家
        ai_descriptions_response = artist_db_service.db.supabase.table("ai_descriptions").select(
            "artist_id, content, language, created_at"
        ).execute()
        
        artists_with_ai = len(ai_descriptions_response.data) if ai_descriptions_response.data else 0
        logging.info(f"🤖 Artists with AI descriptions: {artists_with_ai}")
        
        # 3. 计算覆盖率
        coverage_rate = (artists_with_ai / total_artists * 100) if total_artists > 0 else 0
        logging.info(f"📈 AI Description Coverage: {coverage_rate:.1f}%")
        
        # 4. 分析有 Wiki 数据但缺少 AI 描述的艺术家
        artists_with_wiki = [a for a in all_artists_response.data if a.get("wiki_extract")]
        artists_with_wiki_count = len(artists_with_wiki)
        logging.info(f"📚 Artists with Wiki data: {artists_with_wiki_count}")
        
        # 获取有 AI 描述的艺术家 ID 集合
        ai_artist_ids = set()
        if ai_descriptions_response.data:
            ai_artist_ids = {item["artist_id"] for item in ai_descriptions_response.data}
        
        # 有 Wiki 但没有 AI 描述的艺术家
        missing_ai_with_wiki = [
            a for a in artists_with_wiki 
            if a["id"] not in ai_artist_ids
        ]
        missing_ai_with_wiki_count = len(missing_ai_with_wiki)
        
        # 有 Wiki 且有 AI 描述的艺术家
        has_ai_with_wiki = [
            a for a in artists_with_wiki 
            if a["id"] in ai_artist_ids
        ]
        has_ai_with_wiki_count = len(has_ai_with_wiki)
        
        logging.info(f"✅ Artists with Wiki + AI: {has_ai_with_wiki_count}")
        logging.info(f"❌ Artists with Wiki but no AI: {missing_ai_with_wiki_count}")
        
        # 5. 分析没有 Wiki 数据的艺术家
        artists_without_wiki = [a for a in all_artists_response.data if not a.get("wiki_extract")]
        artists_without_wiki_count = len(artists_without_wiki)
        logging.info(f"📝 Artists without Wiki data: {artists_without_wiki_count}")
        
        # 6. 分析 Spotify 数据情况
        artists_with_spotify = [a for a in all_artists_response.data if a.get("spotify_id")]
        artists_with_spotify_count = len(artists_with_spotify)
        logging.info(f"🎵 Artists with Spotify ID: {artists_with_spotify_count}")
        
        # 7. 分析语言分布
        language_stats = {}
        if ai_descriptions_response.data:
            for item in ai_descriptions_response.data:
                lang = item.get("language", "unknown")
                language_stats[lang] = language_stats.get(lang, 0) + 1
        
        logging.info(f"🌍 Language distribution: {language_stats}")
        
        # 8. 分析内容长度统计
        if ai_descriptions_response.data:
            content_lengths = [len(item.get("content", "")) for item in ai_descriptions_response.data]
            if content_lengths:
                avg_length = sum(content_lengths) / len(content_lengths)
                min_length = min(content_lengths)
                max_length = max(content_lengths)
                logging.info(f"📏 Content length stats:")
                logging.info(f"   Average: {avg_length:.1f} characters")
                logging.info(f"   Min: {min_length} characters")
                logging.info(f"   Max: {max_length} characters")
        
        # 9. 详细分类统计
        print("\n" + "="*60)
        print("📊 DETAILED BREAKDOWN")
        print("="*60)
        
        # 分类统计
        categories = {
            "Complete (Wiki + AI)": has_ai_with_wiki_count,
            "Wiki only (no AI)": missing_ai_with_wiki_count,
            "No Wiki data": artists_without_wiki_count,
            "Total": total_artists
        }
        
        for category, count in categories.items():
            percentage = (count / total_artists * 100) if total_artists > 0 else 0
            print(f"{category:<25} {count:>4} ({percentage:>5.1f}%)")
        
        # 10. 显示缺失 AI 描述的艺术家（前10个）
        if missing_ai_with_wiki:
            print(f"\n❌ Artists with Wiki but missing AI descriptions (showing first 10):")
            for i, artist in enumerate(missing_ai_with_wiki[:10], 1):
                print(f"  {i:2d}. {artist['name']}")
            if len(missing_ai_with_wiki) > 10:
                print(f"  ... and {len(missing_ai_with_wiki) - 10} more")
        
        # 11. 显示没有 Wiki 数据的艺术家（前10个）
        if artists_without_wiki:
            print(f"\n📝 Artists without Wiki data (showing first 10):")
            for i, artist in enumerate(artists_without_wiki[:10], 1):
                spotify_status = "🎵" if artist.get("spotify_id") else "❌"
                print(f"  {i:2d}. {artist['name']} {spotify_status}")
            if len(artists_without_wiki) > 10:
                print(f"  ... and {len(artists_without_wiki) - 10} more")
        
        # 12. 总结和建议
        print("\n" + "="*60)
        print("💡 RECOMMENDATIONS")
        print("="*60)
        
        if missing_ai_with_wiki_count > 0:
            print(f"⚠️  {missing_ai_with_wiki_count} artists have Wiki data but no AI descriptions.")
            print("   Consider running the AI description script again.")
        
        if artists_without_wiki_count > 0:
            print(f"📚 {artists_without_wiki_count} artists lack Wiki data.")
            print("   Consider enriching with Wikipedia data first.")
        
        if coverage_rate >= 90:
            print("🎉 Excellent coverage! AI descriptions are well populated.")
        elif coverage_rate >= 70:
            print("👍 Good coverage. Consider filling remaining gaps.")
        else:
            print("📈 Coverage needs improvement. Focus on missing data.")
        
        print("="*60)
        
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        raise

async def main():
    await analyze_ai_descriptions()

if __name__ == "__main__":
    asyncio.run(main()) 