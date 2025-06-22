"""
艺术家数据库服务 - 管理艺术家相关的数据库操作
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from services.database_service import db_service
from models.database import ArtistModel, CreateArtistRequest, UpdateArtistRequest

logger = logging.getLogger(__name__)

class ArtistDatabaseService:
    """艺术家数据库服务类"""
    
    def __init__(self):
        self.db = db_service
    
    async def create_artist(self, artist_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新艺术家
        
        Args:
            artist_data: 艺术家数据字典
            
        Returns:
            创建结果，包含艺术家ID和详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 检查艺术家是否已存在
            existing = await self.get_artist_by_name(artist_data.get("name"))
            if existing.get("success") and existing.get("data"):
                return {
                    "success": False, 
                    "error": "Artist already exists",
                    "existing_artist_id": existing["data"]["id"]
                }
            
            # 准备插入数据（只使用优化后的字段）
            insert_data = {
                "name": artist_data.get("name"),
                "description": artist_data.get("description", ""),
                "image_url": artist_data.get("image_url"),
                "genres": artist_data.get("genres", []),
                "is_fuji_rock_artist": artist_data.get("is_fuji_rock_artist", False),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 添加可选字段
            if "wiki_data" in artist_data:
                insert_data["wiki_data"] = artist_data["wiki_data"]
            if "wiki_extract" in artist_data:
                insert_data["wiki_extract"] = artist_data["wiki_extract"]
            if "wiki_last_updated" in artist_data:
                insert_data["wiki_last_updated"] = artist_data["wiki_last_updated"]
            if "spotify_id" in artist_data:
                insert_data["spotify_id"] = artist_data["spotify_id"]
            
            # 执行插入操作
            result = self.db.supabase.table("artists").insert(insert_data).execute()
            
            if result.data:
                logger.info(f"Artist created successfully: {artist_data.get('name')}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Artist created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create artist"}
                
        except Exception as e:
            logger.error(f"Error creating artist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_artist_by_id(self, artist_id: UUID) -> Dict[str, Any]:
        """
        根据ID获取艺术家信息
        
        Args:
            artist_id: 艺术家UUID
            
        Returns:
            艺术家详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("artists").select("*").eq("id", str(artist_id)).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "Artist not found"}
                
        except Exception as e:
            logger.error(f"Error getting artist by ID: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_artist_by_name(self, name: str) -> Dict[str, Any]:
        """
        根据名称获取艺术家信息
        
        Args:
            name: 艺术家名称
            
        Returns:
            艺术家详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 只搜索 name 字段
            result = self.db.supabase.table("artists").select("*").eq("name", name).limit(1).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "Artist not found"}
                
        except Exception as e:
            logger.error(f"Error getting artist by name: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_artist_by_spotify_id(self, spotify_id: str) -> Dict[str, Any]:
        """
        根据Spotify ID获取艺术家信息
        
        Args:
            spotify_id: Spotify艺术家ID
            
        Returns:
            艺术家详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("artists").select("*").eq("spotify_id", spotify_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "Artist not found"}
                
        except Exception as e:
            logger.error(f"Error getting artist by Spotify ID: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_artist_performances(self, artist_id: str) -> Dict[str, Any]:
        """
        根据艺术家ID获取其所有演出信息
        
        Args:
            artist_id: 艺术家ID
            
        Returns:
            演出信息列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("performances").select("*").eq("artist_id", artist_id).execute()
            
            # This is not an error, an artist might not have performances
            return {
                "success": True,
                "data": result.data if result.data else []
            }
                
        except Exception as e:
            logger.error(f"Error getting performances for artist {artist_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_artist(self, artist_id: UUID, update_data: UpdateArtistRequest) -> Dict[str, Any]:
        """
        更新艺术家信息
        
        Args:
            artist_id: 艺术家UUID
            update_data: 更新数据
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 准备更新数据（只包含非None的字段）
            update_dict = {}
            for field, value in update_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_dict[field] = value
            
            if not update_dict:
                return {"success": False, "error": "No data to update"}
            
            # 添加更新时间
            update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # 执行更新操作
            result = self.db.supabase.table("artists").update(update_dict).eq("id", str(artist_id)).execute()
            
            if result.data:
                logger.info(f"Artist updated successfully: {artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Artist updated successfully"
                }
            else:
                return {"success": False, "error": "Artist not found or update failed"}
                
        except Exception as e:
            logger.error(f"Error updating artist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_artist_simple(self, artist_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        简单的艺术家信息更新方法（接受字典参数）
        
        Args:
            artist_id: 艺术家ID（字符串格式）
            update_data: 更新数据字典
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 过滤空值
            update_dict = {k: v for k, v in update_data.items() if v is not None}
            
            if not update_dict:
                return {"success": False, "error": "No data to update"}
            
            # 添加更新时间
            update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # 执行更新操作
            result = self.db.supabase.table("artists").update(update_dict).eq("id", artist_id).execute()
            
            if result.data:
                logger.info(f"Artist updated successfully: {artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Artist updated successfully"
                }
            else:
                return {"success": False, "error": "Artist not found or update failed"}
                
        except Exception as e:
            logger.error(f"Error updating artist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_artist_wikipedia_data(self, artist_id: UUID, wiki_data: Dict[str, Any], wiki_extract: str) -> Dict[str, Any]:
        """
        更新艺术家的Wikipedia数据
        
        Args:
            artist_id: 艺术家UUID
            wiki_data: Wikipedia原始数据
            wiki_extract: Wikipedia摘要文本
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            update_data = {
                "wiki_data": wiki_data,
                "wiki_extract": wiki_extract,
                "wiki_last_updated": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.db.supabase.table("artists").update(update_data).eq("id", str(artist_id)).execute()
            
            if result.data:
                logger.info(f"Artist Wikipedia data updated: {artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Wikipedia data updated successfully"
                }
            else:
                return {"success": False, "error": "Failed to update Wikipedia data"}
                
        except Exception as e:
            logger.error(f"Error updating Wikipedia data: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_artist_spotify_data(self, artist_id: UUID, spotify_data: Dict[str, Any], spotify_id: str = None) -> Dict[str, Any]:
        """
        更新艺术家的Spotify数据
        
        Args:
            artist_id: 艺术家UUID
            spotify_data: Spotify艺术家数据
            spotify_id: Spotify艺术家ID（可选）
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            update_data = {
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if spotify_id:
                update_data["spotify_id"] = spotify_id
            
            # 从Spotify数据中提取genres
            if "genres" in spotify_data:
                update_data["genres"] = spotify_data["genres"]
            
            result = self.db.supabase.table("artists").update(update_data).eq("id", str(artist_id)).execute()
            
            if result.data:
                logger.info(f"Artist Spotify data updated: {artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Spotify data updated successfully"
                }
            else:
                return {"success": False, "error": "Failed to update Spotify data"}
                
        except Exception as e:
            logger.error(f"Error updating Spotify data: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def search_artists(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        搜索艺术家（支持全文搜索和模糊匹配）
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            搜索结果列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 只搜索现有字段
            result = self.db.supabase.table("artists").select("*").or_(
                f"name.ilike.%{query}%,description.ilike.%{query}%"
            ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "query": query,
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error searching artists: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_fuji_rock_artists(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        获取Fuji Rock艺术家列表
        
        Args:
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            Fuji Rock艺术家列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("artists").select("*").eq("is_fuji_rock_artist", True).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting Fuji Rock artists: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_popular_artists(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        获取热门艺术家列表
        
        Args:
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            热门艺术家列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("artists").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting popular artists: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_artist(self, artist_id: UUID) -> Dict[str, Any]:
        """
        删除艺术家（软删除，实际项目中可能需要考虑级联删除相关数据）
        
        Args:
            artist_id: 艺术家UUID
            
        Returns:
            删除结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("artists").delete().eq("id", str(artist_id)).execute()
            
            if result.data:
                logger.info(f"Artist deleted successfully: {artist_id}")
                return {
                    "success": True,
                    "message": "Artist deleted successfully"
                }
            else:
                return {"success": False, "error": "Artist not found or delete failed"}
                
        except Exception as e:
            logger.error(f"Error deleting artist: {str(e)}")
            return {"success": False, "error": str(e)}

# 创建全局艺术家数据库服务实例
artist_db_service = ArtistDatabaseService() 