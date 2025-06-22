"""
歌曲数据库服务 - 管理歌曲相关的数据库操作
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, date
from services.database_service import db_service
from models.database import SongModel, CreateSongRequest

logger = logging.getLogger(__name__)

class SongDatabaseService:
    """歌曲数据库服务类"""
    
    def __init__(self):
        self.db = db_service
    
    async def create_song(self, song_data: CreateSongRequest) -> Dict[str, Any]:
        """
        创建新歌曲
        
        Args:
            song_data: 歌曲创建请求数据
            
        Returns:
            创建结果，包含歌曲ID和详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 检查歌曲是否已存在（同一艺术家的同名歌曲）
            existing = await self.get_song_by_artist_and_title(song_data.artist_id, song_data.title)
            if existing.get("success") and existing.get("data"):
                return {
                    "success": False, 
                    "error": "Song already exists for this artist",
                    "existing_song_id": existing["data"]["id"]
                }
            
            # 准备插入数据
            insert_data = {
                "artist_id": str(song_data.artist_id),
                "title": song_data.title,
                "album_name": song_data.album_name,
                "duration_seconds": song_data.duration_seconds,
                "preview_url": song_data.preview_url,
                "spotify_id": song_data.spotify_id,
                "release_date": song_data.release_date.isoformat() if song_data.release_date else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 执行插入操作
            result = self.db.supabase.table("songs").insert(insert_data).execute()
            
            if result.data:
                logger.info(f"Song created successfully: {song_data.title} by artist {song_data.artist_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Song created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create song"}
                
        except Exception as e:
            logger.error(f"Error creating song: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_song_by_id(self, song_id: UUID) -> Dict[str, Any]:
        """
        根据ID获取歌曲信息
        
        Args:
            song_id: 歌曲UUID
            
        Returns:
            歌曲详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("songs").select("*").eq("id", str(song_id)).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "Song not found"}
                
        except Exception as e:
            logger.error(f"Error getting song by ID: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_song_by_artist_and_title(self, artist_id: UUID, title: str) -> Dict[str, Any]:
        """
        根据艺术家ID和歌曲标题获取歌曲信息
        
        Args:
            artist_id: 艺术家UUID
            title: 歌曲标题
            
        Returns:
            歌曲详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("songs").select("*").eq("artist_id", str(artist_id)).eq("title", title).limit(1).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "Song not found"}
                
        except Exception as e:
            logger.error(f"Error getting song by artist and title: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_song_by_spotify_id(self, spotify_id: str) -> Dict[str, Any]:
        """
        根据Spotify ID获取歌曲信息
        
        Args:
            spotify_id: Spotify歌曲ID
            
        Returns:
            歌曲详细信息
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("songs").select("*").eq("spotify_id", spotify_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0]
                }
            else:
                return {"success": False, "error": "Song not found"}
                
        except Exception as e:
            logger.error(f"Error getting song by Spotify ID: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_songs_by_artist(self, artist_id: UUID, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        获取艺术家的歌曲列表
        
        Args:
            artist_id: 艺术家UUID
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            歌曲列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("songs").select("*").eq("artist_id", str(artist_id)).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "artist_id": str(artist_id),
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting songs by artist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_song_spotify_data(self, song_id: UUID, spotify_data: Dict[str, Any], spotify_id: str = None) -> Dict[str, Any]:
        """
        更新歌曲的Spotify数据
        
        Args:
            song_id: 歌曲UUID
            spotify_data: Spotify歌曲数据
            spotify_id: Spotify歌曲ID（可选）
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            update_data = {
                "spotify_data": spotify_data,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if spotify_id:
                update_data["spotify_id"] = spotify_id
            
            # 从Spotify数据中提取有用信息
            if "preview_url" in spotify_data and spotify_data["preview_url"]:
                update_data["preview_url"] = spotify_data["preview_url"]
            if "duration_ms" in spotify_data:
                update_data["duration_seconds"] = spotify_data["duration_ms"] // 1000
            if "album" in spotify_data and "name" in spotify_data["album"]:
                update_data["album_name"] = spotify_data["album"]["name"]
            if "album" in spotify_data and "release_date" in spotify_data["album"]:
                try:
                    release_date = datetime.strptime(spotify_data["album"]["release_date"], "%Y-%m-%d").date()
                    update_data["release_date"] = release_date.isoformat()
                except:
                    pass  # 忽略日期解析错误
            
            result = self.db.supabase.table("songs").update(update_data).eq("id", str(song_id)).execute()
            
            if result.data:
                logger.info(f"Song Spotify data updated: {song_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Spotify data updated successfully"
                }
            else:
                return {"success": False, "error": "Failed to update Spotify data"}
                
        except Exception as e:
            logger.error(f"Error updating song Spotify data: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_song_itunes_data(self, song_id: UUID, itunes_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新歌曲的iTunes数据
        
        Args:
            song_id: 歌曲UUID
            itunes_data: iTunes歌曲数据
            
        Returns:
            更新结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            update_data = {
                "itunes_data": itunes_data,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 从iTunes数据中提取有用信息
            if "previewUrl" in itunes_data and itunes_data["previewUrl"]:
                update_data["preview_url"] = itunes_data["previewUrl"]
            if "trackTimeMillis" in itunes_data:
                update_data["duration_seconds"] = itunes_data["trackTimeMillis"] // 1000
            if "collectionName" in itunes_data:
                update_data["album_name"] = itunes_data["collectionName"]
            if "releaseDate" in itunes_data:
                try:
                    release_date = datetime.strptime(itunes_data["releaseDate"][:10], "%Y-%m-%d").date()
                    update_data["release_date"] = release_date.isoformat()
                except:
                    pass  # 忽略日期解析错误
            
            result = self.db.supabase.table("songs").update(update_data).eq("id", str(song_id)).execute()
            
            if result.data:
                logger.info(f"Song iTunes data updated: {song_id}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "iTunes data updated successfully"
                }
            else:
                return {"success": False, "error": "Failed to update iTunes data"}
                
        except Exception as e:
            logger.error(f"Error updating song iTunes data: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def batch_create_songs(self, songs_data: List[CreateSongRequest]) -> Dict[str, Any]:
        """
        批量创建歌曲（用于从Spotify API获取艺术家热门歌曲后批量插入）
        
        Args:
            songs_data: 歌曲创建请求数据列表
            
        Returns:
            批量创建结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            insert_data_list = []
            for song_data in songs_data:
                insert_data = {
                    "artist_id": str(song_data.artist_id),
                    "title": song_data.title,
                    "album_name": song_data.album_name,
                    "duration_seconds": song_data.duration_seconds,
                    "preview_url": song_data.preview_url,
                    "spotify_id": song_data.spotify_id,
                    "release_date": song_data.release_date.isoformat() if song_data.release_date else None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                insert_data_list.append(insert_data)
            
            # 执行批量插入操作
            result = self.db.supabase.table("songs").insert(insert_data_list).execute()
            
            if result.data:
                logger.info(f"Batch created {len(result.data)} songs successfully")
                return {
                    "success": True,
                    "data": result.data,
                    "count": len(result.data),
                    "message": f"Successfully created {len(result.data)} songs"
                }
            else:
                return {"success": False, "error": "Failed to batch create songs"}
                
        except Exception as e:
            logger.error(f"Error batch creating songs: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def search_songs(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        搜索歌曲（支持歌曲标题和专辑名称搜索）
        
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
            # 使用ilike进行模糊搜索
            result = self.db.supabase.table("songs").select("*, artists(name, name_zh, name_en)").or_(
                f"title.ilike.%{query}%,album_name.ilike.%{query}%"
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
            logger.error(f"Error searching songs: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_songs_with_preview(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        获取有预览URL的歌曲列表
        
        Args:
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            有预览的歌曲列表
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("songs").select("*, artists(name, name_zh, image_url)").not_.is_("preview_url", "null").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data),
                "limit": limit,
                "offset": offset
            }
                
        except Exception as e:
            logger.error(f"Error getting songs with preview: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_song(self, song_id: UUID) -> Dict[str, Any]:
        """
        删除歌曲
        
        Args:
            song_id: 歌曲UUID
            
        Returns:
            删除结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("songs").delete().eq("id", str(song_id)).execute()
            
            if result.data:
                logger.info(f"Song deleted successfully: {song_id}")
                return {
                    "success": True,
                    "message": "Song deleted successfully"
                }
            else:
                return {"success": False, "error": "Song not found or delete failed"}
                
        except Exception as e:
            logger.error(f"Error deleting song: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_songs_by_artist(self, artist_id: UUID) -> Dict[str, Any]:
        """
        删除艺术家的所有歌曲（用于艺术家删除时的级联操作）
        
        Args:
            artist_id: 艺术家UUID
            
        Returns:
            删除结果
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            result = self.db.supabase.table("songs").delete().eq("artist_id", str(artist_id)).execute()
            
            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} songs for artist: {artist_id}")
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Deleted {deleted_count} songs successfully"
            }
                
        except Exception as e:
            logger.error(f"Error deleting songs by artist: {str(e)}")
            return {"success": False, "error": str(e)}

# 创建全局歌曲数据库服务实例
song_db_service = SongDatabaseService()