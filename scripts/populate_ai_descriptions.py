import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

# Load environment variables from .env file
load_dotenv()

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.artist_db_service import artist_db_service
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIDescriptionPopulator:
    """使用 DeepSeek API 和 Volcengine Ark SDK 生成 AI 描述"""
    
    def __init__(self):
        self.db_service = artist_db_service
        self.api_key = settings.ARK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.client = None
        
        if self.api_key:
            try:
                self.client = Ark(api_key=self.api_key)
                logging.info(f"Successfully initialized Ark client for model: {self.model}")
            except Exception as e:
                logging.error(f"Failed to initialize Ark client: {str(e)}")
                raise
        else:
            logging.error("ARK_API_KEY environment variable not set!")
            raise ValueError("Please set ARK_API_KEY environment variable")

    async def call_deepseek_api(self, wiki_extract: str, artist_name: str) -> Optional[str]:
        """使用 Volcengine Ark SDK 调用 DeepSeek API 生成刻薄的描述"""
        if not self.client:
            logging.error("Ark client is not initialized.")
            return None

        prompt = f"""
你是一个刻薄但有趣的音乐评论家。请根据以下艺术家的维基百科信息，写一段100-150字的刻薄但幽默的描述。

艺术家名称: {artist_name}
维基百科信息: {wiki_extract}

要求:
1. 保持刻薄但不要恶意
2. 要有幽默感
3. 长度控制在100-150字
4. 用中文写作
5. 可以调侃但不失尊重

请直接输出描述，不要加任何前缀或后缀。
"""
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.DEEPSEEK_TEMPERATURE,
                max_tokens=settings.DEEPSEEK_MAX_TOKENS
            )
            
            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content.strip()
            else:
                logging.warning(f"API call for {artist_name} returned no choices.")
                return None
                
        except Exception as e:
            logging.error(f"Error calling DeepSeek API via Ark SDK for {artist_name}: {e}")
            return None
    
    async def get_artists_with_wiki(self) -> List[Dict[str, Any]]:
        """获取有 Wiki 描述但还没有 AI 描述的艺术家"""
        logging.info("Fetching artists with Wiki data but no AI description...")
        
        # 获取所有艺术家
        response = self.db_service.db.supabase.table("artists").select(
            "id, name, wiki_extract, genres"  # Corrected column name
        ).execute()
        
        if not response.data:
            logging.error("Could not fetch artists from database.")
            return []
        
        # 获取已有的 AI 描述
        ai_response = self.db_service.db.supabase.table("ai_descriptions").select(
            "artist_id"
        ).execute()
        
        existing_ai_artist_ids = set()
        if ai_response.data:
            existing_ai_artist_ids = {item["artist_id"] for item in ai_response.data}
        
        # 过滤：有 wiki_extract 但没有 AI 描述的艺术家
        target_artists = [
            artist for artist in response.data
            if artist.get("wiki_extract") 
            and artist["id"] not in existing_ai_artist_ids
        ]
        
        logging.info(f"Found {len(target_artists)} artists with Wiki data but no AI description.")
        return target_artists
    
    async def save_ai_description(self, artist_id: str, ai_description: str) -> bool:
        """保存 AI 描述到数据库"""
        try:
            # 检查是否已存在
            existing = self.db_service.db.supabase.table("ai_descriptions").select(
                "*"
            ).eq("artist_id", artist_id).execute()
            
            if existing.data:
                # 更新现有记录
                result = self.db_service.db.supabase.table("ai_descriptions").update({
                    "content": ai_description
                }).eq("artist_id", artist_id).execute()
            else:
                # 插入新记录
                result = self.db_service.db.supabase.table("ai_descriptions").insert({
                    "artist_id": artist_id,
                    "content": ai_description,
                    "language": "zh"
                }).execute()
            
            return bool(result.data)
        except Exception as e:
            logging.error(f"Error saving AI description for artist_id {artist_id}: {e}")
            return False
    
    async def populate_all(self):
        """为所有目标艺术家生成 AI 描述"""
        artists_to_process = await self.get_artists_with_wiki()
        
        if not artists_to_process:
            logging.info("No artists to process. All artists with Wiki data have AI descriptions.")
            return

        total = len(artists_to_process)
        success_count = 0
        failed_artists = []
        
        logging.info(f"=== Starting AI Description Generation for {total} Artists ===")
        
        for i, artist in enumerate(artists_to_process, 1):
            artist_id = artist["id"]
            artist_name = artist["name"]
            
            logging.info(f"\n[{i}/{total}] Processing: {artist_name}")

            # Enhance prompt with genres if available
            wiki_extract = artist.get("wiki_extract", "")
            genres = artist.get("genres")  # Corrected key
            if genres:
                genre_string = ", ".join(genres)
                wiki_extract += f"\n\n关键音乐类型: {genre_string}"

            try:
                # 调用 DeepSeek API 生成描述
                ai_description = await self.call_deepseek_api(wiki_extract, artist_name)
                
                if not ai_description:
                    logging.warning(f"  ⚠️ Could not generate AI description for {artist_name}. Skipping.")
                    failed_artists.append(artist_name)
                    continue
                
                logging.info(f"  Generated AI description: \"{ai_description[:100]}...\"")
                
                # 保存到数据库
                if await self.save_ai_description(artist_id, ai_description):
                    logging.info(f"  🚀 Successfully saved AI description for {artist_name}")
                    success_count += 1
                else:
                    logging.error(f"  ❌ Failed to save AI description for {artist_name}")
                    failed_artists.append(artist_name)
                
            except Exception as e:
                logging.error(f"  ❌ Error processing {artist_name}: {e}")
                failed_artists.append(artist_name)
            
            # Add a small delay to avoid rate limiting
            await asyncio.sleep(1)
        
        logging.info("\n" + "="*60)
        logging.info("=== AI Description Generation Complete ===")
        logging.info(f"  Total artists processed: {total}")
        logging.info(f"  Successfully generated: {success_count}")
        logging.info(f"  Failed: {total - success_count}")
        
        if failed_artists:
            logging.info(f"\nFailed artists ({len(failed_artists)}):")
            for artist in failed_artists[:10]:
                logging.info(f"  - {artist}")
            if len(failed_artists) > 10:
                logging.info(f"  ... and {len(failed_artists) - 10} more")
        
        logging.info("="*60)

async def main():
    populator = AIDescriptionPopulator()
    await populator.populate_all()

if __name__ == "__main__":
    asyncio.run(main()) 