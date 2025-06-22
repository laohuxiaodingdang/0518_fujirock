#!/usr/bin/env python3
"""
Supabase 连接测试脚本
用于验证数据库连接和基本操作是否正常
"""

import asyncio
from supabase import create_client, Client
from config import settings

def test_supabase_connection():
    """测试 Supabase 连接"""
    print("🔍 开始测试 Supabase 连接...")
    
    # 检查配置
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        print("❌ Supabase 配置不完整，请检查环境变量")
        return False
    
    try:
        # 创建客户端
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        print("✅ Supabase 客户端创建成功")
        
        # 测试数据库连接 - 查询艺术家表
        print("🔍 测试数据库连接...")
        response = supabase.table('artists').select('count').execute()
        print(f"✅ 数据库连接成功，艺术家表查询正常")
        
        # 测试其他表
        tables_to_test = ['songs', 'ai_descriptions', 'user_favorites', 'performances']
        for table in tables_to_test:
            try:
                response = supabase.table(table).select('count').limit(1).execute()
                print(f"✅ {table} 表连接正常")
            except Exception as e:
                print(f"⚠️  {table} 表测试失败: {str(e)}")
        
        print("🎉 Supabase 连接测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ Supabase 连接失败: {str(e)}")
        return False

def test_auth_functionality():
    """测试认证功能（可选）"""
    print("\n🔍 测试认证功能...")
    
    try:
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        
        # 测试获取当前用户（应该返回 None，因为未登录）
        user = supabase.auth.get_user()
        print("✅ 认证系统正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 认证功能测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Fuji Rock 2025 - Supabase 连接测试")
    print("=" * 50)
    
    # 显示配置信息
    print(f"Supabase URL: {settings.SUPABASE_URL}")
    print(f"环境: {settings.ENVIRONMENT}")
    print("-" * 50)
    
    # 运行测试
    db_success = test_supabase_connection()
    auth_success = test_auth_functionality()
    
    print("\n" + "=" * 50)
    if db_success and auth_success:
        print("🎉 所有测试通过！您可以开始使用 Supabase 功能了。")
    else:
        print("❌ 部分测试失败，请检查配置和网络连接。") 