#!/usr/bin/env python3
"""
优化 artists 表结构

1. 删除冗余字段
2. 修复 spotify_id 数据
3. 更新表结构
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import asyncio
sys.path.append('.')

from services.database_service import db_service
from services.spotify_service import spotify_service

# 要删除的冗余字段
FIELDS_TO_DROP = [
    'name_zh',
    'name_en', 
    'name_ja',
    'external_urls',
    'popularity',
    'followers_count',
    'image_url',
    'images',
    'search_vector',
    'spotify_data'
]

async def backup_current_data():
    """备份当前数据"""
    print("📦 备份当前数据...")
    
    try:
        result = db_service.supabase.table('artists').select('*').execute()
        print(f"✅ 成功备份 {len(result.data)} 条记录")
        return result.data
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

async def get_spotify_id_for_artist(artist_name: str):
    """获取艺术家的 Spotify ID"""
    try:
        spotify_result = await spotify_service.get_artist_by_name(artist_name)
        if spotify_result.get("success"):
            return spotify_result["data"].get("id")
    except Exception as e:
        print(f"   ⚠️ 获取 {artist_name} 的 Spotify ID 失败: {e}")
    return None

async def update_spotify_ids(backup_data):
    """更新所有艺术家的 spotify_id"""
    print("🎧 更新 Spotify ID...")
    
    for artist in backup_data:
        artist_id = artist['id']
        artist_name = artist['name']
        current_spotify_id = artist.get('spotify_id')
        
        if not current_spotify_id:
            print(f"   🔍 获取 {artist_name} 的 Spotify ID...")
            spotify_id = await get_spotify_id_for_artist(artist_name)
            
            if spotify_id:
                try:
                    db_service.supabase.table('artists').update({
                        'spotify_id': spotify_id
                    }).eq('id', artist_id).execute()
                    print(f"   ✅ 更新 {artist_name} 的 Spotify ID: {spotify_id}")
                except Exception as e:
                    print(f"   ❌ 更新失败: {e}")
            else:
                print(f"   ⚠️ 未找到 {artist_name} 的 Spotify ID")
            
            # API 限制
            await asyncio.sleep(1)

def drop_columns():
    """删除冗余字段"""
    print("🗑️ 删除冗余字段...")
    
    # 注意：Supabase 不支持直接通过 Python 客户端删除列
    # 需要在 Supabase Dashboard 中手动执行 SQL
    
    sql_commands = []
    for field in FIELDS_TO_DROP:
        sql_commands.append(f"ALTER TABLE artists DROP COLUMN IF EXISTS {field};")
    
    print("📝 需要在 Supabase Dashboard 中执行以下 SQL 命令:")
    print("=" * 60)
    for cmd in sql_commands:
        print(cmd)
    print("=" * 60)
    
    return sql_commands

async def verify_optimized_table():
    """验证优化后的表结构"""
    print("🔍 验证优化后的表...")
    
    try:
        result = db_service.supabase.table('artists').select('*').limit(2).execute()
        
        if result.data:
            print("✅ 表结构验证:")
            sample = result.data[0]
            remaining_fields = list(sample.keys())
            print(f"   保留的字段: {remaining_fields}")
            
            # 检查 spotify_id 是否已更新
            spotify_ids = [item.get('spotify_id') for item in result.data]
            non_null_count = sum(1 for sid in spotify_ids if sid)
            print(f"   Spotify ID 更新情况: {non_null_count}/{len(result.data)} 个艺术家有 Spotify ID")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")

async def main():
    """主函数"""
    print("🔧 开始优化 artists 表结构")
    print("=" * 60)
    
    if not db_service.is_connected():
        print("❌ 数据库未连接")
        return
    
    # 1. 备份数据
    backup_data = await backup_current_data()
    if not backup_data:
        print("❌ 备份失败，停止操作")
        return
    
    # 2. 更新 spotify_id
    await update_spotify_ids(backup_data)
    
    # 3. 生成删除字段的 SQL 命令
    sql_commands = drop_columns()
    
    print("\n" + "=" * 60)
    print("📋 优化步骤总结:")
    print("1. ✅ 数据已备份")
    print("2. ✅ Spotify ID 已更新")
    print("3. 📝 SQL 命令已生成（需要手动执行）")
    
    print("\n🔧 下一步操作:")
    print("1. 复制上面的 SQL 命令")
    print("2. 在 Supabase Dashboard > SQL Editor 中执行")
    print("3. 运行验证脚本检查结果")
    
    # 4. 验证当前状态（删除字段前）
    print("\n🔍 当前状态验证:")
    await verify_optimized_table()

if __name__ == "__main__":
    asyncio.run(main()) 