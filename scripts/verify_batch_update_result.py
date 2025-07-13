#!/usr/bin/env python3
"""
验证批量更新结果
"""

import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "backend"))

from backend.services.database_service import db_service

def verify_batch_update_result():
    """验证批量更新结果"""
    try:
        print("=== 验证批量更新结果 ===")
        
        # 检查数据库连接
        if not db_service.is_connected():
            print("❌ 数据库未连接")
            return False
        
        # 1. 统计总艺术家数量
        print("\n1. 统计艺术家数量...")
        total_result = db_service.supabase.table("artists").select("id", count="exact").execute()
        total_artists = total_result.count
        print(f"📊 总艺术家数量: {total_artists}")
        
        # 2. 统计有音乐平台链接的艺术家
        print("\n2. 统计音乐平台链接覆盖率...")
        
        # 有QQ音乐链接的艺术家
        qq_result = db_service.supabase.table("artists").select("id", count="exact").not_.is_("qq_music_url", "null").execute()
        qq_count = qq_result.count
        
        # 有网易云音乐链接的艺术家
        netease_result = db_service.supabase.table("artists").select("id", count="exact").not_.is_("netease_url", "null").execute()
        netease_count = netease_result.count
        
        print(f"   🎵 有QQ音乐链接: {qq_count}/{total_artists} ({qq_count/total_artists*100:.1f}%)")
        print(f"   🎵 有网易云音乐链接: {netease_count}/{total_artists} ({netease_count/total_artists*100:.1f}%)")
        
        # 3. 随机检查几个艺术家的链接
        print("\n3. 随机检查艺术家链接...")
        sample_result = db_service.supabase.table("artists").select("name, qq_music_url, netease_url").limit(5).execute()
        
        for i, artist in enumerate(sample_result.data, 1):
            print(f"\n   🎤 艺术家 {i}: {artist['name']}")
            print(f"      QQ音乐: {artist['qq_music_url']}")
            print(f"      网易云: {artist['netease_url']}")
            
            # 验证链接格式
            if artist['qq_music_url'] and "y.qq.com" in artist['qq_music_url']:
                print(f"      ✅ QQ音乐链接格式正确")
            else:
                print(f"      ❌ QQ音乐链接格式错误")
                
            if artist['netease_url'] and "music.163.com" in artist['netease_url']:
                print(f"      ✅ 网易云音乐链接格式正确")
            else:
                print(f"      ❌ 网易云音乐链接格式错误")
        
        # 4. 检查是否有特殊艺术家使用了直接链接
        print("\n4. 检查特殊艺术家直接链接...")
        special_artists = ["VAMPIRE WEEKEND", "Vampire Weekend"]
        
        for artist_name in special_artists:
            result = db_service.supabase.table("artists").select("*").eq("name", artist_name).execute()
            if result.data:
                artist = result.data[0]
                print(f"\n   🌟 特殊艺术家: {artist['name']}")
                print(f"      QQ音乐: {artist['qq_music_url']}")
                print(f"      网易云: {artist['netease_url']}")
                
                # 检查是否是直接链接
                if artist['qq_music_url'] and "/search" not in artist['qq_music_url']:
                    print(f"      ✅ QQ音乐使用直接链接")
                else:
                    print(f"      ℹ️  QQ音乐使用搜索链接")
                    
                if artist['netease_url'] and "/search" not in artist['netease_url']:
                    print(f"      ✅ 网易云音乐使用直接链接")
                else:
                    print(f"      ℹ️  网易云音乐使用搜索链接")
        
        print(f"\n🎉 验证完成!")
        print(f"   📊 覆盖率: QQ音乐 {qq_count/total_artists*100:.1f}%, 网易云音乐 {netease_count/total_artists*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    verify_batch_update_result()
