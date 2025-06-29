#!/usr/bin/env python3
"""
日文艺术家介绍翻译脚本（调试版）

功能：
1. 检测艺术家介绍中的日文内容
2. 使用AI翻译服务将日文翻译成中文
3. 保留所有专有名词（人名、地名、乐队名等）不翻译
4. 更新数据库中的描述信息
"""

import asyncio
import logging
import sys
import re
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from openai import AsyncOpenAI
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('japanese_translation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class JapaneseTranslator:
    """日文艺术家介绍翻译器（调试版）"""
    
    def __init__(self):
        # 检查环境变量
        self.ark_api_key = os.getenv("ARK_API_KEY")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.ark_api_key:
            raise ValueError("ARK_API_KEY 未配置，请在环境变量中设置 DeepSeek API 密钥")
        
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL 未配置")
        
        # 优先使用 SERVICE_ROLE_KEY，如果没有则使用 ANON_KEY
        supabase_key = self.supabase_service_key or self.supabase_anon_key
        if not supabase_key:
            raise ValueError("Supabase 密钥未配置，需要 SUPABASE_SERVICE_ROLE_KEY 或 SUPABASE_ANON_KEY")
        
        logging.info(f"使用 Supabase 密钥类型: {'SERVICE_ROLE' if self.supabase_service_key else 'ANON'}")
        
        # 初始化客户端
        self.openai_client = AsyncOpenAI(
            api_key=self.ark_api_key,
            base_url="https://api.deepseek.com"
        )
        
        self.supabase: Client = create_client(self.supabase_url, supabase_key)
        
        # === 日文检测规则 ===
        self.hiragana_pattern = re.compile(r'[\u3040-\u309F]')  # 平假名
        self.katakana_pattern = re.compile(r'[\u30A0-\u30FF]')  # 片假名
        self.kanji_pattern = re.compile(r'[\u4E00-\u9FAF]')     # 汉字
        
        # === 专有名词识别模式 ===
        self.proper_noun_patterns = [
            r'\([^)]*[A-Za-z][^)]*\)',  # 括号内包含英文的，如: (Teo Hirvonen)
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # 英文人名，如: John Smith
            r'\b[A-Z]{2,}\b',  # 全大写缩写，如: US, DJ, MTV
            r'[0-9]{4}年',  # 年份，如: 2024年
            r'[0-9]+月',   # 月份，如: 5月
            r'[0-9]+日',   # 日期，如: 22日
            r'[A-Za-z]+\s*Festival',  # 音乐节名称，如: Fuji Rock Festival
            r'[A-Za-z]+\s*Records?',  # 唱片公司，如: Warner Records
        ]

    async def debug_database_info(self):
        """调试数据库信息"""
        logging.info("=== 数据库调试信息 ===")
        
        try:
            # 1. 尝试获取表的基本信息
            logging.info("1. 检查数据库连接...")
            
            # 2. 尝试获取艺术家总数
            count_response = self.supabase.table("artists").select("id", count="exact").execute()
            logging.info(f"艺术家总数: {count_response.count}")
            
            if count_response.count == 0:
                logging.warning("数据库中没有艺术家数据！")
                return False
            
            # 3. 获取前5个艺术家作为样本
            sample_response = self.supabase.table("artists").select(
                "id, name, description, wiki_extract"
            ).limit(5).execute()
            
            if sample_response.data:
                logging.info(f"成功获取 {len(sample_response.data)} 个样本艺术家:")
                for i, artist in enumerate(sample_response.data, 1):
                    name = artist.get("name", "无名称")
                    desc_len = len(artist.get("description", "") or "")
                    wiki_len = len(artist.get("wiki_extract", "") or "")
                    logging.info(f"  {i}. {name} (描述: {desc_len}字符, Wiki: {wiki_len}字符)")
                    
                    # 检查是否有日文内容
                    description = artist.get("description", "")
                    wiki_extract = artist.get("wiki_extract", "")
                    
                    if description:
                        is_jp_desc = self.detect_japanese(description)
                        if is_jp_desc:
                            logging.info(f"     📝 描述包含日文: {description[:100]}...")
                    
                    if wiki_extract:
                        is_jp_wiki = self.detect_japanese(wiki_extract)
                        if is_jp_wiki:
                            logging.info(f"     📖 Wiki包含日文: {wiki_extract[:100]}...")
                
                return True
            else:
                logging.error("无法获取样本数据")
                return False
                
        except Exception as e:
            logging.error(f"数据库调试失败: {e}")
            return False

    def detect_japanese(self, text: str) -> bool:
        """检测文本是否为日文"""
        if not text:
            return False
        
        # 规则1: 检测平假名和片假名
        hiragana_count = len(self.hiragana_pattern.findall(text))
        katakana_count = len(self.katakana_pattern.findall(text))
        
        if hiragana_count > 0 or katakana_count > 0:
            return True
        
        # 规则2: 检查日文特有的助词和表达
        japanese_indicators = [
            r'の', r'は', r'を', r'に', r'で', r'と', r'が', r'から', r'まで',
            r'です', r'ます', r'である', r'として', r'について', r'において'
        ]
        
        for indicator in japanese_indicators:
            if re.search(indicator, text):
                return True
        
        # 规则3: 如果只有汉字，检查是否有中文特征
        kanji_count = len(self.kanji_pattern.findall(text))
        if kanji_count > 0:
            chinese_indicators = [
                r'的', r'了', r'在', r'是', r'有', r'和', r'与', r'及', r'等',
                r'他', r'她', r'我', r'你', r'们', r'这', r'那', r'个'
            ]
            
            has_chinese = any(re.search(indicator, text) for indicator in chinese_indicators)
            
            if not has_chinese:
                total_chars = len(text.replace(' ', '').replace('\n', ''))
                kanji_ratio = kanji_count / total_chars if total_chars > 0 else 0
                
                if kanji_ratio > 0.3:  # 汉字占比超过30%且无中文特征
                    return True
        
        return False

    def extract_proper_nouns(self, text: str) -> List[str]:
        """提取专有名词"""
        proper_nouns = []
        
        for pattern in self.proper_noun_patterns:
            matches = re.findall(pattern, text)
            proper_nouns.extend(matches)
        
        # 去重并过滤常见词
        unique_nouns = list(set(proper_nouns))
        
        # 过滤掉不应该被保护的常见词
        excluded_words = {
            'The', 'This', 'That', 'His', 'Her', 'You', 'Tube', 'And', 'Or', 
            'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'From', 'By'
        }
        
        filtered_nouns = [
            noun for noun in unique_nouns 
            if len(noun.strip()) > 1 and noun.strip() not in excluded_words
        ]
        
        return filtered_nouns

    async def translate_with_proper_nouns_preserved(self, japanese_text: str) -> Optional[str]:
        """翻译日文文本，保留专有名词"""
        try:
            # 提取专有名词
            proper_nouns = self.extract_proper_nouns(japanese_text)
            
            # 构建翻译提示词
            system_prompt = """你是一个专业的日文翻译专家，专门翻译音乐艺术家的介绍。

翻译要求：
1. 将日文准确翻译成中文
2. 保持翻译的流畅性和可读性
3. **绝对不要翻译以下类型的专有名词**：
   - 人名（如：Teo Hirvonen, Pan Hirvonen, Taylor Swift）
   - 乐队名/艺术家名（如：US, Muse, Post Malone, YOASOBI）
   - 地名（如：Finland, Tokyo, New York, Helsinki）
   - 音乐节名称（如：Fuji Rock Festival, Glastonbury）
   - 唱片公司名称（如：Warner Records, Sony Music）
   - 歌曲名和专辑名（保持英文原名）
   - 括号内的英文内容
4. 保持原文的结构和语气
5. 只返回翻译结果，不要添加解释
"""

            user_prompt = f"""请翻译以下日文艺术家介绍：

{japanese_text}

请特别注意保留以下专有名词不翻译：
{', '.join(proper_nouns) if proper_nouns else '（未检测到明显的专有名词，请根据上下文判断）'}

翻译要求：准确、流畅、保留所有专有名词的原文。
"""

            # 调用 AI 翻译
            response = await self.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            translation = response.choices[0].message.content.strip()
            
            # 记录翻译过程
            logging.info(f"原文: {japanese_text[:100]}...")
            logging.info(f"译文: {translation[:100]}...")
            if proper_nouns:
                logging.info(f"保留的专有名词: {proper_nouns}")
            
            return translation
            
        except Exception as e:
            logging.error(f"翻译失败: {e}")
            return None

    async def get_artists_with_japanese_descriptions(self) -> List[Dict[str, Any]]:
        """获取包含日文描述的艺术家"""
        logging.info("正在查找包含日文描述的艺术家...")
        
        try:
            # 获取所有艺术家数据
            response = self.supabase.table("artists").select(
                "id, name, description, wiki_extract"
            ).execute()
            
            logging.info(f"数据库查询状态: {response}")
            
            if not response.data:
                logging.error("数据库查询返回空结果")
                # 尝试调试数据库
                await self.debug_database_info()
                return []
            
            logging.info(f"从数据库获取到 {len(response.data)} 个艺术家")
            
            japanese_artists = []
            
            for artist in response.data:
                artist_name = artist.get("name", "")
                description = artist.get("description", "")
                wiki_extract = artist.get("wiki_extract", "")
                
                # 检查描述或wiki摘要是否包含日文
                has_japanese_desc = self.detect_japanese(description)
                has_japanese_wiki = self.detect_japanese(wiki_extract)
                
                if has_japanese_desc or has_japanese_wiki:
                    artist["has_japanese_desc"] = has_japanese_desc
                    artist["has_japanese_wiki"] = has_japanese_wiki
                    japanese_artists.append(artist)
                    logging.info(f"发现日文内容: {artist_name} (描述: {has_japanese_desc}, Wiki: {has_japanese_wiki})")
            
            logging.info(f"共找到 {len(japanese_artists)} 个包含日文内容的艺术家")
            return japanese_artists
            
        except Exception as e:
            logging.error(f"获取艺术家数据失败: {e}")
            return []

    async def update_artist_in_database(self, artist_id: str, update_data: Dict[str, Any]) -> bool:
        """更新数据库中的艺术家信息"""
        try:
            response = self.supabase.table("artists").update(update_data).eq("id", artist_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"数据库更新失败: {e}")
            return False

    async def translate_artist_descriptions(self):
        """翻译所有日文艺术家描述"""
        # 首先进行数据库调试
        db_ok = await self.debug_database_info()
        if not db_ok:
            logging.error("数据库调试失败，停止执行")
            return
        
        artists_to_translate = await self.get_artists_with_japanese_descriptions()
        
        if not artists_to_translate:
            logging.info("没有找到需要翻译的日文描述")
            return
        
        total = len(artists_to_translate)
        success_count = 0
        failed_artists = []
        
        logging.info(f"=== 开始翻译 {total} 个艺术家的日文描述 ===")
        
        for i, artist in enumerate(artists_to_translate, 1):
            artist_id = artist["id"]
            artist_name = artist["name"]
            
            logging.info(f"\n[{i}/{total}] 处理艺术家: {artist_name}")
            
            try:
                update_data = {}
                
                # 翻译描述
                if artist.get("has_japanese_desc") and artist.get("description"):
                    logging.info("  翻译描述中...")
                    translated_desc = await self.translate_with_proper_nouns_preserved(
                        artist["description"]
                    )
                    if translated_desc:
                        update_data["description"] = translated_desc
                        logging.info(f"  ✅ 描述翻译完成")
                    else:
                        logging.warning(f"  ⚠️ 描述翻译失败")
                
                # 翻译 wiki 摘要
                if artist.get("has_japanese_wiki") and artist.get("wiki_extract"):
                    logging.info("  翻译 Wiki 摘要中...")
                    translated_wiki = await self.translate_with_proper_nouns_preserved(
                        artist["wiki_extract"]
                    )
                    if translated_wiki:
                        update_data["wiki_extract"] = translated_wiki
                        logging.info(f"  ✅ Wiki 摘要翻译完成")
                        
                        # 如果没有描述，使用翻译后的wiki摘要作为描述
                        if not update_data.get("description"):
                            # 截取前200个字符作为描述
                            short_desc = translated_wiki[:200] + "..." if len(translated_wiki) > 200 else translated_wiki
                            update_data["description"] = short_desc
                            logging.info(f"  📝 使用 Wiki 摘要生成描述")
                    else:
                        logging.warning(f"  ⚠️ Wiki 摘要翻译失败")
                
                # 更新数据库
                if update_data:
                    logging.info("  更新数据库中...")
                    success = await self.update_artist_in_database(artist_id, update_data)
                    
                    if success:
                        logging.info(f"  🚀 数据库更新成功: {artist_name}")
                        success_count += 1
                    else:
                        logging.error(f"  ❌ 数据库更新失败: {artist_name}")
                        failed_artists.append(artist_name)
                else:
                    logging.warning(f"  ⚠️ 没有内容需要更新: {artist_name}")
                    
                # 添加延迟避免API限制
                await asyncio.sleep(1)
                
            except Exception as e:
                logging.error(f"  ❌ 处理失败: {artist_name} - {e}")
                failed_artists.append(artist_name)
        
        # 输出总结
        logging.info("\n" + "="*60)
        logging.info("=== 日文描述翻译完成 ===")
        logging.info(f"  总共处理: {total} 个艺术家")
        logging.info(f"  成功翻译: {success_count} 个")
        logging.info(f"  失败: {len(failed_artists)} 个")
        
        if failed_artists:
            logging.info(f"\n失败的艺术家 ({len(failed_artists)} 个):")
            for artist in failed_artists:
                logging.info(f"  - {artist}")
        
        # 保存翻译报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_processed": total,
            "successful": success_count,
            "failed": len(failed_artists),
            "failed_artists": failed_artists
        }
        
        with open("japanese_translation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logging.info(f"\n翻译报告已保存到: japanese_translation_report.json")

async def main():
    """主函数"""
    logging.info("=== 日文艺术家描述翻译脚本启动（调试版） ===")
    
    try:
        translator = JapaneseTranslator()
        await translator.translate_artist_descriptions()
    except ValueError as e:
        logging.error(f"配置错误: {e}")
        logging.error("请确保在环境变量中设置了必要的配置")
        return
    except Exception as e:
        logging.error(f"脚本执行失败: {e}")
        return
    
    logging.info("=== 翻译脚本执行完成 ===")

if __name__ == "__main__":
    asyncio.run(main())