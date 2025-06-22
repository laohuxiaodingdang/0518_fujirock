#!/usr/bin/env python3
"""
Fred again.. 艺术家数据收集和导入脚本

收集 Fred again.. 的完整数据并直接导入到数据库中。

使用方法：
python3 scripts/collect_fred_again_data.py
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 首先加载环境变量（在导入任何配置之前）
from dotenv import load_dotenv
load_dotenv()

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fred_again_data_collection.log')
    ]
)

logger = logging.getLogger(__name__)

async def collect_and_import_fred_again():
    """收集 Fred again.. 的数据并导入到数据库"""
    
    artist_name = "Fred again.."
    logger.info(f"🎤 开始收集和导入 {artist_name} 的数据...")
    
    try:
        from services.wikipedia_service import wikipedia_service
        from services.spotify_service import spotify_service
        from services.openai_service import openai_service
        from services.artist_db_service import artist_db_service
        from services.ai_description_db_service import ai_description_db_service
        from services.song_db_service import song_db_service
        from services.database_service import db_service
        
        # 测试数据库连接
        logger.info("🔗 测试数据库连接...")
        health_result = await db_service.test_connection()
        if not health_result.get("success"):
            logger.error(f"❌ 数据库连接失败: {health_result.get('error')}")
            return
        logger.info("✅ 数据库连接正常")
        
        # 准备艺术家信息
        artist_info = {
            "name": artist_name,
            "is_fuji_rock_artist": True
        }
        
        # 1. 收集 Wikipedia 数据
        logger.info(f"📖 获取 Wikipedia 数据...")
        try:
            wiki_result = await wikipedia_service.get_artist_info(artist_name, "zh")
            if wiki_result:
                wiki_data = {
                    "title": wiki_result.title,
                    "extract": wiki_result.extract,
                    "thumbnail": wiki_result.thumbnail.source if wiki_result.thumbnail else None,
                    "categories": wiki_result.categories,
                    "references": [{"title": ref.title, "url": ref.url} for ref in wiki_result.references] if wiki_result.references else []
                }
                artist_info.update({
                    "wiki_data": wiki_data,
                    "wiki_extract": wiki_result.extract,
                    "wiki_last_updated": datetime.now().isoformat()
                })
                logger.info(f"✅ Wikipedia 数据收集成功")
            else:
                logger.warning(f"⚠️ Wikipedia 数据未找到")
        except Exception as e:
            logger.error(f"❌ Wikipedia 数据收集失败: {str(e)}")
        
        await asyncio.sleep(1)
        
        # 2. 收集 Spotify 数据
        logger.info(f"🎧 获取 Spotify 数据...")
        spotify_tracks = []
        try:
            spotify_result = await spotify_service.get_artist_by_name(artist_name)
            if spotify_result.get("success"):
                spotify_data = spotify_result["data"]
                artist_info.update({
                    "spotify_id": spotify_data.get("id"),
                    "genres": spotify_data.get("genres", [])
                })
                
                # 获取热门歌曲
                spotify_id = spotify_data.get("id")
                if spotify_id:
                    await asyncio.sleep(1)
                    tracks_result = await spotify_service.get_artist_top_tracks(spotify_id, limit=10)
                    if tracks_result.get("success"):
                        spotify_tracks = tracks_result["data"]["tracks"]
                
                logger.info(f"✅ Spotify 数据收集成功")
            else:
                logger.warning(f"⚠️ Spotify 数据收集失败: {spotify_result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Spotify 数据收集失败: {str(e)}")
        
        await asyncio.sleep(1)
        
        # 3. 创建或更新艺术家记录
        logger.info(f"📝 创建艺术家记录...")
        artist_result = await artist_db_service.create_artist(artist_info)
        
        if not artist_result.get("success"):
            # 尝试更新现有记录
            existing_artists = await artist_db_service.search_artists(artist_name)
            if existing_artists.get("success") and existing_artists["data"]:
                artist_id = existing_artists["data"][0]["id"]
                artist_result = await artist_db_service.update_artist(artist_id, artist_info)
                logger.info(f"✅ 艺术家记录更新成功 (ID: {artist_id})")
            else:
                logger.error(f"❌ 艺术家记录创建失败: {artist_result.get('error')}")
                return
        else:
            artist_id = artist_result["data"]["id"]
            logger.info(f"✅ 艺术家记录创建成功 (ID: {artist_id})")
        
        # 4. 导入歌曲数据
        if spotify_tracks:
            logger.info(f"🎵 导入热门歌曲...")
            songs_data = []
            for track in spotify_tracks:
                song_info = {
                    "title": track.get("name", ""),
                    "artist_id": artist_id,
                    "spotify_id": track.get("id"),
                    "duration_ms": track.get("duration_ms"),
                    "popularity": track.get("popularity"),
                    "preview_url": track.get("preview_url"),
                    "external_urls": track.get("external_urls", {}),
                    "is_fuji_rock_related": True
                }
                songs_data.append(song_info)
            
            songs_result = await song_db_service.batch_create_songs(songs_data)
            if songs_result.get("success"):
                logger.info(f"✅ 导入 {len(songs_data)} 首歌曲成功")
            else:
                logger.warning(f"⚠️ 歌曲导入失败: {songs_result.get('error')}")
        
        # 5. 生成并导入 AI 描述
        if artist_info.get("wiki_extract"):
            logger.info(f"🤖 生成 AI 描述...")
            try:
                ai_result = await openai_service.generate_sassy_description(
                    artist_name=artist_name,
                    wiki_content=artist_info["wiki_extract"],
                    style_intensity=7,
                    language="zh"
                )
                if ai_result.get("success"):
                    ai_data = ai_result["data"]
                    
                    description_info = {
                        "artist_id": artist_id,
                        "description": ai_data.get("description", ""),
                        "style_intensity": 7,
                        "language": "zh",
                        "model_used": "deepseek-r1-250120",
                        "prompt_version": "v1.0",
                        "metadata": {
                            "source": "fred_again_collection",
                            "collection_date": datetime.now().isoformat()
                        }
                    }
                    
                    ai_db_result = await ai_description_db_service.create_description(description_info)
                    if ai_db_result.get("success"):
                        logger.info(f"✅ AI 描述生成并导入成功")
                    else:
                        logger.warning(f"⚠️ AI 描述导入失败: {ai_db_result.get('error')}")
                else:
                    logger.warning(f"⚠️ AI 描述生成失败: {ai_result.get('error')}")
            except Exception as e:
                logger.error(f"❌ AI 描述生成失败: {str(e)}")
        
        logger.info(f"🎉 {artist_name} 数据收集和导入完成！")
        logger.info(f"📊 艺术家 ID: {artist_id}")
        
        return {
            "success": True,
            "artist_id": artist_id,
            "artist_name": artist_name
        }
        
    except Exception as e:
        logger.error(f"❌ {artist_name} 数据收集和导入失败: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def main():
    """主函数"""
    logger.info("🎸 Fred again.. 数据收集和导入开始")
    logger.info("="*60)
    
    result = await collect_and_import_fred_again()
    
    if result.get("success"):
        logger.info(f"\n✅ 成功完成 Fred again.. 数据导入！")
        logger.info(f"🆔 艺术家 ID: {result['artist_id']}")
        logger.info(f"🎤 艺术家名称: {result['artist_name']}")
    else:
        logger.error(f"\n❌ Fred again.. 数据导入失败: {result.get('error')}")
    
    logger.info("🎸 Fred again.. 数据收集和导入完成！")

if __name__ == "__main__":
    asyncio.run(main()) 