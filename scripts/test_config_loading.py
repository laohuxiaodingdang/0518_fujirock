#!/usr/bin/env python3
"""
测试配置加载时机

检查环境变量和配置加载的时机问题
"""

import os
import sys
from dotenv import load_dotenv

print("🔍 测试配置加载时机...")

# 1. 检查加载前的状态
print(f"加载前 SUPABASE_URL: {os.getenv('SUPABASE_URL')}")

# 2. 手动加载环境变量
print("🔄 手动加载环境变量...")
result = load_dotenv()
print(f"加载结果: {result}")

# 3. 检查加载后的状态
supabase_url = os.getenv('SUPABASE_URL')
print(f"加载后 SUPABASE_URL: {supabase_url[:50]}..." if supabase_url else "加载后 SUPABASE_URL: None")

# 4. 测试我们的配置模块
print("🔄 导入配置模块...")
sys.path.append('.')

try:
    from config import settings
    print(f"配置中的 SUPABASE_URL: {settings.SUPABASE_URL[:50]}..." if settings.SUPABASE_URL else "配置中的 SUPABASE_URL: None")
    print(f"配置中的 SERVICE_ROLE_KEY: {'已设置' if settings.SUPABASE_SERVICE_ROLE_KEY else '未设置'}")
    
    # 验证 API 密钥
    validation = settings.validate_api_keys()
    print(f"API 密钥验证: {validation}")
    
except Exception as e:
    print(f"❌ 配置导入失败: {str(e)}")

print("\n" + "="*50)
print("🧪 测试完成") 