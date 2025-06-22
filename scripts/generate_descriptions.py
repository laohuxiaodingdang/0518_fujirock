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

class DescriptionGenerator:
    """
    从现有的 wiki_extract 生成干净的、适合App展示的 description。
    """
    def __init__(self):
        self.db_service = artist_db_service

    def clean_wiki_extract(self, extract: str) -> str:
        """
        清理维基百科摘要文本。
        - 移除引用标记，如 [1], [2], [12]
        - 移除多余的换行符和空格
        - 尝试截取到一个完整的句子（约前2-3句）
        """
        if not extract:
            return ""

        # 移除引用标记
        cleaned_text = re.sub(r'\[\d+\]', '', extract)
        
        # 将多个空格和换行符替换为单个空格
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        # 尝试以一个完整的句子结束，截取前 250 个字符作为预览
        # 我们寻找最后一个句号、问号或感叹号
        max_len = 250
        if len(cleaned_text) > max_len:
            # 找到 250 字符内的最后一个句点
            end_pos = cleaned_text.rfind('.', 0, max_len)
            if end_pos != -1:
                # 截取到句点后
                return cleaned_text[:end_pos + 1]
            else:
                # 如果没有句点，就硬截断并加上省略号
                return cleaned_text[:max_len] + "..."
        
        return cleaned_text

    async def run(self):
        """执行生成描述的流程"""
        logging.info("--- Starting Description Generation from Wiki Extracts ---")
        
        # 1. 获取所有已有 wiki_extract 但缺少 description 的艺术家
        logging.info("Fetching artists with wiki_extract but no description...")
        # 修复：使用Python过滤而不是有问题的PostgREST语法
        response = self.db_service.db.supabase.table("artists").select("id, name, wiki_extract, description").execute()
        
        if not response.data:
            logging.info("No artists found in database.")
            return

        # 在Python中过滤：有wiki_extract但没有description的艺术家
        artists_to_update = [
            artist for artist in response.data
            if artist.get("wiki_extract") and (artist.get("description") is None or artist.get("description") == '')
        ]

        if not artists_to_update:
            logging.info("No artists to update. All descriptions from wiki are already generated.")
            return

        total = len(artists_to_update)
        logging.info(f"Found {total} artists to generate descriptions for.")
        
        updated_count = 0
        for i, artist in enumerate(artists_to_update, 1):
            artist_id = artist['id']
            artist_name = artist['name']
            wiki_extract = artist.get('wiki_extract', '')

            logging.info(f"[{i}/{total}] Processing '{artist_name}'...")

            if not wiki_extract:
                logging.warning(f"  - Skipping '{artist_name}' due to empty wiki_extract.")
                continue

            # 2. 清理文本并生成描述
            description = self.clean_wiki_extract(wiki_extract)
            logging.info(f"  - Generated description: \"{description[:50]}...\"")

            # 3. 更新数据库
            update_data = {"description": description}
            update_response = await self.db_service.update_artist_simple(artist_id, update_data)

            if update_response.get("success"):
                logging.info(f"  - ✅ Successfully updated '{artist_name}'.")
                updated_count += 1
            else:
                logging.error(f"  - ❌ Failed to update '{artist_name}': {update_response.get('error')}")
            
            await asyncio.sleep(0.1) # 轻微延迟，避免瞬间请求过多

        logging.info("\n--- Description Generation Complete ---")
        logging.info(f"  Total processed: {total}")
        logging.info(f"  Successfully updated: {updated_count}")
        logging.info(f"  Failed: {total - updated_count}")


async def main():
    generator = DescriptionGenerator()
    await generator.run()

if __name__ == "__main__":
    asyncio.run(main()) 