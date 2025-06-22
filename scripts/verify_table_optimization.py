#!/usr/bin/env python3
"""
验证 artists 表优化结果
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import asyncio
sys.path.append('.')

from services.database_service import db_service

async def verify_optimization():
    """验证表结构优化结果"""
    print("🔍 验证 artists 表优化结果")
    print("=" * 60)
    
    if not db_service.is_connected():
        print("❌ 数据库未连接")
        return
    
    try:
        # 查看优化后的数据
        result = db_service.supabase.table('artists').select('*').execute()
        
        print(f"📊 表中总记录数: {len(result.data)}")
        
        if result.data:
            # 检查字段结构
            sample = result.data[0]
            remaining_fields = list(sample.keys())
            
            print(f"\n📋 优化后保留的字段 ({len(remaining_fields)} 个):")
            for field in sorted(remaining_fields):
                print(f"   - {field}")
            
            # 检查删除的字段是否还存在
            deleted_fields = [
                'name_zh', 'name_en', 'name_ja', 'external_urls', 
                'popularity', 'followers_count', 'image_url', 'images', 
                'search_vector', 'spotify_data'
            ]
            
            still_exists = [field for field in deleted_fields if field in remaining_fields]
            if still_exists:
                print(f"\n⚠️ 以下字段仍然存在（可能需要重新执行 SQL）:")
                for field in still_exists:
                    print(f"   - {field}")
            else:
                print(f"\n✅ 所有冗余字段已成功删除")
            
            # 检查 spotify_id 数据
            print(f"\n🎧 Spotify ID 数据检查:")
            spotify_id_count = sum(1 for item in result.data if item.get('spotify_id'))
            print(f"   有 Spotify ID 的艺术家: {spotify_id_count}/{len(result.data)}")
            
            # 显示每个艺术家的关键信息
            print(f"\n🎤 艺术家数据概览:")
            for i, artist in enumerate(result.data, 1):
                name = artist.get('name', 'Unknown')
                spotify_id = artist.get('spotify_id', 'None')
                is_fuji_rock = artist.get('is_fuji_rock_artist', False)
                print(f"   {i}. {name}")
                print(f"      Spotify ID: {spotify_id}")
                print(f"      Fuji Rock 艺术家: {'是' if is_fuji_rock else '否'}")
                print(f"      创建时间: {artist.get('created_at', 'Unknown')}")
                print()
        
        # 计算优化效果
        expected_fields = [
            'id', 'name', 'description', 'wiki_data', 'wiki_extract', 
            'wiki_last_updated', 'spotify_id', 'genres', 'is_fuji_rock_artist', 
            'created_at', 'updated_at'
        ]
        
        if result.data:
            actual_fields = set(result.data[0].keys())
            expected_fields_set = set(expected_fields)
            
            print("📈 优化效果分析:")
            print(f"   期望字段数: {len(expected_fields_set)}")
            print(f"   实际字段数: {len(actual_fields)}")
            
            extra_fields = actual_fields - expected_fields_set
            missing_fields = expected_fields_set - actual_fields
            
            if extra_fields:
                print(f"   额外字段: {list(extra_fields)}")
            if missing_fields:
                print(f"   缺失字段: {list(missing_fields)}")
            
            if not extra_fields and not missing_fields:
                print("   ✅ 表结构完全符合预期！")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")

async def test_database_operations():
    """测试数据库操作是否正常"""
    print("\n🧪 测试数据库操作...")
    
    try:
        # 测试查询
        result = db_service.supabase.table('artists').select('name, spotify_id').limit(1).execute()
        if result.data:
            print("✅ 查询操作正常")
        
        # 测试搜索（如果有数据）
        if result.data:
            first_artist = result.data[0]
            search_result = db_service.supabase.table('artists').select('*').eq('name', first_artist['name']).execute()
            if search_result.data:
                print("✅ 搜索操作正常")
        
        print("✅ 所有基本操作测试通过")
        
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")

async def main():
    """主函数"""
    await verify_optimization()
    await test_database_operations()
    
    print("\n" + "=" * 60)
    print("🎯 验证完成！")
    print("\n💡 如果发现问题:")
    print("1. 检查 SQL 是否在 Supabase Dashboard 中正确执行")
    print("2. 确认所有 ALTER TABLE 命令都成功运行")
    print("3. 刷新 Supabase Dashboard 查看最新表结构")

if __name__ == "__main__":
    asyncio.run(main()) 