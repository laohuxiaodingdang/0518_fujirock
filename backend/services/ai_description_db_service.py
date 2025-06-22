"""
AI描述数据库服务 - 管理AI生成的艺术家描述相关的数据库操作
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, timedelta
from services.database_service import db_service
from models.database import AIDescriptionModel, CreateAIDescriptionRequest

logger = logging.getLogger(__name__)

class AIDescriptionDatabaseService:
    """AI描述数据库服务类"""
    
    def __init__(self):
        self.db = db_service
    
    async def create_ai_description(self, description_data: CreateAIDescriptionRequest) -> Dict[str, Any]:
        """
        创建新的AI描述
        
        Args:
            description_data: AI描述创建请求数据
            
        Returns:
            创建结果，包含描述ID和详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 准备插入数据
            insert_data = {
                "artist_id": str(description_data.artist_id),
                "content": description_data.content,
                "language": description_data.language,
                "prompt_template": description_data.prompt_template,
                "source_content": description_data.source_content,
                "tokens_used": description_data.tokens_used,
                "generation_time_ms": description_data.generation_time_ms,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 执行插入操作
            result = self.db.supabase.table("ai_descriptions").insert(insert_data).execute()
            
            if result.data:
                logger.info(f"AI description created successfully for artist: {description_data.artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "AI description created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create AI description"}
                
        except Exception as e:
            logger.error(f"Error creating AI description: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_ai_description_by_id(self, description_id: UUID) -> Dict[str, Any]:
        """
        根据ID获取AI描述信息
        
        Args:
            description_id: AI描述UUID
            
        Returns:
            AI描述详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("ai_descriptions").select("*").eq("id", str(description_id)).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "AI description not found"}
                
        except Exception as e:
            logger.error(f"Error getting AI description by ID: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_ai_descriptions_by_artist(self, artist_id: UUID, language: str = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        获取艺术家的AI描述列表
        
        Args:
            artist_id: 艺术家UUID
            language: 语言过滤（可选）
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            AI描述列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            query = self.db.supabase.table("ai_descriptions").select("*").eq("artist_id", str(artist_id))
            
            if language:
                query = query.eq("language", language)
            
            result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "artist_id": str(artist_id),
                "language": language,
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting AI descriptions by artist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_latest_ai_description(self, artist_id: UUID, language: str = "zh") -> Dict[str, Any]:
        """
        获取艺术家最新的AI描述
        
        Args:
            artist_id: 艺术家UUID
            language: 语言代码，默认中文
            
        Returns:
            最新的AI描述
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("ai_descriptions").select("*").eq("artist_id", str(artist_id)).eq("language", language).order("created_at", desc=True).limit(1).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "No AI description found"}
                
        except Exception as e:
            logger.error(f"Error getting latest AI description: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_ai_description_content(self, description_id: UUID, new_content: str) -> Dict[str, Any]:
        """
        更新AI描述内容（用于内容修正或优化）
        
        Args:
            description_id: AI描述UUID
            new_content: 新的描述内容
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            update_data = {
                "content": new_content
            }
            
            result = self.db.supabase.table("ai_descriptions").update(update_data).eq("id", str(description_id)).execute()
            
            if result.data:
                logger.info(f"AI description content updated: {description_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "AI description content updated successfully"
                }
            else:
                return {"success": False, "error": "AI description not found or update failed"}
                
        except Exception as e:
            logger.error(f"Error updating AI description content: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_ai_descriptions_stats(self, artist_id: UUID = None) -> Dict[str, Any]:
        """
        获取AI描述统计信息
        
        Args:
            artist_id: 艺术家UUID（可选，如果提供则只统计该艺术家）
            
        Returns:
            统计信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            query = self.db.supabase.table("ai_descriptions").select("language, tokens_used, generation_time_ms")
            
            if artist_id:
                query = query.eq("artist_id", str(artist_id))
            
            result = query.execute()
            
            if result.data:
                # 计算统计信息
                total_descriptions = len(result.data)
                total_tokens = sum(item.get("tokens_used", 0) for item in result.data if item.get("tokens_used"))
                total_time = sum(item.get("generation_time_ms", 0) for item in result.data if item.get("generation_time_ms"))
                
                # 按语言分组统计
                language_stats = {}
                for item in result.data:
                    lang = item.get("language", "unknown")
                    if lang not in language_stats:
                        language_stats[lang] = 0
                    language_stats[lang] += 1
                
                return {
                    "success": True,
                    "data": {
                        "total_descriptions": total_descriptions,
                        "total_tokens_used": total_tokens,
                        "total_generation_time_ms": total_time,
                        "average_tokens_per_description": total_tokens / total_descriptions if total_descriptions > 0 else 0,
                        "average_generation_time_ms": total_time / total_descriptions if total_descriptions > 0 else 0,
                        "language_distribution": language_stats
                    }
                }
            else:
                return {
                    "success": True,
                    "data": {
                        "total_descriptions": 0,
                        "total_tokens_used": 0,
                        "total_generation_time_ms": 0,
                        "average_tokens_per_description": 0,
                        "average_generation_time_ms": 0,
                        "language_distribution": {}
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting AI descriptions stats: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def search_ai_descriptions(self, query: str, language: str = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        搜索AI描述内容
        
        Args:
            query: 搜索关键词
            language: 语言过滤（可选）
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            搜索结果列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            db_query = self.db.supabase.table("ai_descriptions").select("*, artists(name, name_zh, name_en)").ilike("content", f"%{query}%")
            
            if language:
                db_query = db_query.eq("language", language)
            
            result = db_query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "query": query,
                "language": language,
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error searching AI descriptions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_ai_description(self, description_id: UUID) -> Dict[str, Any]:
        """
        删除AI描述
        
        Args:
            description_id: AI描述UUID
            
        Returns:
            删除结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("ai_descriptions").delete().eq("id", str(description_id)).execute()
            
            if result.data:
                logger.info(f"AI description deleted successfully: {description_id}")
                return {
                    "success": True,
                    "message": "AI description deleted successfully"
                }
            else:
                return {"success": False, "error": "AI description not found or delete failed"}
                
        except Exception as e:
            logger.error(f"Error deleting AI description: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_ai_descriptions_by_artist(self, artist_id: UUID) -> Dict[str, Any]:
        """
        删除艺术家的所有AI描述（用于艺术家删除时的级联操作）
        
        Args:
            artist_id: 艺术家UUID
            
        Returns:
            删除结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("ai_descriptions").delete().eq("artist_id", str(artist_id)).execute()
            
            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} AI descriptions for artist: {artist_id}")
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Deleted {deleted_count} AI descriptions successfully"
            }
                
        except Exception as e:
            logger.error(f"Error deleting AI descriptions by artist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_old_descriptions(self, days_old: int = 30, keep_latest: int = 3) -> Dict[str, Any]:
        """
        清理旧的AI描述（保留每个艺术家最新的几个版本）
        
        Args:
            days_old: 删除多少天前的描述
            keep_latest: 每个艺术家保留最新的描述数量
            
        Returns:
            清理结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 这是一个复杂的清理操作，需要先查询再删除
            # 实际实现中可能需要使用数据库函数或存储过程
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            # 获取所有艺术家的AI描述
            all_descriptions = self.db.supabase.table("ai_descriptions").select("*").lt("created_at", cutoff_date.isoformat()).order("artist_id", "created_at", desc=True).execute()
            
            if not all_descriptions.data:
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "No old descriptions to clean up"
                }
            
            # 按艺术家分组，保留最新的几个
            artist_descriptions = {}
            for desc in all_descriptions.data:
                artist_id = desc["artist_id"]
                if artist_id not in artist_descriptions:
                    artist_descriptions[artist_id] = []
                artist_descriptions[artist_id].append(desc)
            
            # 收集要删除的描述ID
            to_delete = []
            for artist_id, descriptions in artist_descriptions.items():
                if len(descriptions) > keep_latest:
                    # 保留最新的keep_latest个，删除其余的
                    sorted_descriptions = sorted(descriptions, key=lambda x: x["created_at"], reverse=True)
                    to_delete.extend([desc["id"] for desc in sorted_descriptions[keep_latest:]])
            
            if not to_delete:
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "No descriptions need to be cleaned up"
                }
            
            # 批量删除
            result = self.db.supabase.table("ai_descriptions").delete().in_("id", to_delete).execute()
            
            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {deleted_count} old AI descriptions")
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Successfully cleaned up {deleted_count} old descriptions"
            }
                
        except Exception as e:
            logger.error(f"Error cleaning up old AI descriptions: {str(e)}")
            return {"success": False, "error": str(e)}

# 创建全局AI描述数据库服务实例
ai_description_db_service = AIDescriptionDatabaseService() 