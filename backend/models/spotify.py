"""
Spotify API 相关数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class SpotifyImage(BaseModel):
    """Spotify 图片模型"""
    url: str = Field(..., description="图片URL")
    height: int = Field(..., description="图片高度")
    width: int = Field(..., description="图片宽度")

class SpotifyFollowers(BaseModel):
    """Spotify 粉丝信息模型"""
    href: Optional[str] = Field(None, description="链接（总是为null）")
    total: int = Field(..., description="粉丝总数")

class SpotifyArtist(BaseModel):
    """Spotify 艺术家模型"""
    id: str = Field(..., description="Spotify 艺术家 ID")
    name: str = Field(..., description="艺术家名称")
    images: List[SpotifyImage] = Field(default_factory=list, description="艺术家图片")
    genres: List[str] = Field(default_factory=list, description="音乐风格")
    popularity: int = Field(..., ge=0, le=100, description="流行度 (0-100)")
    followers: SpotifyFollowers = Field(..., description="粉丝信息")
    external_urls: Dict[str, str] = Field(default_factory=dict, description="外部链接")

class SpotifyAlbum(BaseModel):
    """Spotify 专辑模型"""
    id: str = Field(..., description="专辑 ID")
    name: str = Field(..., description="专辑名称")
    images: List[SpotifyImage] = Field(default_factory=list, description="专辑封面")
    release_date: str = Field(..., description="发行日期")
    total_tracks: int = Field(..., description="总曲目数")

class SpotifyTrack(BaseModel):
    """Spotify 曲目模型"""
    id: str = Field(..., description="曲目 ID")
    name: str = Field(..., description="曲目名称")
    album: SpotifyAlbum = Field(..., description="所属专辑")
    artists: List[Dict[str, Any]] = Field(default_factory=list, description="艺术家信息")
    duration_ms: int = Field(..., description="时长(毫秒)")
    popularity: int = Field(..., ge=0, le=100, description="流行度")
    preview_url: Optional[str] = Field(None, description="预览音频URL")
    explicit: bool = Field(False, description="是否包含不当内容")
    external_urls: Dict[str, str] = Field(default_factory=dict, description="外部链接")

class SpotifyPlaylist(BaseModel):
    """Spotify 播放列表模型"""
    id: str = Field(..., description="播放列表 ID")
    name: str = Field(..., description="播放列表名称")
    description: str = Field(..., description="播放列表描述")
    public: bool = Field(False, description="是否公开")
    tracks: Dict[str, Any] = Field(..., description="曲目信息")
    external_urls: Dict[str, str] = Field(..., description="外部链接")

class SpotifyArtistRequest(BaseModel):
    """Spotify 艺术家请求模型"""
    spotify_id: str = Field(..., description="Spotify 艺术家 ID", min_length=1)

class SpotifyTopTracksRequest(BaseModel):
    """Spotify 热门曲目请求模型"""
    spotify_id: str = Field(..., description="Spotify 艺术家 ID")
    limit: int = Field(10, ge=1, le=50, description="返回数量限制")
    market: str = Field("JP", description="市场代码")

class SpotifyPlaylistRequest(BaseModel):
    """Spotify 播放列表创建请求模型"""
    playlist_name: str = Field(..., description="播放列表名称", min_length=1)
    description: str = Field("", description="播放列表描述")
    public: bool = Field(False, description="是否公开")

# 通用响应模型
class SpotifyResponse(BaseModel):
    """Spotify 通用响应模型"""
    success: bool = True
    data: Union[SpotifyArtist, Dict[str, Any]]

# 特定响应模型（保持向后兼容）
class SpotifyArtistResponse(BaseModel):
    """Spotify 艺术家响应模型"""
    success: bool = True
    data: SpotifyArtist

class SpotifyTopTracksResponse(BaseModel):
    """Spotify 热门曲目响应模型"""
    success: bool = True
    data: Dict[str, List[SpotifyTrack]]

class SpotifyPlaylistResponse(BaseModel):
    """Spotify 播放列表响应模型"""
    success: bool = True
    data: SpotifyPlaylist 