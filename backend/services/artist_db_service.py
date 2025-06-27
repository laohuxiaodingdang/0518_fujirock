"""
艺术家数据库服务 - 管理艺术家相关的数据库操作
"""
import re
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
    
    def normalize_artist_name(self, name: str) -> str:
        """
        标准化艺术家名称，用于匹配比较
        - 转换为小写
        - 移除特殊符号和多余空格
        
        Args:
            name: 原始艺术家名称
            
        Returns:
            标准化后的名称
        """
        if not name:
            return ""
        
        normalized = name.lower()
        # 移除特殊符号但保留字母数字和空格
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # 移除多余的空格
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def calculate_similarity_score(self, query: str, target: str) -> float:
        """
        计算两个字符串的相似度分数
        
        Args:
            query: 查询字符串
            target: 目标字符串
            
        Returns:
            相似度分数 (0.0 - 1.0)
        """
        if not query or not target:
            return 0.0
        
        # 标准化两个字符串
        norm_query = self.normalize_artist_name(query)
        norm_target = self.normalize_artist_name(target)
        
        # 完全匹配
        if norm_query == norm_target:
            return 1.0
        
        # 包含匹配
        if norm_query in norm_target or norm_target in norm_query:
            return 0.8
        
        # 计算编辑距离相似度
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(norm_query, norm_target)
        max_len = max(len(norm_query), len(norm_target))
        
        if max_len == 0:
            return 0.0
        
        similarity = 1.0 - (distance / max_len)
        
        # 如果相似度很高，给予更高的分数
        if similarity > 0.7:
            return similarity
        
        # 检查单词级别的匹配
        query_words = norm_query.split()
        target_words = norm_target.split()
        
        if query_words and target_words:
            word_matches = 0
            for query_word in query_words:
                for target_word in target_words:
                    if query_word == target_word or query_word in target_word or target_word in query_word:
                        word_matches += 1
                        break
            
            word_similarity = word_matches / max(len(query_words), len(target_words))
            return max(similarity, word_similarity * 0.6)
        
        return similarity if similarity > 0.5 else 0.0
    
    
    async def get_artist_by_name_fuzzy(self, name: str) -> Dict[str, Any]:
        """
        根据名称获取艺术家信息（支持增强模糊匹配）
        
        Args:
            name: 艺术家名称
            
        Returns:
            艺术家详细信息，包含匹配类型和相似度分数
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 1. 首先尝试精确匹配
            result = self.db.supabase.table("artists").select("*").eq("name", name).limit(1).execute()
            
            if result.data:
                logger.info(f"Exact match found for: {name}")
                return {
                    "success": True,
                    "data": result.data[0],
                    "match_type": "exact",
                    "similarity_score": 1.0
                }
            
            # 2. 获取所有艺术家进行模糊匹配
            logger.info(f"Attempting fuzzy match for: '{name}'")
            all_artists = self.db.supabase.table("artists").select("*").execute()
            
            if not all_artists.data:
                return {"success": False, "error": "No artists found in database"}
            
            # 3. 计算所有艺术家的相似度分数
            candidates = []
            for artist in all_artists.data:
                artist_name = artist.get("name", "")
                if not artist_name:
                    continue
                
                similarity_score = self.calculate_similarity_score(name, artist_name)
                
                if similarity_score > 0.0:  # 只保留有相似度的结果
                    candidates.append({
                        "artist": artist,
                        "similarity_score": similarity_score,
                        "original_query": name,
                        "matched_name": artist_name
                    })
            
            if not candidates:
                logger.warning(f"No fuzzy matches found for: {name}")
                return {"success": False, "error": "Artist not found"}
            
            # 4. 按相似度分数排序，取最佳匹配
            candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
            best_match = candidates[0]
            
            # 5. 确定匹配类型
            match_type = "fuzzy"
            if best_match["similarity_score"] == 1.0:
                match_type = "exact"
            elif best_match["similarity_score"] >= 0.8:
                match_type = "high_similarity"
            elif best_match["similarity_score"] >= 0.6:
                match_type = "medium_similarity"
            else:
                match_type = "low_similarity"
            
            logger.info(f"Best match found: '{name}' -> '{best_match['matched_name']}' "
                       f"(score: {best_match['similarity_score']:.3f}, type: {match_type})")
            
            return {
                "success": True,
                "data": best_match["artist"],
                "match_type": match_type,
                "similarity_score": best_match["similarity_score"],
                "original_query": name,
                "matched_name": best_match["matched_name"],
                "all_candidates": [
                    {
                        "name": c["matched_name"],
                        "score": c["similarity_score"]
                    } for c in candidates[:5]  # 返回前5个候选结果
                ]
            }
                    
        except Exception as e:
            logger.error(f"Error getting artist by name (fuzzy): {str(e)}")
            return {"success": False, "error": str(e)}
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
            # 使用模糊匹配检查艺术家是否已存在
            existing = await self.get_artist_by_name_fuzzy(artist_data.get("name"))
            if existing.get("success") and existing.get("data"):
                return {
                    "success": False, 
                    "error": "Artist already exists",
                    "existing_artist_id": existing["data"]["id"],
                    "match_type": existing.get("match_type", "unknown"),
                    "matched_name": existing.get("matched_name", "")
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
        根据名称获取艺术家信息（精确匹配）
        
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
        搜索艺术家（支持增强模糊匹配和全文搜索）
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            offset: 偏移量
            
        Returns:
            搜索结果列表，按相似度排序
        """
        if not self.db.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # 如果查询为空，返回所有艺术家
            if not query.strip():
                result = self.db.supabase.table("artists").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
                return {
                    "success": True,
                    "data": result.data,
                    "count": len(result.data),
                    "query": query,
                    "limit": limit,
                    "offset": offset,
                    "search_type": "all"
                }
            
            # 获取所有艺术家进行模糊匹配
            all_artists = self.db.supabase.table("artists").select("*").execute()
            
            if not all_artists.data:
                return {"success": False, "error": "No artists found in database"}
            
            # 计算所有艺术家的相似度分数
            candidates = []
            for artist in all_artists.data:
                artist_name = artist.get("name", "")
                artist_description = artist.get("description", "")
                
                if not artist_name:
                    continue
                
                # 计算名称相似度
                name_similarity = self.calculate_similarity_score(query, artist_name)
                
                # 计算描述相似度（权重较低）
                description_similarity = 0.0
                if artist_description and len(query) > 2:
                    # 简单的关键词匹配
                    query_lower = query.lower()
                    description_lower = artist_description.lower()
                    if query_lower in description_lower:
                        description_similarity = 0.3
                
                # 综合相似度分数
                total_similarity = name_similarity + (description_similarity * 0.3)
                
                if total_similarity > 0.0:
                    candidates.append({
                        "artist": artist,
                        "similarity_score": total_similarity,
                        "name_similarity": name_similarity,
                        "description_similarity": description_similarity,
                        "original_query": query,
                        "matched_name": artist_name
                    })
            
            if not candidates:
                logger.warning(f"No matches found for: {query}")
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "query": query,
                    "limit": limit,
                    "offset": offset,
                    "search_type": "fuzzy_no_results"
                }
            
            # 按相似度分数排序
            candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # 应用分页
            paginated_candidates = candidates[offset:offset + limit]
            
            # 准备返回数据
            result_data = []
            for candidate in paginated_candidates:
                artist_data = candidate["artist"].copy()
                # 添加搜索元数据
                artist_data["_search_metadata"] = {
                    "similarity_score": candidate["similarity_score"],
                    "name_similarity": candidate["name_similarity"],
                    "description_similarity": candidate["description_similarity"],
                    "original_query": query,
                    "matched_name": candidate["matched_name"]
                }
                result_data.append(artist_data)
            
            # 确定搜索类型
            search_type = "fuzzy"
            if candidates and candidates[0]["similarity_score"] == 1.0:
                search_type = "exact"
            elif candidates and candidates[0]["similarity_score"] >= 0.8:
                search_type = "high_similarity"
            
            logger.info(f"Search completed: '{query}' -> {len(candidates)} candidates, "
                       f"returning {len(result_data)} results (type: {search_type})")
            
            return {
                "success": True,
                "data": result_data,
                "count": len(result_data),
                "total_candidates": len(candidates),
                "query": query,
                "limit": limit,
                "offset": offset,
                "search_type": search_type,
                "best_match_score": candidates[0]["similarity_score"] if candidates else 0.0
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