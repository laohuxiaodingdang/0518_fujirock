#!/usr/bin/env python3
"""
Fuji Rock 2025 艺术家数据收集脚本（无数据库版本）

这个脚本收集 Fuji Rock 2025 的艺术家数据并保存到 JSON 文件中。
不依赖数据库连接，适合网络环境受限的情况。

使用方法：
python3 scripts/collect_fuji_rock_data.py
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

def serialize_for_json(obj):
    """
    将复杂对象转换为可 JSON 序列化的格式
    """
    if hasattr(obj, '__dict__'):
        # 如果对象有 __dict__ 属性，转换为字典
        return obj.__dict__
    elif hasattr(obj, '_asdict'):
        # 如果是 namedtuple，转换为字典
        return obj._asdict()
    elif isinstance(obj, (list, tuple)):
        # 如果是列表或元组，递归处理每个元素
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        # 如果是字典，递归处理每个值
        return {key: serialize_for_json(value) for key, value in obj.items()}
    else:
        # 其他情况，尝试转换为字符串
        try:
            json.dumps(obj)  # 测试是否可以序列化
            return obj
        except (TypeError, ValueError):
            return str(obj)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fuji_rock_data_collection.log')
    ]
)

logger = logging.getLogger(__name__)

# Fuji Rock 2025 艺术家名单（基于官方网站）
FUJI_ROCK_2025_ARTISTS = [
    # 主要艺术家
    "VAMPIRE",
    "Radiohead", 
    "Coldplay",
    "The Strokes",
    "Arctic Monkeys",
    "Tame Impala",
    "Mac Miller",
    "Tyler, The Creator",
    "Billie Eilish",
    "Lana Del Rey",
    
    # 日本艺术家
    "ONE OK ROCK",
    "BABYMETAL",
    "King Gnu",
    "Yoasobi",
    "Official髭男dism",
    
    # 其他国际艺术家
    "Dua Lipa",
    "The Weeknd",
    "Post Malone",
    "Imagine Dragons",
    "Twenty One Pilots",
    "Foo Fighters",
    "Red Hot Chili Peppers",
    "Muse",
    "Gorillaz",
    "Beck"
]

async def collect_artist_data(artist_name: str) -> Dict[str, Any]:
    """
    收集单个艺术家的完整数据
    
    Args:
        artist_name: 艺术家名称
        
    Returns:
        Dict: 艺术家的完整数据
    """
    logger.info(f"🎤 开始收集 {artist_name} 的数据...")
    
    result = {
        "artist_name": artist_name,
        "collected_at": datetime.now().isoformat(),
        "data": {},
        "success": True,
        "errors": []
    }
    
    try:
        from services.wikipedia_service import wikipedia_service
        from services.spotify_service import spotify_service
        from services.openai_service import openai_service
        
        # 1. 收集 Wikipedia 数据
        logger.info(f"  📖 获取 Wikipedia 数据...")
        try:
            wiki_result = await wikipedia_service.get_artist_info(artist_name, "zh")
            if wiki_result:
                result["data"]["wikipedia"] = {
                    "title": wiki_result.title,
                    "extract": wiki_result.extract,
                    "thumbnail": wiki_result.thumbnail.source if wiki_result.thumbnail else None,
                    "categories": wiki_result.categories,
                    "references": [{"title": ref.title, "url": ref.url} for ref in wiki_result.references] if wiki_result.references else []
                }
                logger.info(f"    ✅ Wikipedia 数据收集成功")
            else:
                result["errors"].append("Wikipedia data not found")
                logger.warning(f"    ⚠️ Wikipedia 数据未找到")
        except Exception as e:
            result["errors"].append(f"Wikipedia error: {str(e)}")
            logger.error(f"    ❌ Wikipedia 数据收集失败: {str(e)}")
        
        await asyncio.sleep(1)  # API 限制
        
        # 2. 收集 Spotify 数据
        logger.info(f"  🎧 获取 Spotify 数据...")
        try:
            spotify_result = await spotify_service.get_artist_by_name(artist_name)
            if spotify_result.get("success"):
                spotify_data = spotify_result["data"]
                result["data"]["spotify"] = {
                    "id": spotify_data.get("id"),
                    "name": spotify_data.get("name"),
                    "popularity": spotify_data.get("popularity"),
                    "followers": spotify_data.get("followers", {}).get("total", 0),
                    "genres": spotify_data.get("genres", []),
                    "external_urls": spotify_data.get("external_urls", {}),
                    "images": spotify_data.get("images", [])
                }
                
                # 获取热门歌曲
                spotify_id = spotify_data.get("id")
                if spotify_id:
                    await asyncio.sleep(1)
                    tracks_result = await spotify_service.get_artist_top_tracks(spotify_id, limit=5)
                    if tracks_result.get("success"):
                        result["data"]["spotify"]["top_tracks"] = tracks_result["data"]["tracks"]
                
                logger.info(f"    ✅ Spotify 数据收集成功")
            else:
                result["errors"].append(f"Spotify error: {spotify_result.get('error')}")
                logger.warning(f"    ⚠️ Spotify 数据收集失败: {spotify_result.get('error')}")
        except Exception as e:
            result["errors"].append(f"Spotify error: {str(e)}")
            logger.error(f"    ❌ Spotify 数据收集失败: {str(e)}")
        
        await asyncio.sleep(1)
        
        # 3. 生成 AI 描述
        if result["data"].get("wikipedia"):
            logger.info(f"  🤖 生成 AI 描述...")
            try:
                wiki_extract = result["data"]["wikipedia"]["extract"]
                ai_result = await openai_service.generate_sassy_description(
                    artist_name=artist_name,
                    wiki_content=wiki_extract,
                    style_intensity=7,
                    language="zh"
                )
                if ai_result.get("success"):
                    result["data"]["ai_description"] = ai_result["data"]
                    logger.info(f"    ✅ AI 描述生成成功")
                else:
                    result["errors"].append(f"AI error: {ai_result.get('error')}")
                    logger.warning(f"    ⚠️ AI 描述生成失败: {ai_result.get('error')}")
            except Exception as e:
                result["errors"].append(f"AI error: {str(e)}")
                logger.error(f"    ❌ AI 描述生成失败: {str(e)}")
        
        # 4. 计算数据完整性
        data_sources = ["wikipedia", "spotify", "ai_description"]
        collected_sources = [source for source in data_sources if source in result["data"]]
        result["data_completeness"] = {
            "collected": len(collected_sources),
            "total": len(data_sources),
            "percentage": (len(collected_sources) / len(data_sources)) * 100,
            "sources": collected_sources
        }
        
        logger.info(f"✅ {artist_name} 数据收集完成 ({len(collected_sources)}/{len(data_sources)} 数据源)")
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"General error: {str(e)}")
        logger.error(f"❌ {artist_name} 数据收集失败: {str(e)}")
    
    return result

async def main():
    """主函数"""
    logger.info("🎸 Fuji Rock 2025 艺术家数据收集开始")
    logger.info("="*80)
    
    # 创建输出目录
    output_dir = "data/fuji_rock_2025"
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = []
    successful_collections = 0
    
    # 处理艺术家列表
    total_artists = len(FUJI_ROCK_2025_ARTISTS)
    logger.info(f"📝 将收集 {total_artists} 个艺术家的数据")
    
    for i, artist in enumerate(FUJI_ROCK_2025_ARTISTS, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"进度: {i}/{total_artists} - {artist}")
        logger.info(f"{'='*60}")
        
        result = await collect_artist_data(artist)
        all_results.append(result)
        
        if result["success"]:
            successful_collections += 1
        
        # 保存单个艺术家数据
        artist_filename = f"{output_dir}/{artist.replace(' ', '_').replace(',', '').lower()}.json"
        with open(artist_filename, 'w', encoding='utf-8') as f:
            # 使用序列化函数处理复杂对象
            serializable_result = serialize_for_json(result)
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
        
        # 处理间隔（避免 API 限制）
        if i < total_artists:
            logger.info("⏳ 等待 2 秒...")
            await asyncio.sleep(2)
    
    # 保存汇总数据
    summary = {
        "collection_info": {
            "total_artists": total_artists,
            "successful_collections": successful_collections,
            "success_rate": (successful_collections / total_artists) * 100,
            "collected_at": datetime.now().isoformat(),
            "collection_duration": "N/A"  # 可以添加时间计算
        },
        "artists": all_results
    }
    
    summary_filename = f"{output_dir}/fuji_rock_2025_summary.json"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        # 使用序列化函数处理复杂对象
        serializable_summary = serialize_for_json(summary)
        json.dump(serializable_summary, f, ensure_ascii=False, indent=2)
    
    # 输出最终结果
    logger.info(f"\n{'='*80}")
    logger.info("🎵 数据收集完成！结果摘要:")
    logger.info(f"{'='*80}")
    
    logger.info(f"📊 总计: {total_artists} 个艺术家")
    logger.info(f"✅ 成功: {successful_collections}")
    logger.info(f"❌ 失败: {total_artists - successful_collections}")
    logger.info(f"📈 成功率: {(successful_collections / total_artists * 100):.1f}%")
    
    # 数据完整性统计
    completeness_stats = {}
    for result in all_results:
        if result["success"] and "data_completeness" in result:
            percentage = result["data_completeness"]["percentage"]
            if percentage == 100:
                completeness_stats["完整"] = completeness_stats.get("完整", 0) + 1
            elif percentage >= 66:
                completeness_stats["较完整"] = completeness_stats.get("较完整", 0) + 1
            elif percentage >= 33:
                completeness_stats["部分"] = completeness_stats.get("部分", 0) + 1
            else:
                completeness_stats["不完整"] = completeness_stats.get("不完整", 0) + 1
    
    logger.info(f"\n📋 数据完整性统计:")
    for status, count in completeness_stats.items():
        logger.info(f"   {status}: {count} 个艺术家")
    
    logger.info(f"\n💾 数据已保存到:")
    logger.info(f"   📁 目录: {output_dir}/")
    logger.info(f"   📄 汇总文件: {summary_filename}")
    logger.info(f"   📄 单个文件: {output_dir}/[artist_name].json")
    
    logger.info(f"\n🎸 Fuji Rock 2025 艺术家数据收集完成！")

if __name__ == "__main__":
    asyncio.run(main()) 