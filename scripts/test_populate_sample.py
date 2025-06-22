#!/usr/bin/env python3
"""
Fuji Rock 2025 艺术家数据库填充测试脚本

这个脚本用于测试数据库填充功能，只处理几个知名艺术家。

使用方法：
python3 scripts/test_populate_sample.py
"""

import asyncio
import logging
import sys
import os
from typing import List, Dict, Any

# 首先加载环境变量（在导入任何配置之前）
from dotenv import load_dotenv
load_dotenv()

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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试用的艺术家名单（选择一些知名度高的艺术家）
TEST_ARTISTS = [
    "VAMPIRE WEEKEND",
    "RADWIMPS", 
    "JAMES BLAKE",
    "FOUR TET",
    "THE HIVES"
]

async def process_test_artist(artist_name: str) -> Dict[str, Any]:
    """处理单个测试艺术家"""
    logger.info(f"🎵 开始处理艺术家: {artist_name}")
    
    result = {
        "artist_name": artist_name,
        "steps": [],
        "data": {},
        "success": True
    }
    
    try:
        # 1. 检查是否已存在
        existing = await artist_db_service.get_artist_by_name(artist_name)
        if existing.get("success"):
            logger.info(f"✅ 艺术家 {artist_name} 已存在")
            result["steps"].append("already_exists")
            return result
        
        # 2. 获取 Wikipedia 数据
        logger.info(f"📖 获取 Wikipedia 数据: {artist_name}")
        wiki_result = await wikipedia_service.get_artist_info(artist_name, "zh")
        if wiki_result:  # WikipediaData 对象存在
            # 转换为字典格式
            wiki_data = {
                "title": wiki_result.title,
                "extract": wiki_result.extract,
                "thumbnail": wiki_result.thumbnail.source if wiki_result.thumbnail else None,
                "categories": wiki_result.categories,
                "references": [{"title": ref.title, "url": ref.url} for ref in wiki_result.references] if wiki_result.references else []
            }
            result["data"]["wikipedia"] = wiki_data
            result["steps"].append("wikipedia_ok")
            logger.info(f"✅ Wikipedia 数据获取成功")
        else:
            logger.warning(f"⚠️ Wikipedia 数据获取失败")
        
        await asyncio.sleep(1)  # API 限制
        
        # 3. 获取 Spotify 数据
        logger.info(f"🎧 获取 Spotify 数据: {artist_name}")
        spotify_result = await spotify_service.get_artist_by_name(artist_name)
        if spotify_result.get("success"):
            result["data"]["spotify"] = spotify_result["data"]
            result["steps"].append("spotify_ok")
            logger.info(f"✅ Spotify 数据获取成功")
            
            # 获取热门歌曲
            spotify_id = spotify_result["data"].get("id")
            if spotify_id:
                await asyncio.sleep(1)
                tracks_result = await spotify_service.get_artist_top_tracks(spotify_id)
                if tracks_result.get("success"):
                    result["data"]["tracks"] = tracks_result["data"]
                    result["steps"].append("tracks_ok")
                    logger.info(f"✅ 热门歌曲获取成功")
        else:
            logger.warning(f"⚠️ Spotify 数据获取失败: {spotify_result.get('error')}")
        
        await asyncio.sleep(1)
        
        # 4. 生成 AI 描述
        if result["data"].get("wikipedia"):
            logger.info(f"🤖 生成 AI 描述: {artist_name}")
            wiki_extract = result["data"]["wikipedia"].get("extract", "")
            ai_result = await openai_service.generate_sassy_description(
                artist_name=artist_name,
                wiki_content=wiki_extract,
                style_intensity=7,
                language="zh"
            )
            if ai_result.get("success"):
                result["data"]["ai"] = ai_result["data"]
                result["steps"].append("ai_ok")
                logger.info(f"✅ AI 描述生成成功")
            else:
                logger.warning(f"⚠️ AI 描述生成失败: {ai_result.get('error')}")
        
        # 5. 保存到数据库
        logger.info(f"💾 保存到数据库: {artist_name}")
        
        # 创建艺术家
        artist_data = CreateArtistRequest(
            name=artist_name,
            description=result["data"].get("wikipedia", {}).get("extract", "")[:500] if result["data"].get("wikipedia") else None,
            genres=result["data"].get("spotify", {}).get("genres", []) if result["data"].get("spotify") else None,
            is_fuji_rock_artist=True
        )
        
        create_result = await artist_db_service.create_artist(artist_data)
        if create_result.get("success"):
            artist_id = create_result["data"]["id"]
            result["data"]["artist_id"] = artist_id
            result["steps"].append("artist_created")
            logger.info(f"✅ 艺术家记录创建成功")
            
            # 更新 Wikipedia 数据
            if result["data"].get("wikipedia"):
                await artist_db_service.update_artist_wikipedia_data(
                    artist_id,
                    result["data"]["wikipedia"],
                    result["data"]["wikipedia"].get("extract", "")
                )
                result["steps"].append("wiki_updated")
            
            # 更新 Spotify 数据
            if result["data"].get("spotify"):
                await artist_db_service.update_artist_spotify_data(
                    artist_id,
                    result["data"]["spotify"],
                    result["data"]["spotify"].get("id")
                )
                result["steps"].append("spotify_updated")
            
            # 保存 AI 描述
            if result["data"].get("ai"):
                ai_desc = CreateAIDescriptionRequest(
                    artist_id=artist_id,
                    content=result["data"]["ai"]["sassy_description"],
                    language="zh",
                    source_content=result["data"].get("wikipedia", {}).get("extract", ""),
                    tokens_used=result["data"]["ai"].get("tokens_used"),
                    generation_time_ms=result["data"]["ai"].get("generation_time_ms")
                )
                await ai_description_db_service.create_ai_description(ai_desc)
                result["steps"].append("ai_saved")
            
            # 保存歌曲
            if result["data"].get("tracks"):
                songs_data = []
                for track in result["data"]["tracks"]["tracks"][:5]:  # 只保存前5首
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
                    await song_db_service.batch_create_songs(songs_data)
                    result["steps"].append(f"songs_saved_{len(songs_data)}")
            
            logger.info(f"🎉 艺术家 {artist_name} 处理完成！")
        else:
            logger.error(f"❌ 数据库保存失败: {create_result.get('error')}")
            result["success"] = False
    
    except Exception as e:
        logger.error(f"❌ 处理 {artist_name} 时发生异常: {str(e)}")
        result["success"] = False
        result["error"] = str(e)
    
    return result

async def main():
    """主函数"""
    logger.info("🎸 Fuji Rock 2025 艺术家数据库填充测试开始")
    
    # 检查数据库连接
    from services.database_service import db_service
    if not db_service.is_connected():
        logger.error("❌ 数据库连接失败，请检查 Supabase 配置")
        return
    
    test_result = await db_service.test_connection()
    if not test_result.get("success"):
        logger.error(f"❌ 数据库连接测试失败: {test_result.get('error')}")
        return
    
    logger.info("✅ 数据库连接正常")
    logger.info(f"📝 将处理 {len(TEST_ARTISTS)} 个测试艺术家")
    
    results = []
    
    # 逐个处理艺术家
    for i, artist in enumerate(TEST_ARTISTS, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"处理进度: {i}/{len(TEST_ARTISTS)} - {artist}")
        logger.info(f"{'='*60}")
        
        result = await process_test_artist(artist)
        results.append(result)
        
        # 处理间隔
        if i < len(TEST_ARTISTS):
            logger.info("⏳ 等待 2 秒...")
            await asyncio.sleep(2)
    
    # 输出最终结果
    logger.info(f"\n{'='*80}")
    logger.info("🎵 测试完成！结果摘要:")
    logger.info(f"{'='*80}")
    
    success_count = sum(1 for r in results if r["success"])
    
    logger.info(f"📊 总计: {len(results)} 个艺术家")
    logger.info(f"✅ 成功: {success_count}")
    logger.info(f"❌ 失败: {len(results) - success_count}")
    logger.info(f"📈 成功率: {(success_count / len(results) * 100):.1f}%")
    
    logger.info(f"\n📋 详细结果:")
    for result in results:
        artist_name = result["artist_name"]
        steps = len(result["steps"])
        status = "✅" if result["success"] else "❌"
        logger.info(f"   {status} {artist_name}: {steps} 步骤完成")
        if result["steps"]:
            logger.info(f"      步骤: {', '.join(result['steps'])}")
    
    logger.info(f"\n🔍 可以通过以下方式查看结果:")
    logger.info(f"   - 访问 http://localhost:8000/api/database/artists/fuji-rock")
    logger.info(f"   - 访问 http://localhost:8000/docs 查看 API 文档")
    logger.info(f"   - 搜索艺术家: http://localhost:8000/api/database/artists?query=VAMPIRE")
    
    logger.info(f"\n🎸 测试完成！数据库已包含 Fuji Rock 2025 艺术家数据。")

if __name__ == "__main__":
    asyncio.run(main()) 