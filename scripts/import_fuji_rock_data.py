#!/usr/bin/env python3
"""
Fuji Rock 2025 数据导入脚本

将收集到的艺术家数据批量导入到 Supabase 数据库中。

使用方法：
python3 scripts/import_fuji_rock_data.py
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any

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
        logging.FileHandler('fuji_rock_data_import.log')
    ]
)

logger = logging.getLogger(__name__)

async def import_artist_data(artist_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    导入单个艺术家的数据到数据库
    
    Args:
        artist_data: 艺术家数据字典
        
    Returns:
        Dict: 导入结果
    """
    from services.artist_db_service import artist_db_service
    from services.ai_description_db_service import ai_description_db_service
    from services.song_db_service import song_db_service
    
    artist_name = artist_data.get("artist_name", "Unknown")
    logger.info(f"🎤 开始导入 {artist_name} 的数据...")
    
    result = {
        "artist_name": artist_name,
        "imported_at": datetime.now().isoformat(),
        "success": True,
        "errors": [],
        "steps_completed": []
    }
    
    try:
        data = artist_data.get("data", {})
        
        # 1. 准备艺术家基本信息
        artist_info = {
            "name": artist_name,
            "is_fuji_rock_artist": True
        }
        
        # 添加 Wikipedia 数据
        if "wikipedia" in data:
            wiki_data = data["wikipedia"]
            artist_info.update({
                "wiki_data": wiki_data,
                "wiki_extract": wiki_data.get("extract", ""),
                "wiki_last_updated": datetime.now().isoformat()
            })
            result["steps_completed"].append("wikipedia_data")
        
        # 添加 Spotify 数据
        if "spotify" in data:
            spotify_data = data["spotify"]
            artist_info.update({
                "spotify_id": spotify_data.get("id"),
                "genres": spotify_data.get("genres", [])
            })
            result["steps_completed"].append("spotify_data")
        
        # 2. 创建或更新艺术家记录
        logger.info(f"  📝 创建艺术家记录...")
        artist_result = await artist_db_service.create_artist(artist_info)
        
        if not artist_result.get("success"):
            # 尝试更新现有记录
            existing_artists = await artist_db_service.search_artists(artist_name)
            if existing_artists.get("success") and existing_artists["data"]:
                artist_id = existing_artists["data"][0]["id"]
                artist_result = await artist_db_service.update_artist(artist_id, artist_info)
            else:
                raise Exception(f"Failed to create/update artist: {artist_result.get('error')}")
        
        artist_id = artist_result["data"]["id"]
        result["artist_id"] = artist_id
        result["steps_completed"].append("artist_created")
        logger.info(f"    ✅ 艺术家记录创建成功 (ID: {artist_id})")
        
        # 3. 导入歌曲数据
        if "spotify" in data and "top_tracks" in data["spotify"]:
            logger.info(f"  🎵 导入热门歌曲...")
            tracks = data["spotify"]["top_tracks"]
            
            songs_data = []
            for track in tracks:
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
            
            if songs_data:
                songs_result = await song_db_service.batch_create_songs(songs_data)
                if songs_result.get("success"):
                    result["steps_completed"].append("songs_imported")
                    logger.info(f"    ✅ 导入 {len(songs_data)} 首歌曲成功")
                else:
                    result["errors"].append(f"Songs import failed: {songs_result.get('error')}")
                    logger.warning(f"    ⚠️ 歌曲导入失败: {songs_result.get('error')}")
        
        # 4. 导入 AI 描述
        if "ai_description" in data:
            logger.info(f"  🤖 导入 AI 描述...")
            ai_data = data["ai_description"]
            
            description_info = {
                "artist_id": artist_id,
                "description": ai_data.get("description", ""),
                "style_intensity": 7,
                "language": "zh",
                "model_used": "deepseek-r1-250120",
                "prompt_version": "v1.0",
                "metadata": {
                    "source": "fuji_rock_2025_collection",
                    "collection_date": artist_data.get("collected_at")
                }
            }
            
            ai_result = await ai_description_db_service.create_description(description_info)
            if ai_result.get("success"):
                result["steps_completed"].append("ai_description_imported")
                logger.info(f"    ✅ AI 描述导入成功")
            else:
                result["errors"].append(f"AI description import failed: {ai_result.get('error')}")
                logger.warning(f"    ⚠️ AI 描述导入失败: {ai_result.get('error')}")
        
        # 5. 计算导入完整性
        total_steps = 4  # artist, songs, ai_description, completion
        completed_steps = len(result["steps_completed"])
        result["import_completeness"] = {
            "completed": completed_steps,
            "total": total_steps,
            "percentage": (completed_steps / total_steps) * 100
        }
        
        logger.info(f"✅ {artist_name} 数据导入完成 ({completed_steps}/{total_steps} 步骤)")
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Import error: {str(e)}")
        logger.error(f"❌ {artist_name} 数据导入失败: {str(e)}")
    
    return result

async def main():
    """主函数"""
    logger.info("🎸 Fuji Rock 2025 数据导入开始")
    logger.info("="*80)
    
    # 读取收集到的数据
    data_file = "data/fuji_rock_2025/fuji_rock_2025_summary.json"
    
    if not os.path.exists(data_file):
        logger.error(f"❌ 数据文件不存在: {data_file}")
        logger.error("请先运行 scripts/collect_fuji_rock_data.py 收集数据")
        return
    
    logger.info(f"📖 读取数据文件: {data_file}")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)
    
    artists_data = summary_data.get("artists", [])
    total_artists = len(artists_data)
    
    if total_artists == 0:
        logger.error("❌ 没有找到艺术家数据")
        return
    
    logger.info(f"📝 将导入 {total_artists} 个艺术家的数据")
    
    # 测试数据库连接
    logger.info("🔗 测试数据库连接...")
    try:
        from services.database_service import database_service
        health_result = await database_service.health_check()
        if not health_result.get("success"):
            logger.error(f"❌ 数据库连接失败: {health_result.get('error')}")
            return
        logger.info("✅ 数据库连接正常")
    except Exception as e:
        logger.error(f"❌ 数据库连接测试失败: {str(e)}")
        return
    
    # 开始导入数据
    all_results = []
    successful_imports = 0
    
    for i, artist_data in enumerate(artists_data, 1):
        if not artist_data.get("success"):
            logger.warning(f"⚠️ 跳过失败的数据收集: {artist_data.get('artist_name')}")
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"进度: {i}/{total_artists} - {artist_data.get('artist_name')}")
        logger.info(f"{'='*60}")
        
        result = await import_artist_data(artist_data)
        all_results.append(result)
        
        if result["success"]:
            successful_imports += 1
        
        # 处理间隔（避免数据库压力）
        if i < total_artists:
            logger.info("⏳ 等待 1 秒...")
            await asyncio.sleep(1)
    
    # 保存导入结果
    import_summary = {
        "import_info": {
            "total_artists": total_artists,
            "successful_imports": successful_imports,
            "success_rate": (successful_imports / total_artists) * 100,
            "imported_at": datetime.now().isoformat()
        },
        "results": all_results
    }
    
    # 创建导入结果目录
    results_dir = "data/import_results"
    os.makedirs(results_dir, exist_ok=True)
    
    results_filename = f"{results_dir}/fuji_rock_2025_import_results.json"
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(import_summary, f, ensure_ascii=False, indent=2)
    
    # 输出最终结果
    logger.info(f"\n{'='*80}")
    logger.info("🎵 数据导入完成！结果摘要:")
    logger.info(f"{'='*80}")
    
    logger.info(f"📊 总计: {total_artists} 个艺术家")
    logger.info(f"✅ 成功: {successful_imports}")
    logger.info(f"❌ 失败: {total_artists - successful_imports}")
    logger.info(f"📈 成功率: {(successful_imports / total_artists * 100):.1f}%")
    
    # 导入完整性统计
    completeness_stats = {}
    for result in all_results:
        if result["success"] and "import_completeness" in result:
            percentage = result["import_completeness"]["percentage"]
            if percentage == 100:
                completeness_stats["完整"] = completeness_stats.get("完整", 0) + 1
            elif percentage >= 75:
                completeness_stats["较完整"] = completeness_stats.get("较完整", 0) + 1
            elif percentage >= 50:
                completeness_stats["部分"] = completeness_stats.get("部分", 0) + 1
            else:
                completeness_stats["不完整"] = completeness_stats.get("不完整", 0) + 1
    
    logger.info(f"\n📋 导入完整性统计:")
    for status, count in completeness_stats.items():
        logger.info(f"   {status}: {count} 个艺术家")
    
    logger.info(f"\n💾 导入结果已保存到:")
    logger.info(f"   📄 结果文件: {results_filename}")
    
    logger.info(f"\n🎸 Fuji Rock 2025 数据导入完成！")

if __name__ == "__main__":
    asyncio.run(main()) 