"""
用户数据库服务 - 管理用户收藏和搜索历史相关的数据库操作
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, timedelta
from services.database_service import db_service
from models.database import UserFavoriteModel, SearchHistoryModel, CreateFavoriteRequest

logger = logging.getLogger(__name__)

class UserDatabaseService:
    """用户数据库服务类"""
    
    def __init__(self):
        self.db = db_service
    
    # ==================== 用户收藏相关操作 ====================
    
    async def add_favorite(self, user_id: UUID, favorite_data: CreateFavoriteRequest) -> Dict[str, Any]:
        """
        添加用户收藏
        
        Args:
            user_id: 用户UUID
            favorite_data: 收藏创建请求数据
            
        Returns:
            创建结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 检查是否已经收藏
            existing = await self.get_favorite(user_id, favorite_data.artist_id)
            if existing.get("success") and existing.get("data"):
                return {
                    "success": False, 
                    "error": "Artist already in favorites",
                    "existing_favorite_id": existing["data"]["id"]
                }
            
            # 准备插入数据
            insert_data = {
                "user_id": str(user_id),
                "artist_id": str(favorite_data.artist_id),
                "tags": favorite_data.tags,
                "notes": favorite_data.notes,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 执行插入操作
            result = self.db.supabase.table("user_favorites").insert(insert_data).execute()
            
            if result.data:
                logger.info(f"Favorite added successfully: user {user_id}, artist {favorite_data.artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Favorite added successfully"
                }
            else:
                return {"success": False, "error": "Failed to add favorite"}
                
        except Exception as e:
            logger.error(f"Error adding favorite: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def remove_favorite(self, user_id: UUID, artist_id: UUID) -> Dict[str, Any]:
        """
        移除用户收藏
        
        Args:
            user_id: 用户UUID
            artist_id: 艺术家UUID
            
        Returns:
            删除结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("user_favorites").delete().eq("user_id", str(user_id)).eq("artist_id", str(artist_id)).execute()
            
            if result.data:
                logger.info(f"Favorite removed successfully: user {user_id}, artist {artist_id}")
                return {
                    "success": True,
                    "message": "Favorite removed successfully"
                }
            else:
                return {"success": False, "error": "Favorite not found"}
                
        except Exception as e:
            logger.error(f"Error removing favorite: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_favorite(self, user_id: UUID, artist_id: UUID) -> Dict[str, Any]:
        """
        获取特定的用户收藏
        
        Args:
            user_id: 用户UUID
            artist_id: 艺术家UUID
            
        Returns:
            收藏信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("user_favorites").select("*").eq("user_id", str(user_id)).eq("artist_id", str(artist_id)).limit(1).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "Favorite not found"}
                
        except Exception as e:
            logger.error(f"Error getting favorite: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_favorites(self, user_id: UUID, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        获取用户收藏列表
        
        Args:
            user_id: 用户UUID
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            用户收藏列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("user_favorites").select("*, artists(id, name, name_zh, name_en, image_url, genres, popularity)").eq("user_id", str(user_id)).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "user_id": str(user_id),
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting user favorites: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_favorite_notes(self, user_id: UUID, artist_id: UUID, notes: str, tags: List[str] = None) -> Dict[str, Any]:
        """
        更新收藏的备注和标签
        
        Args:
            user_id: 用户UUID
            artist_id: 艺术家UUID
            notes: 新的备注
            tags: 新的标签列表（可选）
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            update_data = {"notes": notes}
            if tags is not None:
                update_data["tags"] = tags
            
            result = self.db.supabase.table("user_favorites").update(update_data).eq("user_id", str(user_id)).eq("artist_id", str(artist_id)).execute()
            
            if result.data:
                logger.info(f"Favorite notes updated: user {user_id}, artist {artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Favorite notes updated successfully"
                }
            else:
                return {"success": False, "error": "Favorite not found or update failed"}
                
        except Exception as e:
            logger.error(f"Error updating favorite notes: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_favorites_by_tag(self, user_id: UUID, tag: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        根据标签获取用户收藏
        
        Args:
            user_id: 用户UUID
            tag: 标签名称
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            带有指定标签的收藏列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 使用PostgreSQL数组操作符查询包含指定标签的收藏
            result = self.db.supabase.table("user_favorites").select("*, artists(id, name, name_zh, name_en, image_url, genres, popularity)").eq("user_id", str(user_id)).contains("tags", [tag]).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "user_id": str(user_id),
                "tag": tag,
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting favorites by tag: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ==================== 搜索历史相关操作 ====================
    
    async def record_search(self, search_query: str, search_type: str = "artist", user_id: UUID = None, 
                          results_count: int = 0, session_id: str = None, ip_address: str = None, 
                          user_agent: str = None) -> Dict[str, Any]:
        """
        记录搜索历史
        
        Args:
            search_query: 搜索关键词
            search_type: 搜索类型
            user_id: 用户UUID（可选）
            results_count: 结果数量
            session_id: 会话ID（可选）
            ip_address: IP地址（可选）
            user_agent: 用户代理（可选）
            
        Returns:
            记录结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 准备插入数据
            insert_data = {
                "search_query": search_query,
                "search_type": search_type,
                "results_count": results_count,
                "session_id": session_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            if user_id:
                insert_data["user_id"] = str(user_id)
            
            # 执行插入操作
            result = self.db.supabase.table("search_history").insert(insert_data).execute()
            
            if result.data:
                logger.info(f"Search recorded: {search_query} ({search_type})")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Search recorded successfully"
                }
            else:
                return {"success": False, "error": "Failed to record search"}
                
        except Exception as e:
            logger.error(f"Error recording search: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_search_history(self, user_id: UUID, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        获取用户搜索历史
        
        Args:
            user_id: 用户UUID
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            用户搜索历史列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("search_history").select("*").eq("user_id", str(user_id)).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "user_id": str(user_id),
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting user search history: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_popular_searches(self, search_type: str = None, days: int = 7, limit: int = 10) -> Dict[str, Any]:
        """
        获取热门搜索关键词
        
        Args:
            search_type: 搜索类型过滤（可选）
            days: 统计最近多少天的数据
            limit: 返回结果数量限制
            
        Returns:
            热门搜索关键词列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 计算时间范围
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # 构建查询
            query = self.db.supabase.table("search_history").select("search_query").gte("created_at", cutoff_date.isoformat())
            
            if search_type:
                query = query.eq("search_type", search_type)
            
            result = query.execute()
            
            if result.data:
                # 统计搜索频次
                search_counts = {}
                for item in result.data:
                    query_text = item["search_query"]
                    search_counts[query_text] = search_counts.get(query_text, 0) + 1
                
                # 排序并取前N个
                popular_searches = sorted(search_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
                
                return {
                    "success": True,
                    "data": [{"query": query, "count": count} for query, count in popular_searches],
                    "search_type": search_type,
                    "days": days,
                    "limit": limit
                }
            else:
                return {
                    "success": True,
                    "data": [],
                    "search_type": search_type,
                    "days": days,
                    "limit": limit
                }
                
        except Exception as e:
            logger.error(f"Error getting popular searches: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def record_search_click(self, search_id: UUID, clicked_result_id: UUID) -> Dict[str, Any]:
        """
        记录搜索结果点击
        
        Args:
            search_id: 搜索记录UUID
            clicked_result_id: 被点击的结果ID
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            update_data = {
                "clicked_result_id": str(clicked_result_id)
            }
            
            result = self.db.supabase.table("search_history").update(update_data).eq("id", str(search_id)).execute()
            
            if result.data:
                logger.info(f"Search click recorded: search {search_id}, result {clicked_result_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Search click recorded successfully"
                }
            else:
                return {"success": False, "error": "Search record not found"}
                
        except Exception as e:
            logger.error(f"Error recording search click: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_old_search_history(self, days_old: int = 90) -> Dict[str, Any]:
        """
        清理旧的搜索历史记录
        
        Args:
            days_old: 删除多少天前的记录
            
        Returns:
            清理结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            result = self.db.supabase.table("search_history").delete().lt("created_at", cutoff_date.isoformat()).execute()
            
            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {deleted_count} old search history records")
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Successfully cleaned up {deleted_count} old search records"
            }
                
        except Exception as e:
            logger.error(f"Error cleaning up old search history: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ==================== 用户统计相关操作 ====================
    
    async def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户UUID
            
        Returns:
            用户统计信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 获取收藏数量
            favorites_result = self.db.supabase.table("user_favorites").select("id", count="exact").eq("user_id", str(user_id)).execute()
            favorites_count = favorites_result.count if hasattr(favorites_result, 'count') else 0
            
            # 获取搜索历史数量
            searches_result = self.db.supabase.table("search_history").select("id", count="exact").eq("user_id", str(user_id)).execute()
            searches_count = searches_result.count if hasattr(searches_result, 'count') else 0
            
            # 获取最近收藏的艺术家
            recent_favorites = self.db.supabase.table("user_favorites").select("artists(name, name_zh)").eq("user_id", str(user_id)).order("created_at", desc=True).limit(5).execute()
            
            return {
                "success": True,
                "data": {
                    "user_id": str(user_id),
                    "favorites_count": favorites_count,
                    "searches_count": searches_count,
                    "recent_favorites": recent_favorites.data if recent_favorites.data else []
                }
            }
                
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {"success": False, "error": str(e)}

# 创建全局用户数据库服务实例
user_db_service = UserDatabaseService() 