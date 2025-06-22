#!/usr/bin/env python3
"""
基础 API 测试脚本

这个脚本测试基本的 API 功能，不依赖数据库连接。
用于验证 Wikipedia、Spotify 和 AI 服务是否正常工作。

使用方法：
python3 scripts/test_basic_apis.py
"""

import asyncio
import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_basic_apis.log')
    ]
)

logger = logging.getLogger(__name__)

# 测试艺术家列表
TEST_ARTISTS = [
    "Radiohead",
    "VAMPIRE",
    "Coldplay"
]

async def test_wikipedia_service():
    """测试 Wikipedia 服务"""
    logger.info("🔍 测试 Wikipedia 服务...")
    
    try:
        from services.wikipedia_service import wikipedia_service
        
        for artist in TEST_ARTISTS:
            logger.info(f"  测试艺术家: {artist}")
            result = await wikipedia_service.get_artist_info(artist, "zh")
            
            if result:
                logger.info(f"    ✅ 成功获取 {artist} 的 Wikipedia 数据")
                logger.info(f"    📝 标题: {result.title}")
                logger.info(f"    📄 摘要: {result.extract[:100]}...")
                if result.thumbnail:
                    logger.info(f"    🖼️ 图片: {result.thumbnail.source}")
            else:
                logger.warning(f"    ⚠️ 未获取到 {artist} 的数据")
            
            await asyncio.sleep(1)  # 避免请求过快
        
        logger.info("✅ Wikipedia 服务测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ Wikipedia 服务测试失败: {str(e)}")
        return False

async def test_spotify_service():
    """测试 Spotify 服务"""
    logger.info("🎵 测试 Spotify 服务...")
    
    try:
        from services.spotify_service import spotify_service
        
        for artist in TEST_ARTISTS:
            logger.info(f"  测试艺术家: {artist}")
            result = await spotify_service.get_artist_by_name(artist)
            
            if result.get("success"):
                data = result["data"]
                logger.info(f"    ✅ 成功获取 {artist} 的 Spotify 数据")
                logger.info(f"    🎤 艺术家: {data.get('name')}")
                logger.info(f"    👥 粉丝数: {data.get('followers', {}).get('total', 0):,}")
                logger.info(f"    🎭 风格: {', '.join(data.get('genres', [])[:3])}")
                
                # 测试获取热门歌曲
                spotify_id = data.get("id")
                if spotify_id:
                    await asyncio.sleep(1)
                    tracks_result = await spotify_service.get_artist_top_tracks(spotify_id)
                    if tracks_result.get("success"):
                        tracks = tracks_result["data"]["tracks"]
                        logger.info(f"    🎵 热门歌曲数量: {len(tracks)}")
                        if tracks:
                            logger.info(f"    🔥 最热门: {tracks[0]['name']}")
            else:
                logger.warning(f"    ⚠️ 未获取到 {artist} 的 Spotify 数据: {result.get('error')}")
            
            await asyncio.sleep(1)
        
        logger.info("✅ Spotify 服务测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ Spotify 服务测试失败: {str(e)}")
        return False

async def test_ai_service():
    """测试 AI 服务"""
    logger.info("🤖 测试 AI 服务...")
    
    try:
        from services.openai_service import openai_service
        
        # 使用一个简单的测试内容
        test_content = "Radiohead是一支来自英国的摇滚乐队，以其实验性音乐风格而闻名。"
        
        logger.info("  测试 AI 描述生成...")
        result = await openai_service.generate_sassy_description(
            artist_name="Radiohead",
            wiki_content=test_content,
            style_intensity=7,
            language="zh"
        )
        
        if result.get("success"):
            data = result["data"]
            logger.info("    ✅ 成功生成 AI 描述")
            logger.info(f"    📝 描述长度: {len(data['sassy_description'])} 字符")
            logger.info(f"    🎭 幽默程度: {data['style_metrics']['humor_level']}/10")
            logger.info(f"    😏 讽刺程度: {data['style_metrics']['sarcasm_level']}/10")
            logger.info(f"    📊 模型: {data['model_used']}")
            logger.info(f"    🔤 Token 使用: {data.get('tokens_used', 'N/A')}")
            logger.info(f"    📄 生成内容预览: {data['sassy_description'][:150]}...")
        else:
            logger.warning(f"    ⚠️ AI 描述生成失败: {result.get('error')}")
        
        logger.info("✅ AI 服务测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ AI 服务测试失败: {str(e)}")
        return False

async def test_integration_workflow():
    """测试完整的集成工作流"""
    logger.info("🔄 测试完整集成工作流...")
    
    try:
        from services.wikipedia_service import wikipedia_service
        from services.spotify_service import spotify_service
        from services.openai_service import openai_service
        
        artist_name = "VAMPIRE"
        logger.info(f"  测试艺术家: {artist_name}")
        
        # 1. 获取 Wikipedia 数据
        logger.info("    1️⃣ 获取 Wikipedia 数据...")
        wiki_result = await wikipedia_service.get_artist_info(artist_name, "zh")
        wiki_content = ""
        if wiki_result:
            wiki_content = wiki_result.extract
            logger.info(f"       ✅ Wikipedia 数据获取成功")
        else:
            logger.warning(f"       ⚠️ Wikipedia 数据获取失败")
        
        await asyncio.sleep(1)
        
        # 2. 获取 Spotify 数据
        logger.info("    2️⃣ 获取 Spotify 数据...")
        spotify_result = await spotify_service.get_artist_by_name(artist_name)
        spotify_data = None
        if spotify_result.get("success"):
            spotify_data = spotify_result["data"]
            logger.info(f"       ✅ Spotify 数据获取成功")
        else:
            logger.warning(f"       ⚠️ Spotify 数据获取失败")
        
        await asyncio.sleep(1)
        
        # 3. 生成 AI 描述
        if wiki_content:
            logger.info("    3️⃣ 生成 AI 描述...")
            ai_result = await openai_service.generate_sassy_description(
                artist_name=artist_name,
                wiki_content=wiki_content,
                style_intensity=8,
                language="zh"
            )
            if ai_result.get("success"):
                logger.info(f"       ✅ AI 描述生成成功")
            else:
                logger.warning(f"       ⚠️ AI 描述生成失败")
        
        logger.info("✅ 集成工作流测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 集成工作流测试失败: {str(e)}")
        return False

async def main():
    """主函数"""
    logger.info("🎸 Fuji Rock 2025 基础 API 测试开始")
    logger.info("="*60)
    
    results = {}
    
    # 测试各个服务
    results["wikipedia"] = await test_wikipedia_service()
    logger.info("")
    
    results["spotify"] = await test_spotify_service()
    logger.info("")
    
    results["ai"] = await test_ai_service()
    logger.info("")
    
    results["integration"] = await test_integration_workflow()
    logger.info("")
    
    # 输出测试结果摘要
    logger.info("="*60)
    logger.info("🎵 测试结果摘要:")
    logger.info("="*60)
    
    success_count = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    for service, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        logger.info(f"  {service.capitalize():12} : {status}")
    
    logger.info(f"\n📊 总体结果: {success_count}/{total_tests} 测试通过")
    success_rate = (success_count / total_tests) * 100
    logger.info(f"📈 成功率: {success_rate:.1f}%")
    
    if success_count == total_tests:
        logger.info("\n🎉 所有测试通过！API 服务运行正常。")
        logger.info("💡 提示: 现在可以尝试安装数据库依赖并运行完整的数据填充脚本。")
    else:
        logger.info(f"\n⚠️ 有 {total_tests - success_count} 个测试失败，请检查相关服务配置。")
    
    logger.info("\n🔍 详细日志已保存到 test_basic_apis.log")

if __name__ == "__main__":
    asyncio.run(main()) 