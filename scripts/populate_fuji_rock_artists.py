#!/usr/bin/env python3
"""
Fuji Rock 2025 艺术家数据库填充脚本

这个脚本会：
1. 读取 Fuji Rock 2025 的官方艺术家名单
2. 为每个艺术家从 Wikipedia 和 Spotify 获取数据
3. 生成 AI 描述
4. 将所有数据保存到数据库中

使用方法：
python scripts/populate_fuji_rock_artists.py
"""

import asyncio
import logging
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.wikipedia_service import wikipedia_service
from services.spotify_service import spotify_service
from services.openai_service import openai_service
from services.artist_db_service import artist_db_service
from services.song_db_service import song_db_service
from services.ai_description_db_service import ai_description_db_service
from models.database import CreateArtistRequest, CreateSongRequest, CreateAIDescriptionRequest

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fuji_rock_populate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Fuji Rock 2025 艺术家名单（从官方网站提取）
FUJI_ROCK_2025_ARTISTS = [
    # GREEN STAGE - 主舞台艺术家
    "FRED AGAIN..",
    "Vaundy", 
    "HYUKOH",
    "SUNSET ROLLERCOASTER",
    "BRAHMAN",
    "US",
    "VULFPECK",
    "山下達郎",  # Tatsuro Yamashita
    "JAMES BLAKE",
    "STUTS",
    "君島大空",  # Kimishima Osora
    "CA7RIEL & PACO AMOROSO",
    "VAMPIRE WEEKEND",
    "RADWIMPS",
    "LITTLE SIMZ",
    "Creepy Nuts",
    "森山直太朗",  # Naotaro Moriyama
    "PIPERS",
    
    # WHITE STAGE
    "Suchmos",
    "OK GO",
    "MIYAVI",
    "MDOU MOCTAR",
    "ECCA VANDAL",
    "おとぼけビ〜バ〜",  # Otoboke Beaver
    "FOUR TET",
    "BARRY CAN'T SWIM",
    "JJJ",
    "FAYE WEBSTER",
    "BALMING TIGER",
    "FERMIN MUGURUZA",
    "HAIM",
    "羊文学",  # Hitsujibungaku
    "ROYEL OTIS",
    "佐野元春",  # Motoharu Sano
    "SILICA GEL",
    "MONO NO AWARE",
    
    # RED MARQUEE
    "TYCHO",
    "PERFUME GENIUS",
    "青葉市子",  # Ichiko Aoba
    "MARCIN",
    "TOMOO",
    "kurayamisaka",
    "downy",
    "サンボマスター",  # Sambo Master
    "GINGER ROOT",
    "NEWDAD",
    "YHWH NAILGUN",
    "離婚伝説",  # Rikon Densetsu
    "jo0ji",
    "DYGL",
    "THE HIVES",
    "kanekoayano",
    "ENGLISH TEACHER",
    "まらしぃ",  # Marasy
    "MEI SEMONES",
    "T字路s",  # T-jiro-s
    
    # FIELD OF HEAVEN
    "EZRA COLLECTIVE",
    "MAYA DELILAH",
    "PARLOR GREENS",
    "ANSWER TO REMEMBER",
    "KIRINJI",
    "トリプルファイヤー",  # Triple Fire
    "EGO-WRAPPIN'",
    "AFRICAN HEAD CHARGE",
    "THE SKA FLAMES",
    "踊ってばかりの国",  # Odotte Bakari no Kuni
    "THE PANTURAS",
    "mei ehara",
    "GALACTIC",
    "ROBERT RANDOLPH",
    "JAKE SHIMABUKURO BAND",
    "GRACE BOWERS & THE HODGE PODGE",
    "吾妻光良 & The Swinging Boppers",
    "She Her Her Hers",
    
    # PLANET GROOVE
    "坂本慎太郎",  # Shintaro Sakamoto
    "KIASMOS",
    "Joy (Anonymous)",
    "HIROKO YAMAMURA",
    "パソコン音楽クラブ",  # Personal Computer Music Club
    
    # TRIBAL CIRCUS
    "CONFIDENCE MAN",
    "NIGHT TEMPO",
    "JANE REMOVER",
    "JYOTY",
    
    # SUNDAY SESSION
    "勢喜遊",  # Sekiyu
    "Yohji Igarashi",
    "Ovall",
    "Nujabes Metaphorical Ensemble",
    "ATSUO THE PINEAPPLE DONKEY",
    
    # 其他舞台的重要艺术家
    "ROUTE 17 Rock'n'Roll ORCHESTRA",
    "CUMBIA KID",
    "DISCOS FANTASTICO!",
    "DJ GONCHAN",
    "RADICAL MUSIC NETWORK",
    "SOUTH CARNIVAL",
    "SAKURA CIRCUS",
    "苗場音楽突撃隊",  # Naeba Music Assault Squad
    "brkfstblend",
    "E.scene",
    "Khaki",
    "LAUSBUB",
    "のろしレコードと悪魔のいけにえ",
    "BRADIO",
    "EVRAAK",
    "NONE THE WiSER",
    "toconoma",
    "THE BOYS&GIRLS",
    "百々和宏と69ers",
    "NOT WONK",
    "鈴木実貴子ズ",
    "ZION"
]

class FujiRockArtistPopulator:
    """Fuji Rock 艺术家数据库填充器"""
    
    def __init__(self):
        self.processed_artists = []
        self.failed_artists = []
        self.success_count = 0
        self.error_count = 0
    
    async def process_single_artist(self, artist_name: str, delay: float = 1.0) -> Dict[str, Any]:
        """
        处理单个艺术家的完整流程
        
        Args:
            artist_name: 艺术家名称
            delay: API 调用之间的延迟（秒）
            
        Returns:
            处理结果
        """
        logger.info(f"开始处理艺术家: {artist_name}")
        
        try:
            # 检查艺术家是否已存在
            existing_artist = await artist_db_service.get_artist_by_name(artist_name)
            if existing_artist.get("success"):
                logger.info(f"艺术家 {artist_name} 已存在，跳过")
                return {
                    "artist_name": artist_name,
                    "status": "already_exists",
                    "artist_id": existing_artist["data"]["id"]
                }
            
            result = {
                "artist_name": artist_name,
                "status": "processing",
                "steps_completed": [],
                "data": {},
                "errors": []
            }
            
            # 步骤1: 从 Wikipedia 获取信息
            try:
                await asyncio.sleep(delay)  # 避免 API 限制
                wiki_result = await wikipedia_service.get_artist_info(artist_name, "zh")
                if wiki_result.get("success"):
                    result["data"]["wikipedia"] = wiki_result["data"]
                    result["steps_completed"].append("wikipedia_fetched")
                    logger.info(f"✓ Wikipedia 数据获取成功: {artist_name}")
                else:
                    result["errors"].append(f"Wikipedia: {wiki_result.get('error', 'Unknown error')}")
                    logger.warning(f"✗ Wikipedia 数据获取失败: {artist_name}")
            except Exception as e:
                result["errors"].append(f"Wikipedia exception: {str(e)}")
                logger.error(f"✗ Wikipedia API 异常: {artist_name} - {str(e)}")
            
            # 步骤2: 从 Spotify 获取艺术家信息
            try:
                await asyncio.sleep(delay)
                spotify_artist_result = await spotify_service.get_artist_by_name(artist_name)
                if spotify_artist_result.get("success"):
                    result["data"]["spotify_artist"] = spotify_artist_result["data"]
                    result["steps_completed"].append("spotify_artist_fetched")
                    logger.info(f"✓ Spotify 艺术家数据获取成功: {artist_name}")
                    
                    # 获取热门歌曲
                    spotify_id = spotify_artist_result["data"].get("id")
                    if spotify_id:
                        await asyncio.sleep(delay)
                        tracks_result = await spotify_service.get_artist_top_tracks(spotify_id)
                        if tracks_result.get("success"):
                            result["data"]["spotify_tracks"] = tracks_result["data"]
                            result["steps_completed"].append("spotify_tracks_fetched")
                            logger.info(f"✓ Spotify 歌曲数据获取成功: {artist_name}")
                else:
                    result["errors"].append(f"Spotify: {spotify_artist_result.get('error', 'Unknown error')}")
                    logger.warning(f"✗ Spotify 数据获取失败: {artist_name}")
            except Exception as e:
                result["errors"].append(f"Spotify exception: {str(e)}")
                logger.error(f"✗ Spotify API 异常: {artist_name} - {str(e)}")
            
            # 步骤3: 生成 AI 描述
            try:
                if result["data"].get("wikipedia"):
                    await asyncio.sleep(delay)
                    wiki_extract = result["data"]["wikipedia"].get("extract", "")
                    ai_result = await openai_service.generate_sassy_description(
                        artist_name=artist_name,
                        wiki_content=wiki_extract,
                        style_intensity=8,
                        language="zh"
                    )
                    if ai_result.get("success"):
                        result["data"]["ai_description"] = ai_result["data"]
                        result["steps_completed"].append("ai_description_generated")
                        logger.info(f"✓ AI 描述生成成功: {artist_name}")
                    else:
                        result["errors"].append(f"AI: {ai_result.get('error', 'Unknown error')}")
                        logger.warning(f"✗ AI 描述生成失败: {artist_name}")
            except Exception as e:
                result["errors"].append(f"AI exception: {str(e)}")
                logger.error(f"✗ AI API 异常: {artist_name} - {str(e)}")
            
            # 步骤4: 保存到数据库
            try:
                # 4.1 创建艺术家记录
                artist_data = CreateArtistRequest(
                    name=artist_name,
                    description=result["data"].get("wikipedia", {}).get("extract", "")[:500] if result["data"].get("wikipedia") else None,
                    genres=result["data"].get("spotify_artist", {}).get("genres", []) if result["data"].get("spotify_artist") else None,
                    is_fuji_rock_artist=True  # 标记为 Fuji Rock 艺术家
                )
                
                artist_create_result = await artist_db_service.create_artist(artist_data)
                if artist_create_result.get("success"):
                    artist_id = artist_create_result["data"]["id"]
                    result["data"]["artist_id"] = artist_id
                    result["steps_completed"].append("artist_created")
                    logger.info(f"✓ 艺术家记录创建成功: {artist_name}")
                    
                    # 4.2 更新 Wikipedia 数据
                    if result["data"].get("wikipedia"):
                        wiki_update_result = await artist_db_service.update_artist_wikipedia_data(
                            artist_id,
                            result["data"]["wikipedia"],
                            result["data"]["wikipedia"].get("extract", "")
                        )
                        if wiki_update_result.get("success"):
                            result["steps_completed"].append("wikipedia_data_updated")
                    
                    # 4.3 更新 Spotify 数据
                    if result["data"].get("spotify_artist"):
                        spotify_update_result = await artist_db_service.update_artist_spotify_data(
                            artist_id,
                            result["data"]["spotify_artist"],
                            result["data"]["spotify_artist"].get("id")
                        )
                        if spotify_update_result.get("success"):
                            result["steps_completed"].append("spotify_data_updated")
                    
                    # 4.4 保存 AI 描述
                    if result["data"].get("ai_description"):
                        ai_desc_data = CreateAIDescriptionRequest(
                            artist_id=artist_id,
                            content=result["data"]["ai_description"]["sassy_description"],
                            language="zh",
                            source_content=result["data"].get("wikipedia", {}).get("extract", ""),
                            tokens_used=result["data"]["ai_description"].get("tokens_used"),
                            generation_time_ms=result["data"]["ai_description"].get("generation_time_ms")
                        )
                        
                        ai_create_result = await ai_description_db_service.create_ai_description(ai_desc_data)
                        if ai_create_result.get("success"):
                            result["steps_completed"].append("ai_description_saved")
                    
                    # 4.5 批量保存歌曲
                    if result["data"].get("spotify_tracks"):
                        songs_data = []
                        for track in result["data"]["spotify_tracks"]["tracks"][:10]:  # 限制前10首
                            song_data = CreateSongRequest(
                                artist_id=artist_id,
                                title=track["name"],
                                album_name=track.get("album", {}).get("name"),
                                duration_seconds=track.get("duration_ms", 0) // 1000,
                                preview_url=track.get("preview_url"),
                                spotify_id=track.get("id")
                            )
                            songs_data.append(song_data)
                        
                        if songs_data:
                            songs_create_result = await song_db_service.batch_create_songs(songs_data)
                            if songs_create_result.get("success"):
                                result["steps_completed"].append(f"songs_saved_{len(songs_data)}")
                    
                    result["status"] = "completed"
                    self.success_count += 1
                    logger.info(f"✅ 艺术家 {artist_name} 处理完成")
                    
                else:
                    result["errors"].append(f"Database: {artist_create_result.get('error')}")
                    result["status"] = "failed"
                    self.error_count += 1
                    logger.error(f"❌ 艺术家 {artist_name} 数据库保存失败")
                    
            except Exception as e:
                result["errors"].append(f"Database exception: {str(e)}")
                result["status"] = "failed"
                self.error_count += 1
                logger.error(f"❌ 艺术家 {artist_name} 数据库操作异常: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 艺术家 {artist_name} 处理过程中发生异常: {str(e)}")
            self.error_count += 1
            return {
                "artist_name": artist_name,
                "status": "failed",
                "errors": [f"General exception: {str(e)}"]
            }
    
    async def populate_all_artists(self, batch_size: int = 5, delay: float = 2.0):
        """
        批量处理所有艺术家
        
        Args:
            batch_size: 批处理大小
            delay: API 调用之间的延迟（秒）
        """
        logger.info(f"开始批量处理 {len(FUJI_ROCK_2025_ARTISTS)} 个 Fuji Rock 2025 艺术家")
        logger.info(f"批处理大小: {batch_size}, API 延迟: {delay}秒")
        
        total_artists = len(FUJI_ROCK_2025_ARTISTS)
        
        # 分批处理艺术家
        for i in range(0, total_artists, batch_size):
            batch = FUJI_ROCK_2025_ARTISTS[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_artists + batch_size - 1) // batch_size
            
            logger.info(f"\n🔄 处理批次 {batch_num}/{total_batches}: {batch}")
            
            # 并发处理当前批次
            tasks = [self.process_single_artist(artist, delay) for artist in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 记录批次结果
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"批次处理异常: {str(result)}")
                    self.failed_artists.append({"error": str(result)})
                else:
                    self.processed_artists.append(result)
                    if result["status"] == "failed":
                        self.failed_artists.append(result)
            
            # 批次间休息
            if i + batch_size < total_artists:
                logger.info(f"批次 {batch_num} 完成，休息 {delay * 2} 秒...")
                await asyncio.sleep(delay * 2)
        
        # 输出最终统计
        self.print_final_summary()
    
    def print_final_summary(self):
        """打印最终处理摘要"""
        logger.info("\n" + "="*80)
        logger.info("🎵 FUJI ROCK 2025 艺术家数据库填充完成！")
        logger.info("="*80)
        logger.info(f"📊 处理统计:")
        logger.info(f"   总艺术家数: {len(FUJI_ROCK_2025_ARTISTS)}")
        logger.info(f"   成功处理: {self.success_count}")
        logger.info(f"   处理失败: {self.error_count}")
        logger.info(f"   成功率: {(self.success_count / len(FUJI_ROCK_2025_ARTISTS) * 100):.1f}%")
        
        if self.failed_artists:
            logger.info(f"\n❌ 失败的艺术家:")
            for failed in self.failed_artists:
                artist_name = failed.get("artist_name", "Unknown")
                errors = failed.get("errors", ["Unknown error"])
                logger.info(f"   - {artist_name}: {', '.join(errors)}")
        
        logger.info(f"\n✅ 成功处理的艺术家:")
        successful_artists = [a for a in self.processed_artists if a["status"] in ["completed", "already_exists"]]
        for artist in successful_artists:
            steps = len(artist.get("steps_completed", []))
            logger.info(f"   - {artist['artist_name']} ({steps} 步骤完成)")
        
        logger.info("\n🎸 数据库现在包含了 Fuji Rock 2025 的艺术家信息！")
        logger.info("   可以通过以下 API 查看:")
        logger.info("   - GET /api/database/artists/fuji-rock")
        logger.info("   - GET /api/database/artists?query=艺术家名称")
        logger.info("="*80)

async def main():
    """主函数"""
    logger.info("🎵 Fuji Rock 2025 艺术家数据库填充脚本启动")
    
    # 检查数据库连接
    from services.database_service import db_service
    if not db_service.is_connected():
        logger.error("❌ 数据库连接失败，请检查 Supabase 配置")
        return
    
    # 测试数据库连接
    test_result = await db_service.test_connection()
    if not test_result.get("success"):
        logger.error(f"❌ 数据库连接测试失败: {test_result.get('error')}")
        return
    
    logger.info("✅ 数据库连接正常")
    
    # 创建填充器并开始处理
    populator = FujiRockArtistPopulator()
    
    try:
        # 可以调整这些参数来控制处理速度和 API 限制
        await populator.populate_all_artists(
            batch_size=3,  # 每批处理3个艺术家
            delay=1.5      # API 调用间隔1.5秒
        )
    except KeyboardInterrupt:
        logger.info("\n⏹️  用户中断，正在保存已处理的结果...")
        populator.print_final_summary()
    except Exception as e:
        logger.error(f"❌ 处理过程中发生异常: {str(e)}")
        populator.print_final_summary()

if __name__ == "__main__":
    asyncio.run(main()) 