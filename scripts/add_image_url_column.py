#!/usr/bin/env python3
"""
数据库迁移脚本：为 artists 表添加 image_url 列
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import db_service

async def add_image_url_column():
    """为 artists 表添加 image_url 列"""
    try:
        print("=== Adding image_url column to artists table ===")
        
        # 检查数据库连接
        if not db_service.is_connected():
            print("Database not connected!")
            return False
        
        # 注意：Supabase 不支持直接通过 Python SDK 修改表结构
        # 需要通过 SQL 命令或 Supabase Dashboard 来添加列
        print("📋 To add the image_url column, please run the following SQL command in your Supabase Dashboard:")
        print()
        print("🔧 SQL Command:")
        print("ALTER TABLE artists ADD COLUMN image_url TEXT;")
        print()
        print("Or you can use the Supabase Dashboard:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to Table Editor")
        print("3. Select the 'artists' table")
        print("4. Click 'Add Column'")
        print("5. Set column name: 'image_url'")
        print("6. Set type: 'text'")
        print("7. Leave nullable: true")
        print("8. Click 'Save'")
        print()
        
        # 测试是否已经添加了列（通过插入测试数据）
        try:
            # 尝试获取一个艺术家记录，看看是否有 image_url 字段
            result = db_service.supabase.table("artists").select("*").limit(1).execute()
            if result.data and len(result.data) > 0:
                artist = result.data[0]
                if "image_url" in artist:
                    print("✅ image_url column already exists!")
                    return True
                else:
                    print("❌ image_url column does not exist yet. Please add it using the SQL command above.")
                    return False
        except Exception as e:
            print(f"Error checking column existence: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(add_image_url_column()) 