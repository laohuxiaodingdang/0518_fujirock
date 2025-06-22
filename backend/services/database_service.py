"""
数据库服务 - 管理Supabase数据库连接和基础操作
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.supabase: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Supabase客户端"""
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                logger.warning("Supabase configuration incomplete")
                return
            
            self.supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            self.supabase = None
    
    def is_connected(self) -> bool:
        """检查数据库连接状态"""
        return self.supabase is not None
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试数据库连接"""
        if not self.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 尝试查询artists表的数量
            result = self.supabase.table("artists").select("id", count="exact").limit(1).execute()
            return {
                "success": True,
                "message": "Database connection successful",
                "artists_count": result.count if hasattr(result, 'count') else 0
            }
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return {"success": False, "error": str(e)}

# 创建全局数据库服务实例
db_service = DatabaseService() 