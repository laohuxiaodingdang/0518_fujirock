"""
iTunes API Service
提供音频预览功能，作为Spotify preview_url的替代方案
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from config import settings

logger = logging.getLogger(__name__)

class iTunesService:
    """iTunes API服务类"""
    
    def __init__(self):
        self.base_url = "https://itunes.apple.com/search"
        self.timeout = settings.ITUNES_TIMEOUT  # 使用专门的iTunes超时配置
    
    async def search_track(self, artist_name: str, track_name: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """
        在iTunes中搜索歌曲
        
        Args:
            artist_name: 艺术家名称
            track_name: 歌曲名称
            limit: 返回结果数量限制
            
        Returns:
            iTunes搜索结果，包含预览URL
        """
        try:
            # 构建搜索查询
            query = f"{artist_name} {track_name}"
            
            params = {
                "term": query,  # 不要手动编码，让httpx处理
                "media": "music",
                "entity": "song",
                "limit": limit,
                "country": "US"  # 使用美国区域获得更好的覆盖率
            }
            
            logger.info(f"Searching iTunes for: {query}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"iTunes API returned {data.get('resultCount', 0)} results")
                
                if data.get("resultCount", 0) > 0:
                    # 寻找最匹配的结果
                    best_match = self._find_best_match(
                        data["results"], 
                        artist_name, 
                        track_name
                    )
                    
                    if best_match:
                        has_preview = bool(best_match.get("previewUrl"))
                        logger.info(f"Found match: {best_match.get('trackName')} by {best_match.get('artistName')}, has preview: {has_preview}")
                        
                        return {
                            "success": True,
                            "data": {
                                "track_name": best_match.get("trackName"),
                                "artist_name": best_match.get("artistName"),
                                "album_name": best_match.get("collectionName"),
                                "preview_url": best_match.get("previewUrl"),
                                "artwork_url": best_match.get("artworkUrl100"),
                                "track_time_millis": best_match.get("trackTimeMillis"),
                                "itunes_url": best_match.get("trackViewUrl"),
                                "genre": best_match.get("primaryGenreName"),
                                "release_date": best_match.get("releaseDate")
                            }
                        }
                
                # 如果第一次搜索失败，尝试更宽松的搜索
                if artist_name and track_name:
                    logger.info(f"First search failed, trying fallback search strategies")
                    
                    # 策略1: 只用歌曲名称搜索
                    fallback_params = {
                        "term": track_name,
                        "media": "music", 
                        "entity": "song",
                        "limit": limit * 2,  # 增加结果数量
                        "country": "US"
                    }
                    
                    response = await client.get(self.base_url, params=fallback_params)
                    response.raise_for_status()
                    
                    data = response.json()
                    logger.info(f"Fallback search returned {data.get('resultCount', 0)} results")
                    
                    if data.get("resultCount", 0) > 0:
                        best_match = self._find_best_match_fuzzy(
                            data["results"], 
                            artist_name, 
                            track_name
                        )
                        
                        if best_match:
                            has_preview = bool(best_match.get("previewUrl"))
                            logger.info(f"Fallback found match: {best_match.get('trackName')} by {best_match.get('artistName')}, has preview: {has_preview}")
                            
                            return {
                                "success": True,
                                "data": {
                                    "track_name": best_match.get("trackName"),
                                    "artist_name": best_match.get("artistName"),
                                    "album_name": best_match.get("collectionName"),
                                    "preview_url": best_match.get("previewUrl"),
                                    "artwork_url": best_match.get("artworkUrl100"),
                                    "track_time_millis": best_match.get("trackTimeMillis"),
                                    "itunes_url": best_match.get("trackViewUrl"),
                                    "genre": best_match.get("primaryGenreName"),
                                    "release_date": best_match.get("releaseDate")
                                }
                            }
                
                logger.warning(f"No matching tracks found for: {query}")
                return {
                    "success": False,
                    "error": "No matching tracks found in iTunes"
                }
                
        except httpx.TimeoutException:
            logger.error(f"iTunes API timeout for query: {artist_name} - {track_name}")
            return {
                "success": False,
                "error": "iTunes API request timeout"
            }
        except Exception as e:
            logger.error(f"iTunes API error: {str(e)}")
            return {
                "success": False,
                "error": f"iTunes API error: {str(e)}"
            }
    
    def _find_best_match(self, results: List[Dict], artist_name: str, track_name: str) -> Optional[Dict]:
        """
        从搜索结果中找到最佳匹配
        
        Args:
            results: iTunes搜索结果列表
            artist_name: 目标艺术家名称
            track_name: 目标歌曲名称
            
        Returns:
            最佳匹配的结果
        """
        if not results:
            return None
        
        logger.info(f"Searching through {len(results)} results for best match")
        
        # 优先返回第一个有预览URL的结果（iTunes搜索通常按相关性排序）
        for i, result in enumerate(results):
            has_preview = bool(result.get("previewUrl"))
            logger.info(f"Result {i+1}: {result.get('trackName')} by {result.get('artistName')}, has preview: {has_preview}")
            if has_preview:
                return result
        
        # 如果没有找到有预览URL的结果，返回第一个结果
        logger.info(f"No results with preview found, returning first result: {results[0].get('trackName')}")
        return results[0]
    
    def _find_best_match_fuzzy(self, results: List[Dict], artist_name: str, track_name: str) -> Optional[Dict]:
        """
        从搜索结果中找到最佳匹配（模糊匹配）
        
        Args:
            results: iTunes搜索结果列表
            artist_name: 目标艺术家名称
            track_name: 目标歌曲名称
            
        Returns:
            最佳匹配的结果
        """
        if not results:
            return None
        
        logger.info(f"Fuzzy searching through {len(results)} results for best match")
        
        def similarity_score(result_artist: str, result_track: str, target_artist: str, target_track: str) -> float:
            """计算相似度分数"""
            score = 0.0
            
            # 艺术家名称匹配（权重0.4）
            result_artist_lower = result_artist.lower()
            target_artist_lower = target_artist.lower()
            
            if target_artist_lower in result_artist_lower or result_artist_lower in target_artist_lower:
                score += 0.4
            elif any(word in result_artist_lower for word in target_artist_lower.split()):
                score += 0.2
            
            # 歌曲名称匹配（权重0.6）
            result_track_lower = result_track.lower()
            target_track_lower = target_track.lower()
            
            if target_track_lower in result_track_lower or result_track_lower in target_track_lower:
                score += 0.6
            elif any(word in result_track_lower for word in target_track_lower.split() if len(word) > 2):
                score += 0.3
            
            return score
        
        best_match = None
        best_score = 0.0
        
        for i, result in enumerate(results):
            has_preview = bool(result.get("previewUrl"))
            result_artist = result.get("artistName", "")
            result_track = result.get("trackName", "")
            
            score = similarity_score(result_artist, result_track, artist_name, track_name)
            
            # 有预览的结果获得额外分数
            if has_preview:
                score += 0.1
            
            logger.info(f"Result {i+1}: {result_track} by {result_artist}, score: {score:.2f}, has preview: {has_preview}")
            
            if score > best_score:
                best_score = score
                best_match = result
        
        if best_match and best_score > 0.3:  # 最低相似度阈值
            logger.info(f"Best fuzzy match: {best_match.get('trackName')} by {best_match.get('artistName')}, score: {best_score:.2f}")
            return best_match
        
        logger.info("No good fuzzy match found")
        return None
    
    async def get_artist_top_tracks(self, artist_name: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        获取艺术家的热门歌曲（通过搜索实现）
        
        Args:
            artist_name: 艺术家名称
            limit: 返回结果数量限制
            
        Returns:
            艺术家热门歌曲列表
        """
        try:
            params = {
                "term": artist_name,  # 不要手动编码，让httpx处理
                "media": "music",
                "entity": "song",
                "limit": limit,
                "country": "US"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("resultCount", 0) > 0:
                    tracks = []
                    for result in data["results"]:
                        # 只包含有预览URL的歌曲
                        if result.get("previewUrl"):
                            tracks.append({
                                "track_name": result.get("trackName"),
                                "artist_name": result.get("artistName"),
                                "album_name": result.get("collectionName"),
                                "preview_url": result.get("previewUrl"),
                                "artwork_url": result.get("artworkUrl100"),
                                "track_time_millis": result.get("trackTimeMillis"),
                                "itunes_url": result.get("trackViewUrl"),
                                "genre": result.get("primaryGenreName")
                            })
                    
                    return {
                        "success": True,
                        "data": {
                            "artist_name": artist_name,
                            "tracks": tracks,
                            "total_count": len(tracks)
                        }
                    }
                
                return {
                    "success": False,
                    "error": "No tracks found for this artist in iTunes"
                }
                
        except Exception as e:
            logger.error(f"iTunes API error for artist {artist_name}: {str(e)}")
            return {
                "success": False,
                "error": f"iTunes API error: {str(e)}"
            }

# 全局实例
itunes_service = iTunesService() 