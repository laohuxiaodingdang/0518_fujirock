#!/usr/bin/env python3
"""
测试环境变量加载

检查 .env 文件是否能被正确加载
"""

import os
import sys
from dotenv import load_dotenv

print("🔍 测试环境变量加载...")

# 检查当前工作目录
print(f"📁 当前工作目录: {os.getcwd()}")

# 检查 .env 文件是否存在
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ .env 文件存在: {os.path.abspath(env_file)}")
    
    # 显示文件大小
    file_size = os.path.getsize(env_file)
    print(f"📊 文件大小: {file_size} 字节")
    
    # 尝试加载环境变量
    print("🔄 尝试加载环境变量...")
    result = load_dotenv(env_file, verbose=True)
    print(f"📋 加载结果: {result}")
    
    # 检查特定的环境变量
    supabase_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    print("\n🔍 检查 Supabase 环境变量:")
    for var in supabase_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: 已设置 (长度: {len(value)})")
        else:
            print(f"  ❌ {var}: 未设置")
    
    # 检查所有以 SUPABASE 开头的环境变量
    print("\n🔍 所有 SUPABASE 相关环境变量:")
    supabase_env_vars = {k: v for k, v in os.environ.items() if k.startswith('SUPABASE')}
    if supabase_env_vars:
        for k, v in supabase_env_vars.items():
            print(f"  {k}: {v[:20]}..." if len(v) > 20 else f"  {k}: {v}")
    else:
        print("  ❌ 没有找到任何 SUPABASE 环境变量")
        
else:
    print(f"❌ .env 文件不存在: {os.path.abspath(env_file)}")

print("\n" + "="*50)
print("🧪 测试完成") 