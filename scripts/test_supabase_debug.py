#!/usr/bin/env python3
"""
Supabase 连接诊断脚本

这个脚本用于诊断 Supabase 连接问题，提供详细的错误信息。

使用方法：
python3 scripts/test_supabase_debug.py
"""

import sys
import os
import logging
from typing import Optional

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_environment_variables():
    """检查环境变量配置"""
    logger.info("🔍 检查环境变量配置...")
    
    from config import settings
    
    # 检查必要的环境变量
    env_checks = {
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": settings.SUPABASE_SERVICE_ROLE_KEY,
        "SUPABASE_ANON_KEY": settings.SUPABASE_ANON_KEY
    }
    
    all_good = True
    for key, value in env_checks.items():
        if value:
            logger.info(f"  ✅ {key}: 已配置 (长度: {len(value)})")
            # 显示前几个字符用于验证
            if len(value) > 10:
                logger.info(f"     开头: {value[:10]}...")
        else:
            logger.error(f"  ❌ {key}: 未配置或为空")
            all_good = False
    
    return all_good, env_checks

def test_supabase_import():
    """测试 Supabase 包导入"""
    logger.info("📦 测试 Supabase 包导入...")
    
    try:
        import supabase
        logger.info(f"  ✅ supabase 包导入成功，版本: {supabase.__version__ if hasattr(supabase, '__version__') else '未知'}")
        
        from supabase import create_client
        logger.info("  ✅ create_client 函数导入成功")
        
        return True
    except ImportError as e:
        logger.error(f"  ❌ Supabase 包导入失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"  ❌ 其他导入错误: {str(e)}")
        return False

def test_client_creation():
    """测试 Supabase 客户端创建"""
    logger.info("🔗 测试 Supabase 客户端创建...")
    
    try:
        from config import settings
        from supabase import create_client
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.error("  ❌ 缺少必要的环境变量")
            return None
        
        # 尝试创建客户端
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        
        logger.info("  ✅ Supabase 客户端创建成功")
        logger.info(f"  📍 URL: {settings.SUPABASE_URL}")
        
        return client
        
    except Exception as e:
        logger.error(f"  ❌ 客户端创建失败: {str(e)}")
        logger.error(f"  🔍 错误类型: {type(e).__name__}")
        return None

def test_database_connection(client):
    """测试数据库连接"""
    if not client:
        logger.error("❌ 无法测试连接：客户端未创建")
        return False
    
    logger.info("🌐 测试数据库连接...")
    
    try:
        # 尝试简单的查询
        result = client.table("artists").select("*").limit(1).execute()
        
        logger.info("  ✅ 数据库连接成功")
        logger.info(f"  📊 查询结果: {len(result.data)} 条记录")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ 数据库连接失败: {str(e)}")
        logger.error(f"  🔍 错误类型: {type(e).__name__}")
        
        # 尝试更详细的错误分析
        error_str = str(e).lower()
        if "authentication" in error_str or "unauthorized" in error_str:
            logger.error("  💡 可能的问题: API 密钥错误或权限不足")
        elif "network" in error_str or "connection" in error_str:
            logger.error("  💡 可能的问题: 网络连接问题")
        elif "not found" in error_str:
            logger.error("  💡 可能的问题: 表不存在或 URL 错误")
        
        return False

def test_database_service():
    """测试我们的数据库服务类"""
    logger.info("🛠️ 测试数据库服务类...")
    
    try:
        from services.database_service import db_service
        
        logger.info(f"  📊 连接状态: {db_service.is_connected()}")
        
        if db_service.is_connected():
            # 测试连接
            import asyncio
            result = asyncio.run(db_service.test_connection())
            logger.info(f"  🧪 连接测试结果: {result}")
            return result.get("success", False)
        else:
            logger.error("  ❌ 数据库服务未连接")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ 数据库服务测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("🔧 Supabase 连接诊断开始")
    logger.info("=" * 60)
    
    # 1. 检查环境变量
    env_ok, env_vars = check_environment_variables()
    
    # 2. 测试包导入
    import_ok = test_supabase_import()
    
    # 3. 测试客户端创建
    client = test_client_creation() if env_ok and import_ok else None
    
    # 4. 测试数据库连接
    connection_ok = test_database_connection(client) if client else False
    
    # 5. 测试我们的服务类
    service_ok = test_database_service()
    
    # 总结
    logger.info("=" * 60)
    logger.info("📋 诊断结果总结:")
    logger.info(f"  环境变量配置: {'✅' if env_ok else '❌'}")
    logger.info(f"  包导入: {'✅' if import_ok else '❌'}")
    logger.info(f"  客户端创建: {'✅' if client else '❌'}")
    logger.info(f"  数据库连接: {'✅' if connection_ok else '❌'}")
    logger.info(f"  服务类测试: {'✅' if service_ok else '❌'}")
    
    if all([env_ok, import_ok, client, connection_ok, service_ok]):
        logger.info("🎉 所有测试通过！Supabase 连接正常")
        return True
    else:
        logger.error("❌ 存在问题，请根据上述信息进行修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 