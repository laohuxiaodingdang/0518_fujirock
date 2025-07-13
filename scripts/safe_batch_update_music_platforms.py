#!/usr/bin/env python3
"""
安全批量更新艺术家音乐平台链接 - 分批处理版本
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "backend"))

from backend.services.database_service import db_service

# 一些主要艺术家的直接链接示例
ARTIST_MUSIC_PLATFORMS = {
    "Vampire Weekend": {
        "qq_music_url": "https://y.qq.com/n/ryqq/singer/003LaMHm42u7qH",
        "netease_url": "https://music.163.com/#/artist?id=98351"
    },
    "Arctic Monkeys": {
        "qq_music_url": "https://y.qq.com/n/ryqq/singer/004YXNbO2x5Zzm",
        "netease_url": "https://music.163.com/#/artist?id=1045123"
    },
    "The Strokes": {
        "qq_music_url": "https://y.qq.com/n/ryqq/singer/000Sp0Bz4JXH0o",
        "netease_url": "https://music.163.com/#/artist?id=35032"
    }
}

async def safe_batch_update_music_platforms():
    """安全批量更新艺术家音乐平台链接"""
    try:
        print("=== 安全批量更新艺术家音乐平台链接 ===")
        
        # 检查数据库连接
        if not db_service.is_connected():
            print("❌ 数据库未连接")
            return False
        
        # 1. 获取所有需要更新的艺术家
        print("\n1. 获取艺术家列表...")
        result = db_service.supabase.table("artists").select("*").execute()
        
        if not result.data:
            print("❌ 数据库中没有找到艺术家")
            return False
        
        # 筛选出需要更新的艺术家（没有音乐平台链接的）
        artists_to_update = []
        for artist in result.data:
            if not artist.get('qq_music_url') or not artist.get('netease_url'):
                artists_to_update.append(artist)
        
        total_artists = len(artists_to_update)
        print(f"📊 总共需要更新 {total_artists} 个艺术家")
        
        if total_artists == 0:
            print("✅ 所有艺术家都已经有音乐平台链接了")
            return True
        
        # 2. 显示前几个艺术家作为预览
        print("\n2. 预览前 5 个需要更新的艺术家:")
        for i, artist in enumerate(artists_to_update[:5]):
            print(f"   {i+1}. {artist['name']}")
        
        if total_artists > 5:
            print(f"   ... 还有 {total_artists - 5} 个艺术家")
        
        # 3. 询问用户是否继续
        print(f"\n3. 准备分批更新 {total_artists} 个艺术家...")
        print("   - 每批处理 10 个艺术家")
        print("   - 每批之间暂停 1 秒")
        print("   - 可以随时按 Ctrl+C 停止")
        
        user_input = input("\n是否继续批量更新？(y/n): ").strip().lower()
        
        if user_input != 'y':
            print("❌ 用户取消操作")
            return False
        
        # 4. 分批处理
        batch_size = 10
        success_count = 0
        error_count = 0
        
        for i in range(0, total_artists, batch_size):
            batch = artists_to_update[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_artists + batch_size - 1) // batch_size
            
            print(f"\n📦 处理第 {batch_num}/{total_batches} 批 ({len(batch)} 个艺术家)...")
            
            for j, artist in enumerate(batch):
                try:
                    artist_name = artist.get("name")
                    artist_id = artist.get("id")
                    
                    # 生成搜索链接作为默认值
                    from urllib.parse import quote
                    default_qq_url = f"https://y.qq.com/n/ryqq/search?w={quote(artist_name)}"
                    default_netease_url = f"https://music.163.com/#/search/m/?s={quote(artist_name)}"
                    
                    # 如果有直接链接，使用直接链接
                    if artist_name in ARTIST_MUSIC_PLATFORMS:
                        qq_url = ARTIST_MUSIC_PLATFORMS[artist_name]["qq_music_url"]
                        netease_url = ARTIST_MUSIC_PLATFORMS[artist_name]["netease_url"]
                        link_type = "直接链接"
                    else:
                        qq_url = default_qq_url
                        netease_url = default_netease_url
                        link_type = "搜索链接"
                    
                    # 只更新空字段
                    update_data = {}
                    if not artist.get('qq_music_url'):
                        update_data['qq_music_url'] = qq_url
                    if not artist.get('netease_url'):
                        update_data['netease_url'] = netease_url
                    
                    if update_data:
                        # 执行更新
                        update_result = db_service.supabase.table("artists").update(update_data).eq("id", artist_id).execute()
                        
                        if update_result.data:
                            print(f"   ✅ {artist_name} ({link_type})")
                            success_count += 1
                        else:
                            print(f"   ❌ {artist_name} - 更新失败")
                            error_count += 1
                    else:
                        print(f"   ⏭️  {artist_name} - 已有链接，跳过")
                        
                except Exception as e:
                    print(f"   ❌ {artist_name} - 错误: {str(e)}")
                    error_count += 1
            
            # 批次间暂停
            if i + batch_size < total_artists:
                print(f"   ⏸️  暂停 1 秒...")
                time.sleep(1)
        
        # 5. 显示最终结果
        print(f"\n📊 更新完成!")
        print(f"   ✅ 成功: {success_count}")
        print(f"   ❌ 失败: {error_count}")
        print(f"   📈 总计: {success_count + error_count}")
        
        return error_count == 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断操作")
        print(f"   ✅ 已成功更新: {success_count}")
        print(f"   ❌ 失败: {error_count}")
        return False
        
    except Exception as e:
        print(f"❌ 批量更新过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(safe_batch_update_music_platforms())
