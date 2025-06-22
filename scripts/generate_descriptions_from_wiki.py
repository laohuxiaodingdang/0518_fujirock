import asyncio
import logging
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WikiDescriptionGenerator:
    """从 Wiki 数据生成 Description"""
    
    def __init__(self):
        self.artist_db_service = artist_db_service

    def clean_wiki_extract(self, extract: str) -> str:
        """
        清理和格式化 Wiki 摘要，生成适合 App 展示的 description
        """
        if not extract:
            return ""
        
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', extract.strip())
        
        # 移除括号内的内容（通常是引用或注释）
        cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned)
        
        # 移除方括号内的内容（通常是 Wiki 链接）
        cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
        
        # 移除多余的标点符号
        cleaned = re.sub(r'[。、，；：！？]{2,}', '。', cleaned)
        
        # 限制长度（大约 200 个字符）
        if len(cleaned) > 200:
            # 尝试在句号处截断
            sentences = cleaned.split('。')
            result = ""
            for sentence in sentences:
                if len(result + sentence + '。') <= 200:
                    result += sentence + '。'
                else:
                    break
            
            if not result:
                # 如果没有找到合适的句号，直接截断
                result = cleaned[:197] + '...'
            else:
                result = result.rstrip('。')
        else:
            result = cleaned
        
        return result

    async def get_artists_with_wiki_no_description(self) -> List[Dict[str, Any]]:
        """获取有 Wiki 数据但缺少 Description 的艺术家"""
        logging.info("Fetching artists with Wiki data but missing descriptions...")
        
        response = self.artist_db_service.db.supabase.table("artists").select(
            "id, name, wiki_data, wiki_extract, description"
        ).execute()
        
        if not response.data:
            logging.error("Could not fetch artists from database.")
            return []
            
        # 过滤：有 wiki_extract 但没有 description 的艺术家
        target_artists = [
            artist for artist in response.data
            if artist.get("wiki_extract") and (not artist.get("description") or artist.get("description") == "")
        ]
        
        logging.info(f"Found {len(target_artists)} artists with Wiki data but missing descriptions.")
        return target_artists

    async def generate_descriptions(self):
        """为所有目标艺术家生成 Description"""
        artists_to_update = await self.get_artists_with_wiki_no_description()
        
        if not artists_to_update:
            logging.info("No artists to update. All artists with Wiki data have descriptions.")
            return
            
        total = len(artists_to_update)
        updated_count = 0
        failed_artists = []
        
        logging.info(f"=== Starting Description Generation from Wiki for {total} Artists ===")
        
        for i, artist in enumerate(artists_to_update, 1):
            artist_name = artist["name"]
            artist_id = artist["id"]
            wiki_extract = artist["wiki_extract"]
            
            logging.info(f"\n[{i}/{total}] Processing: {artist_name}")
            
            try:
                # 生成 Description
                description = self.clean_wiki_extract(wiki_extract)
                
                if not description:
                    logging.warning(f"  ⚠️ Could not generate description for {artist_name}. Skipping.")
                    failed_artists.append(artist_name)
                    continue
                
                logging.info(f"  Generated description: \"{description[:100]}...\"")
                
                # 更新数据库
                update_response = await self.artist_db_service.update_artist_simple(
                    artist_id=artist_id,
                    update_data={"description": description}
                )
                
                if update_response.get("success"):
                    logging.info(f"  🚀 Successfully updated database for {artist_name}")
                    updated_count += 1
                else:
                    logging.error(f"  ❌ Failed to update database for {artist_name}: {update_response.get('error')}")
                    failed_artists.append(artist_name)
                    
            except Exception as e:
                logging.error(f"  ❌ Error processing {artist_name}: {e}")
                failed_artists.append(artist_name)

        logging.info("\n" + "="*60)
        logging.info("=== Description Generation from Wiki Complete ===")
        logging.info(f"  Total artists processed: {total}")
        logging.info(f"  Successfully updated: {updated_count}")
        logging.info(f"  Failed: {total - updated_count}")
        
        if failed_artists:
            logging.info(f"\nFailed artists ({len(failed_artists)}):")
            for artist in failed_artists[:10]:  # 只显示前10个
                logging.info(f"  - {artist}")
            if len(failed_artists) > 10:
                logging.info(f"  ... and {len(failed_artists) - 10} more")
        
        logging.info("="*60)

async def main():
    generator = WikiDescriptionGenerator()
    await generator.generate_descriptions()

if __name__ == "__main__":
    asyncio.run(main()) 