"""
Spotify 服务 - 处理 Spotify API 相关逻辑
"""
import httpx
import logging
import base64
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from config import settings
from models.spotify import (
    SpotifyArtist, SpotifyImage, SpotifyTrack, SpotifyAlbum, 
    SpotifyPlaylist, SpotifyPlaylistRequest
)

logger = logging.getLogger(__name__)

class SpotifyService:
    """Spotify API 服务类"""
    
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.api_url = settings.SPOTIFY_API_URL
        self.auth_url = settings.SPOTIFY_AUTH_URL
        self.timeout = settings.SPOTIFY_TIMEOUT  # 使用专门的Spotify超时配置
        self._access_token = None
        self._token_expires_at = None
    
    async def get_mock_artist_data(self, artist_name: str) -> SpotifyArtist:
        """获取 Mock 艺术家数据"""
        logger.info(f"Using MOCK Spotify API for artist {artist_name}")
        
        # 根据艺术家名称提供不同的Mock数据
        mock_data = {
            "Radiohead": {
                "id": "4Z8W4fKeB5YxbusRsdQVPb",
                "name": "Radiohead",
                "images": [
                    "https://i.scdn.co/image/ab6761610000e5eba03696716c9ee605006047fd",
                    "https://i.scdn.co/image/ab67616100005174a03696716c9ee605006047fd"
                ],
                "genres": ["alternative rock", "art rock", "electronic"],
                "popularity": 82,
                "followers": 12500000
            },
            "Nirvana": {
                "id": "6olE6TJLqED3rqDCT0FyPh",
                "name": "Nirvana",
                "images": [
                    "https://i.scdn.co/image/ab6761610000e5eb4b9d2671bb8c1d5a8e8d4e8a",
                    "https://i.scdn.co/image/ab676161000051744b9d2671bb8c1d5a8e8d4e8a"
                ],
                "genres": ["grunge", "alternative rock", "rock"],
                "popularity": 85,
                "followers": 22000000
            },
            "The Beatles": {
                "id": "3WrFJ7ztbogyGnTHbHJFl2",
                "name": "The Beatles",
                "images": [
                    "https://i.scdn.co/image/ab6761610000e5ebe9348cc01ff5d55971b22433",
                    "https://i.scdn.co/image/ab67616100005174e9348cc01ff5d55971b22433"
                ],
                "genres": ["rock", "pop rock", "psychedelic rock"],
                "popularity": 88,
                "followers": 35000000
            },
            "Coldplay": {
                "id": "4gzpq5DPGxSnKTe4SA8HAU",
                "name": "Coldplay",
                "images": [
                    "https://i.scdn.co/image/ab6761610000e5eb1ba8fc5f5c73256e6e5f8e8a",
                    "https://i.scdn.co/image/ab676161000051741ba8fc5f5c73256e6e5f8e8a"
                ],
                "genres": ["alternative rock", "pop rock", "post-britpop"],
                "popularity": 84,
                "followers": 28000000
            }
        }
        
        # 获取特定艺术家的数据，如果没有则使用默认数据
        artist_data = mock_data.get(artist_name, {
            "id": f"mock_{artist_name.lower().replace(' ', '_')}",
            "name": artist_name,
            "images": [
                "https://via.placeholder.com/640x640/1db954/ffffff?text=Mock+Artist",
                "https://via.placeholder.com/320x320/1db954/ffffff?text=Mock+Artist"
            ],
            "genres": ["Rock", "Alternative", "Mock Genre"],
            "popularity": 75,
            "followers": 1000000
        })
        
        return SpotifyArtist(
            id=artist_data["id"],
            name=artist_data["name"],
            images=[
                SpotifyImage(
                    url=artist_data["images"][0],
                    height=640,
                    width=640
                ),
                SpotifyImage(
                    url=artist_data["images"][1],
                    height=320,
                    width=320
                )
            ],
            genres=artist_data["genres"],
            popularity=artist_data["popularity"],
            followers={"total": artist_data["followers"]},
            external_urls={"spotify": f"https://open.spotify.com/artist/{artist_data['id']}"}
        )
    
    async def get_mock_tracks_data(self, spotify_id: str, limit: int = 10) -> List[SpotifyTrack]:
        """获取 Mock 曲目数据"""
        logger.info(f"Using MOCK Spotify API for tracks of {spotify_id}")
        
        # 根据 spotify_id 确定艺术家名称
        id_to_name = {
            "4Z8W4fKeB5YxbusRsdQVPb": "Radiohead",
            "6olE6TJLqED3rqDCT0FyPh": "Nirvana", 
            "7dE2MLL2SaI6MujpU5HFVi": "Nirvana",  # 真实的Nirvana ID
            "3WrFJ7ztbogyGnTHbHJFl2": "The Beatles",
            "4gzpq5DPGxSnKTe4SA8HAU": "Coldplay"
        }
        
        artist_name = id_to_name.get(spotify_id, "Unknown Artist")
        
        # 根据艺术家提供不同的歌曲 - 扩展歌曲列表并确保唯一性
        track_names = {
            "Nirvana": [
                "Smells Like Teen Spirit", 
                "Come As You Are", 
                "Lithium", 
                "In Bloom", 
                "Heart-Shaped Box",
                "About a Girl",
                "The Man Who Sold the World",
                "Where Did You Sleep Last Night",
                "All Apologies",
                "Rape Me"
            ],
            "Radiohead": [
                "Creep", 
                "Karma Police", 
                "No Surprises", 
                "Paranoid Android", 
                "High and Dry",
                "Fake Plastic Trees",
                "Street Spirit (Fade Out)",
                "Just",
                "My Iron Lung",
                "The Bends"
            ],
            "The Beatles": [
                "Hey Jude", 
                "Let It Be", 
                "Yesterday", 
                "Come Together", 
                "Here Comes the Sun",
                "Something",
                "While My Guitar Gently Weeps",
                "A Hard Day's Night",
                "Help!",
                "Norwegian Wood"
            ],
            "Coldplay": [
                "Yellow", 
                "The Scientist", 
                "Clocks", 
                "Fix You", 
                "Viva La Vida",
                "Paradise",
                "Speed of Sound",
                "In My Place",
                "Trouble",
                "Don't Panic"
            ]
        }
        
        songs = track_names.get(artist_name, [f"Mock Track {i + 1}" for i in range(10)])
        
        # 去重逻辑：使用set来跟踪已添加的歌曲名称（忽略大小写）
        seen_tracks = set()
        unique_songs = []
        
        for song in songs:
            song_lower = song.lower().strip()
            # 移除常见的变体标识符
            normalized_song = song_lower.replace("(", "").replace(")", "").replace("-", " ").strip()
            
            if normalized_song not in seen_tracks:
                seen_tracks.add(normalized_song)
                unique_songs.append(song)
        
        tracks = []
        for i in range(min(limit, len(unique_songs))):
            album = SpotifyAlbum(
                id=f"mock_album_{i}",
                name=f"Greatest Hits" if i < 3 else f"Album {i + 1}",
                images=[
                    SpotifyImage(
                        url=f"https://via.placeholder.com/640x640/1db954/ffffff?text=Album+{i+1}",
                        height=640,
                        width=640
                    )
                ],
                release_date="2023-01-01",
                total_tracks=12
            )
            
            # 添加艺术家信息
            artists = [{
                "id": spotify_id,
                "name": artist_name,
                "external_urls": {
                    "spotify": f"https://open.spotify.com/artist/{spotify_id}"
                }
            }]
            
            track = SpotifyTrack(
                id=f"mock_track_{i}_{unique_songs[i].replace(' ', '_').lower()}",
                name=unique_songs[i],
                album=album,
                artists=artists,  # 添加艺术家信息
                duration_ms=180000 + (i * 15000),  # 3-4 分钟
                popularity=85 - (i * 3),
                preview_url=None,  # Mock数据没有预览URL，这样会触发iTunes搜索
                explicit=False,
                external_urls={
                    "spotify": f"https://open.spotify.com/track/mock_track_{i}_{unique_songs[i].replace(' ', '_').lower()}"
                }
            )
            tracks.append(track)
        
        logger.info(f"Generated {len(tracks)} unique tracks for {artist_name}")
        return tracks
    
    async def _get_access_token(self) -> str:
        """获取 Spotify 访问令牌"""
        if not self.client_id or not self.client_secret:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Credentials not configured",
                    "message": "Spotify API credentials are not configured. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in environment variables.",
                    "service": "Spotify"
                }
            )
        
        # 检查现有 token 是否仍然有效
        if self._access_token and self._token_expires_at:
            import time
            if time.time() < self._token_expires_at:
                return self._access_token
        
        # 获取新的访问令牌
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_base64 = base64.b64encode(auth_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.auth_url,
                    headers=headers,
                    data=data
                )
                
                if response.status_code == 400:
                    error_data = response.json() if response.content else {}
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Invalid credentials",
                            "message": error_data.get("error_description", "Invalid Spotify API credentials"),
                            "service": "Spotify"
                        }
                    )
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail={
                            "error": "Authentication failed",
                            "message": f"Failed to authenticate with Spotify API: {response.status_code}",
                            "service": "Spotify"
                        }
                    )
                
                token_data = response.json()
                self._access_token = token_data["access_token"]
                
                # 计算 token 过期时间（提前 5 分钟刷新）
                import time
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in - 300
                
                return self._access_token
                
            except httpx.TimeoutException:
                logger.error("Spotify authentication timeout")
                raise HTTPException(
                    status_code=408,
                    detail={
                        "error": "Authentication timeout",
                        "message": f"Spotify authentication timeout after {self.timeout} seconds",
                        "service": "Spotify"
                    }
                )
            except httpx.RequestError as e:
                logger.error(f"Spotify authentication network error: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Network error",
                        "message": f"Failed to connect to Spotify authentication service: {str(e)}",
                        "service": "Spotify"
                    }
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Spotify authentication: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Authentication error",
                        "message": "An unexpected error occurred during Spotify authentication",
                        "details": str(e)
                    }
                )
    
    async def get_real_artist_data(self, spotify_id: str) -> SpotifyArtist:
        """获取真实 Spotify 艺术家数据"""
        logger.info(f"Using REAL Spotify API for artist {spotify_id}")
        
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/artists/{spotify_id}",
                    headers=headers
                )
                
                if response.status_code == 400:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Invalid artist ID",
                            "message": f"Invalid Spotify artist ID: {spotify_id}",
                            "service": "Spotify"
                        }
                    )
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "Artist not found",
                            "message": f"Artist with ID '{spotify_id}' not found on Spotify",
                            "service": "Spotify"
                        }
                    )
                elif response.status_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail={
                            "error": "Authentication failed",
                            "message": "Spotify API authentication failed",
                            "service": "Spotify"
                        }
                    )
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail={
                            "error": "Spotify API error",
                            "message": f"Spotify API returned status {response.status_code}",
                            "service": "Spotify"
                        }
                    )
                
                data = response.json()
                
                # 解析图片
                images = [
                    SpotifyImage(
                        url=img["url"],
                        height=img["height"],
                        width=img["width"]
                    )
                    for img in data.get("images", [])
                ]
                
                return SpotifyArtist(
                    id=data["id"],
                    name=data["name"],
                    images=images,
                    genres=data.get("genres", []),
                    popularity=data.get("popularity", 0),
                    followers=data.get("followers", {"total": 0}),
                    external_urls=data.get("external_urls", {})
                )
                
            except httpx.TimeoutException:
                logger.error(f"Spotify API timeout for artist {spotify_id}")
                raise HTTPException(
                    status_code=408,
                    detail={
                        "error": "Request timeout",
                        "message": f"Spotify API request timeout after {self.timeout} seconds",
                        "service": "Spotify"
                    }
                )
            except httpx.RequestError as e:
                logger.error(f"Spotify API network error: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Network error",
                        "message": f"Failed to connect to Spotify API: {str(e)}",
                        "service": "Spotify"
                    }
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Spotify artist service: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": "An unexpected error occurred while processing Spotify artist data",
                        "details": str(e)
                    }
                )
    
    async def get_real_tracks_data(self, spotify_id: str, limit: int = 10, market: str = "JP") -> List[SpotifyTrack]:
        """获取真实 Spotify 热门曲目数据"""
        logger.info(f"Using REAL Spotify API for tracks of {spotify_id}")
        
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/artists/{spotify_id}/top-tracks",
                    headers=headers,
                    params={"market": market}
                )
                
                if response.status_code == 400:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Invalid request",
                            "message": f"Invalid artist ID or market code: {spotify_id}, {market}",
                            "service": "Spotify"
                        }
                    )
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "Artist not found",
                            "message": f"Artist with ID '{spotify_id}' not found",
                            "service": "Spotify"
                        }
                    )
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail={
                            "error": "Spotify API error",
                            "message": f"Failed to get top tracks from Spotify: {response.status_code}",
                            "service": "Spotify"
                        }
                    )
                
                data = response.json()
                tracks = []
                
                for track_data in data.get("tracks", [])[:limit]:
                    # 解析专辑信息
                    album_data = track_data.get("album", {})
                    album_images = [
                        SpotifyImage(
                            url=img["url"],
                            height=img["height"],
                            width=img["width"]
                        )
                        for img in album_data.get("images", [])
                    ]
                    
                    album = SpotifyAlbum(
                        id=album_data.get("id", ""),
                        name=album_data.get("name", ""),
                        images=album_images,
                        release_date=album_data.get("release_date", ""),
                        total_tracks=album_data.get("total_tracks", 0)
                    )
                    
                    # 解析艺术家信息
                    artists = []
                    for artist_data in track_data.get("artists", []):
                        artists.append({
                            "id": artist_data.get("id", ""),
                            "name": artist_data.get("name", ""),
                            "external_urls": artist_data.get("external_urls", {})
                        })
                    
                    track = SpotifyTrack(
                        id=track_data["id"],
                        name=track_data["name"],
                        album=album,
                        artists=artists,  # 添加艺术家信息
                        duration_ms=track_data.get("duration_ms", 0),
                        popularity=track_data.get("popularity", 0),
                        preview_url=track_data.get("preview_url"),
                        explicit=track_data.get("explicit", False),
                        external_urls=track_data.get("external_urls", {})
                    )
                    tracks.append(track)
                
                return tracks
                
            except httpx.TimeoutException:
                logger.error(f"Spotify API timeout for tracks of {spotify_id}")
                raise HTTPException(
                    status_code=408,
                    detail={
                        "error": "Request timeout",
                        "message": f"Spotify API request timeout after {self.timeout} seconds",
                        "service": "Spotify"
                    }
                )
            except httpx.RequestError as e:
                logger.error(f"Spotify API network error: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Network error",
                        "message": f"Failed to connect to Spotify API: {str(e)}",
                        "service": "Spotify"
                    }
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Spotify tracks service: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": "An unexpected error occurred while processing Spotify tracks data",
                        "details": str(e)
                    }
                )
    
    async def get_artist_info(self, spotify_id: str) -> SpotifyArtist:
        """
        获取艺术家信息 - 根据环境选择数据源
        
        Args:
            spotify_id: Spotify 艺术家 ID
            
        Returns:
            SpotifyArtist: 艺术家信息
            
        Raises:
            HTTPException: 当 API 调用失败时
        """
        if settings.is_production and self.is_available():
            return await self.get_real_artist_data(spotify_id)
        else:
            # 在开发环境下，根据ID映射到艺术家名称
            id_to_name = {
                "4Z8W4fKeB5YxbusRsdQVPb": "Radiohead",
                "6olE6TJLqED3rqDCT0FyPh": "Nirvana", 
                "3WrFJ7ztbogyGnTHbHJFl2": "The Beatles",
                "4gzpq5DPGxSnKTe4SA8HAU": "Coldplay"
            }
            
            artist_name = id_to_name.get(spotify_id, spotify_id)
            return await self.get_mock_artist_data(artist_name)
    
    async def get_top_tracks(self, spotify_id: str, limit: int = 10, market: str = "JP") -> List[SpotifyTrack]:
        """
        获取热门曲目 - 根据环境选择数据源
        
        Args:
            spotify_id: Spotify 艺术家 ID
            limit: 返回数量限制
            market: 市场代码
            
        Returns:
            List[SpotifyTrack]: 热门曲目列表
            
        Raises:
            HTTPException: 当 API 调用失败时
        """
        if settings.is_production and self.is_available():
            return await self.get_real_tracks_data(spotify_id, limit, market)
        else:
            return await self.get_mock_tracks_data(spotify_id, limit)
    
    async def create_playlist(self, spotify_id: str, request: SpotifyPlaylistRequest) -> SpotifyPlaylist:
        """
        创建播放列表 - 目前返回 Mock 数据
        
        Args:
            spotify_id: Spotify 艺术家 ID
            request: 播放列表创建请求
            
        Returns:
            SpotifyPlaylist: 创建的播放列表信息
            
        Note:
            真实的播放列表创建需要用户授权和更复杂的 OAuth 流程
        """
        logger.info(f"Creating playlist for artist {spotify_id}")
        
        # TODO: 实现真实的播放列表创建逻辑
        # 需要用户授权和更复杂的 OAuth 流程
        # 这里返回 Mock 数据
        
        return SpotifyPlaylist(
            id="mock_playlist_id",
            name=request.playlist_name,
            description=request.description or f"Playlist created for artist {spotify_id}",
            public=request.public,
            tracks={
                "total": 20,
                "items": [
                    {
                        "id": f"track_{i}",
                        "name": f"Mock Track {i}",
                        "duration_ms": 180000 + (i * 10000),
                        "artist": f"Mock Artist {spotify_id[:8]}"
                    }
                    for i in range(1, 21)
                ]
            },
            external_urls={"spotify": "https://open.spotify.com/playlist/mock"}
        )
    
    async def search_artists(self, query: str, limit: int = 10, market: str = "JP") -> List[Dict[str, Any]]:
        """
        搜索艺术家
        
        Args:
            query: 搜索关键词
            limit: 返回数量限制
            market: 市场代码
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        if not settings.is_production or not self.is_available():
            logger.info(f"Using MOCK Spotify search for query: {query}")
            
            # 根据查询关键词返回匹配的Mock数据
            mock_artists = {
                "radiohead": {
                    "id": "4Z8W4fKeB5YxbusRsdQVPb",
                    "name": "Radiohead",
                    "popularity": 82,
                    "genres": ["alternative rock", "art rock", "electronic"]
                },
                "nirvana": {
                    "id": "6olE6TJLqED3rqDCT0FyPh", 
                    "name": "Nirvana",
                    "popularity": 85,
                    "genres": ["grunge", "alternative rock", "rock"]
                },
                "the beatles": {
                    "id": "3WrFJ7ztbogyGnTHbHJFl2",
                    "name": "The Beatles", 
                    "popularity": 88,
                    "genres": ["rock", "pop rock", "psychedelic rock"]
                },
                "coldplay": {
                    "id": "4gzpq5DPGxSnKTe4SA8HAU",
                    "name": "Coldplay",
                    "popularity": 84,
                    "genres": ["alternative rock", "pop rock", "post-britpop"]
                }
            }
            
            # 查找匹配的艺术家
            query_lower = query.lower().strip()
            results = []
            
            # 精确匹配
            if query_lower in mock_artists:
                artist_data = mock_artists[query_lower]
                results.append({
                    "id": artist_data["id"],
                    "name": artist_data["name"],
                    "popularity": artist_data["popularity"],
                    "genres": artist_data["genres"],
                    "external_urls": {"spotify": f"https://open.spotify.com/artist/{artist_data['id']}"}
                })
            else:
                # 模糊匹配
                for artist_name, artist_data in mock_artists.items():
                    if query_lower in artist_name or artist_name in query_lower:
                        results.append({
                            "id": artist_data["id"],
                            "name": artist_data["name"],
                            "popularity": artist_data["popularity"],
                            "genres": artist_data["genres"],
                            "external_urls": {"spotify": f"https://open.spotify.com/artist/{artist_data['id']}"}
                        })
                
                # 如果没有匹配，返回通用Mock数据
                if not results:
                    results.append({
                        "id": f"mock_{query_lower.replace(' ', '_')}",
                        "name": query,
                        "popularity": 75,
                        "genres": ["Rock", "Alternative", "Mock Genre"],
                        "external_urls": {"spotify": f"https://open.spotify.com/artist/mock_{query_lower.replace(' ', '_')}"}
                    })
            
            return results[:limit]
        
        # 真实搜索实现
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/search",
                    headers=headers,
                    params={
                        "q": query,
                        "type": "artist",
                        "limit": limit,
                        "market": market
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    artists = data.get("artists", {}).get("items", [])
                    
                    results = []
                    for artist in artists:
                        results.append({
                            "id": artist.get("id"),
                            "name": artist.get("name"),
                            "popularity": artist.get("popularity", 0),
                            "genres": artist.get("genres", []),
                            "external_urls": artist.get("external_urls", {}),
                            "images": artist.get("images", [])
                        })
                    
                    return results
                else:
                    logger.error(f"Spotify search API error: {response.status_code}")
                    return []
                    
            except Exception as e:
                logger.error(f"Spotify search error: {str(e)}")
                return []
    
    def is_available(self) -> bool:
        """检查 Spotify 服务是否可用"""
        return bool(self.client_id and self.client_secret)
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态信息
        
        Returns:
            Dict: 服务状态信息
        """
        status = {
            "available": self.is_available(),
            "credentials_configured": bool(self.client_id and self.client_secret),
            "has_access_token": bool(self._access_token),
            "environment": settings.ENVIRONMENT,
            "api_url": self.api_url
        }
        
        if self.is_available():
            try:
                # 尝试获取访问令牌来测试连接
                await self._get_access_token()
                status["connection_test"] = "success"
            except Exception as e:
                status["connection_test"] = "failed"
                status["connection_error"] = str(e)
        
        return status

    async def get_artist_by_name(self, artist_name: str) -> Dict[str, Any]:
        """通过艺术家姓名获取其 Spotify 信息"""
        if not self.is_available():
            logger.warning(f"Spotify not available, returning mock data for {artist_name}")
            artist_data = await self.get_mock_artist_data(artist_name)
            return artist_data.model_dump() if artist_data else {}

        # 尝试清理艺术家名字以提高匹配率
        # 例如 "ARTIST (Band Set)" -> "ARTIST"
        # "ARTIST & OTHER" -> "ARTIST"
        cleaned_name = artist_name.split('(')[0].split('&')[0].split('（')[0].strip()

        try:
            # 优先使用清理过的名字搜索
            search_results = await self.search_artists(cleaned_name)
            
            # 如果清理后的名字找不到，尝试使用原名
            if not search_results:
                logger.info(f"Could not find '{cleaned_name}', trying original name '{artist_name}'")
                search_results = await self.search_artists(artist_name)

            if not search_results:
                logger.warning(f"No Spotify search results for '{artist_name}'")
                return {}

            # 假设第一个结果是最佳匹配
            best_match = search_results[0]
            spotify_id = best_match.get("id")

            if not spotify_id:
                logger.warning(f"No Spotify ID found for '{artist_name}'")
                return {}

            # 获取完整的艺术家信息
            artist_info = await self.get_artist_info(spotify_id)
            if not artist_info:
                logger.warning(f"Failed to get detailed artist info for {artist_name}")
                return {}
            
            # ** 关键修复：返回完整的模型数据 **
            return artist_info.model_dump()

        except Exception as e:
            logger.error(f"Error getting artist by name '{artist_name}': {str(e)}")
            return {}
    
    async def get_artist_top_tracks(self, spotify_id: str, limit: int = 10) -> Dict[str, Any]:
        """获取艺术家热门单曲"""
        if not self.is_available():
            logger.warning(f"Spotify not available, returning mock data for {spotify_id}")
            return {}

        try:
            tracks = await self.get_top_tracks(spotify_id, limit)
            
            # 转换为字典格式
            tracks_data = []
            for track in tracks:
                track_data = {
                    "id": track.id,
                    "name": track.name,
                    "duration_ms": track.duration_ms,
                    "popularity": track.popularity,
                    "preview_url": track.preview_url,
                    "external_urls": track.external_urls,
                    "album": {
                        "id": track.album.id if track.album else None,
                        "name": track.album.name if track.album else None,
                        "images": track.album.images if track.album else []
                    }
                }
                tracks_data.append(track_data)
            
            return {
                "success": True,
                "data": {
                    "tracks": tracks_data,
                    "total": len(tracks_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting top tracks for artist {spotify_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get top tracks for artist {spotify_id}"
            }

# 创建全局实例供其他模块使用
spotify_service = SpotifyService() 