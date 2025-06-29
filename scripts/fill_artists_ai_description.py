import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleAIDescriptionFiller:
    """独立的 AI 描述填充工具"""
    
    def __init__(self):
        # 初始化 Supabase 客户端
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase = None
        
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logging.info("✅ Supabase 客户端初始化成功")
        else:
            raise ValueError("请设置 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 环境变量")
        
        # 初始化 AI 客户端
        self.api_key = os.getenv("ARK_API_KEY")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.client = None
        
        if self.api_key:
            try:
                self.client = Ark(api_key=self.api_key)
                logging.info(f"✅ 成功初始化 Ark 客户端，模型: {self.model}")
            except Exception as e:
                logging.error(f"❌ 初始化 Ark 客户端失败: {str(e)}")
                raise
        else:
            logging.error("❌ ARK_API_KEY 环境变量未设置!")
            raise ValueError("请设置 ARK_API_KEY 环境变量")

    async def call_deepseek_api(self, wiki_extract: str, artist_name: str, genres: List[str] = None) -> Optional[str]:
        """调用 DeepSeek API 生成毒舌描述"""
        if not self.client:
            logging.error("Ark 客户端未初始化")
            return None

        # 构建更丰富的提示词
        genre_info = ""
        if genres:
            genre_info = f"\n音乐风格: {', '.join(genres)}"

        prompt = f"""
你是一个刻薄但有趣的音乐评论家。请根据以下信息，为这个艺术家写一段100-150字的刻薄但幽默的中文描述。

艺术家: {artist_name}
{genre_info}

维基百科信息: {wiki_extract}

要求:
1. 刻薄但不恶毒，要有幽默感
2. 可以调侃但保持基本尊重
3. 长度100-150字
4. 用中文写作
5. 风格要生动有趣，让人印象深刻

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
                temperature=0.8,
                max_tokens=1000
            )
            
            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content.strip()
            else:
                logging.warning(f"⚠️ {artist_name} 的 API 调用没有返回结果")
                return None
                
        except Exception as e:
            logging.error(f"❌ 调用 DeepSeek API 失败 ({artist_name}): {e}")
            return None

    async def get_artists_need_ai_description(self) -> List[Dict[str, Any]]:
        """获取需要生成 AI 描述的艺术家"""
        logging.info("🔍 查找需要生成 AI 描述的艺术家...")
        
        try:
            # 获取所有艺术家
            response = self.supabase.table("artists").select(
                "id, name, wiki_extract, genres, ai_description"
            ).execute()
            
            if not response.data:
                logging.error("❌ 无法从数据库获取艺术家数据")
                return []
            
            # 过滤条件：有 wiki_extract 但 ai_description 为空的艺术家
            target_artists = []
            for artist in response.data:
                has_wiki = artist.get("wiki_extract") and artist.get("wiki_extract").strip()
                has_ai_desc = artist.get("ai_description") and artist.get("ai_description").strip()
                
                if has_wiki and not has_ai_desc:
                    target_artists.append(artist)
            
            logging.info(f"📊 找到 {len(target_artists)} 个需要生成 AI 描述的艺术家")
            return target_artists
            
        except Exception as e:
            logging.error(f"❌ 获取艺术家数据失败: {str(e)}")
            return []

    async def update_artist_ai_description(self, artist_id: str, ai_description: str) -> bool:
        """更新艺术家的 AI 描述，带重试机制"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # 修复时间函数警告
                current_time = datetime.now(timezone.utc).isoformat()
                
                result = self.supabase.table("artists").update({
                    "ai_description": ai_description,
                    "updated_at": current_time
                }).eq("id", artist_id).execute()
                
                if result.data:
                    return True
                else:
                    logging.warning(f"⚠️ 更新返回空数据 (尝试 {attempt + 1}/{max_retries})")
                    
            except Exception as e:
                logging.error(f"❌ 更新艺术家 AI 描述失败 (尝试 {attempt + 1}/{max_retries}, ID: {artist_id}): {e}")
                
                if attempt < max_retries - 1:
                    logging.info(f"⏳ 等待 {retry_delay} 秒后重试...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    return False
        
        return False

    async def check_status(self):
        """检查当前状态"""
        logging.info("📊 检查数据库状态...")
        
        try:
            # 获取所有艺术家统计
            all_response = self.supabase.table("artists").select(
                "id, name, wiki_extract, ai_description"
            ).execute()
            
            if not all_response.data:
                logging.error("❌ 无法获取艺术家数据")
                return
            
            total_artists = len(all_response.data)
            has_wiki = len([a for a in all_response.data if a.get("wiki_extract")])
            has_ai_desc = len([a for a in all_response.data if a.get("ai_description")])
            need_ai_desc = len([a for a in all_response.data 
                              if a.get("wiki_extract") and not a.get("ai_description")])
            
            print(f"""
🎯 数据库状态报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 总艺术家数量: {total_artists}
📝 有 Wikipedia 信息: {has_wiki}
🤖 已有 AI 描述: {has_ai_desc}
⚠️  需要生成 AI 描述: {need_ai_desc}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            
            if need_ai_desc > 0:
                # 显示前几个需要处理的艺术家
                need_artists = [a for a in all_response.data 
                               if a.get("wiki_extract") and not a.get("ai_description")]
                
                print("🎯 需要生成 AI 描述的艺术家（前10个）:")
                for i, artist in enumerate(need_artists[:10], 1):
                    print(f"  {i:2d}. {artist['name']}")
                
                if len(need_artists) > 10:
                    print(f"     ... 还有 {len(need_artists) - 10} 个")
                
                print(f"\n💡 准备开始生成...")
            else:
                print("✅ 所有艺术家都已经有 AI 描述了！")
                
        except Exception as e:
            logging.error(f"❌ 检查状态失败: {str(e)}")

    async def fill_all(self):
        """为所有需要的艺术家生成 AI 描述"""
        artists_to_process = await self.get_artists_need_ai_description()
        
        if not artists_to_process:
            logging.info("✅ 没有需要处理的艺术家，所有艺术家都已经有 AI 描述了！")
            return

        total = len(artists_to_process)
        success_count = 0
        failed_artists = []
        
        logging.info(f"🚀 开始为 {total} 个艺术家生成 AI 描述...")
        
        for i, artist in enumerate(artists_to_process, 1):
            artist_id = artist["id"]
            artist_name = artist["name"]
            wiki_extract = artist.get("wiki_extract", "")
            genres = artist.get("genres", [])
            
            logging.info(f"\n[{i}/{total}] 处理: {artist_name}")

            try:
                # 调用 DeepSeek API 生成描述
                ai_description = await self.call_deepseek_api(wiki_extract, artist_name, genres)
                
                if not ai_description:
                    logging.warning(f"  ⚠️ 无法为 {artist_name} 生成 AI 描述，跳过")
                    failed_artists.append(artist_name)
                    continue
                
                logging.info(f"  📝 生成描述: \"{ai_description[:50]}...\"")
                
                # 保存到数据库（带重试机制）
                if await self.update_artist_ai_description(artist_id, ai_description):
                    logging.info(f"  ✅ 成功保存 {artist_name} 的 AI 描述")
                    success_count += 1
                else:
                    logging.error(f"  ❌ 保存 {artist_name} 的 AI 描述失败（重试后仍失败）")
                    failed_artists.append(artist_name)
                
            except Exception as e:
                logging.error(f"  ❌ 处理 {artist_name} 时出错: {e}")
                failed_artists.append(artist_name)
            
            # 添加延迟避免 API 限流和数据库压力
            await asyncio.sleep(2)  # 增加延迟到2秒
        
        # 输出最终结果
        print(f"\n{'='*60}")
        print("🎉 AI 描述生成完成！")
        print(f"📊 总共处理: {total} 个艺术家")
        print(f"✅ 成功生成: {success_count}")
        print(f"❌ 失败: {total - success_count}")
        
        if failed_artists:
            print(f"\n❌ 失败的艺术家 ({len(failed_artists)}):")
            for artist in failed_artists[:10]:
                print(f"  - {artist}")
            if len(failed_artists) > 10:
                print(f"  ... 还有 {len(failed_artists) - 10} 个")
        
        print("="*60)

    async def fill_single(self, artist_name: str):
        """为单个艺术家生成 AI 描述（用于测试）"""
        logging.info(f"🎯 为单个艺术家生成 AI 描述: {artist_name}")
        
        try:
            # 查找艺术家
            response = self.supabase.table("artists").select(
                "id, name, wiki_extract, genres, ai_description"
            ).ilike("name", f"%{artist_name}%").execute()
            
            if not response.data:
                print(f"❌ 未找到艺术家: {artist_name}")
                return
            
            artist = response.data[0]
            artist_id = artist["id"]
            artist_name = artist["name"]
            wiki_extract = artist.get("wiki_extract", "")
            genres = artist.get("genres", [])
            
            if not wiki_extract:
                print(f"❌ {artist_name} 没有 Wikipedia 信息")
                return
            
            if artist.get("ai_description"):
                print(f"⚠️ {artist_name} 已经有 AI 描述了")
                print(f"现有描述: {artist['ai_description']}")
                return
            
            print(f"🔍 处理: {artist_name}")
            
            # 生成描述
            ai_description = await self.call_deepseek_api(wiki_extract, artist_name, genres)
            
            if not ai_description:
                print(f"❌ 无法生成 AI 描述")
                return
            
            print(f"📝 生成的描述: {ai_description}")
            
            # 保存到数据库
            if await self.update_artist_ai_description(artist_id, ai_description):
                print(f"✅ 成功保存 {artist_name} 的 AI 描述")
            else:
                print(f"❌ 保存失败")
                
        except Exception as e:
            logging.error(f"❌ 处理单个艺术家时出错: {e}")

async def main():
    """主函数"""
    try:
        filler = SimpleAIDescriptionFiller()
        
        # 检查命令行参数
        if len(sys.argv) > 1:
            # 如果提供了艺术家名称，只处理单个艺术家
            artist_name = " ".join(sys.argv[1:])
            await filler.fill_single(artist_name)
            return
        
        # 先检查状态
        await filler.check_status()
        
        # 询问是否开始生成
        print("\n🤔 是否开始生成 AI 描述？(y/n): ", end="")
        choice = input().strip().lower()
        if choice in ['y', 'yes', '是', '好']:
            await filler.fill_all()
        else:
            print("👋 已取消操作")
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
    except Exception as e:
        logging.error(f"❌ 程序运行出错: {e}")
        print(f"❌ 出现错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())