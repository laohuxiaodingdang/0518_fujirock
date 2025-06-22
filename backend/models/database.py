"""
数据库模型 - 定义所有表的数据结构
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, Field
from uuid import UUID

class ArtistModel(BaseModel):
    """艺术家模型 - 优化后的精简版本"""
    id: Optional[UUID] = None
    name: str = Field(..., description="艺术家名称")
    description: Optional[str] = Field(None, description="简短描述")
    image_url: Optional[str] = Field(None, description="艺术家头像图片URL")
    wiki_data: Optional[Dict[str, Any]] = Field(None, description="Wikipedia原始数据")
    wiki_extract: Optional[str] = Field(None, description="Wikipedia摘要文本")
    wiki_last_updated: Optional[datetime] = Field(None, description="Wikipedia数据最后更新时间")
    spotify_id: Optional[str] = Field(None, description="Spotify艺术家ID")
    genres: Optional[List[str]] = Field(None, description="音乐风格标签数组")
    is_fuji_rock_artist: Optional[bool] = Field(False, description="是否为Fuji Rock艺术家")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SongModel(BaseModel):
    """歌曲模型"""
    id: Optional[UUID] = None
    artist_id: UUID = Field(..., description="关联艺术家ID")
    title: str = Field(..., description="歌曲标题")
    album_name: Optional[str] = Field(None, description="专辑名称")
    duration_seconds: Optional[int] = Field(None, description="歌曲时长(秒)")
    preview_url: Optional[str] = Field(None, description="预览音频URL")
    spotify_id: Optional[str] = Field(None, description="Spotify歌曲ID")
    spotify_data: Optional[Dict[str, Any]] = Field(None, description="Spotify歌曲完整数据")
    itunes_data: Optional[Dict[str, Any]] = Field(None, description="iTunes搜索结果数据")
    release_date: Optional[date] = Field(None, description="发行日期")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AIDescriptionModel(BaseModel):
    """AI描述模型"""
    id: Optional[UUID] = None
    artist_id: UUID = Field(..., description="关联艺术家ID")
    content: str = Field(..., description="AI生成的描述内容")
    language: str = Field("zh", description="语言代码")
    prompt_template: Optional[str] = Field(None, description="使用的提示模板")
    source_content: Optional[str] = Field(None, description="源内容(Wikipedia摘要)")
    tokens_used: Optional[int] = Field(None, description="消耗的token数量")
    generation_time_ms: Optional[int] = Field(None, description="生成耗时")
    created_at: Optional[datetime] = None

class UserFavoriteModel(BaseModel):
    """用户收藏模型"""
    id: Optional[UUID] = None
    user_id: UUID = Field(..., description="关联用户ID")
    artist_id: UUID = Field(..., description="关联艺术家ID")
    tags: Optional[List[str]] = Field(None, description="用户自定义标签")
    notes: Optional[str] = Field(None, description="用户备注")
    created_at: Optional[datetime] = None

class PerformanceModel(BaseModel):
    """演出信息模型"""
    id: Optional[UUID] = None
    artist_id: UUID = Field(..., description="关联艺术家ID")
    stage_name: str = Field(..., description="舞台名称")
    performance_date: date = Field(..., description="演出日期")
    start_time: time = Field(..., description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    duration_minutes: Optional[int] = Field(None, description="演出时长(分钟)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SearchHistoryModel(BaseModel):
    """搜索历史模型"""
    id: Optional[UUID] = None
    user_id: Optional[UUID] = Field(None, description="关联用户ID(可为空)")
    search_query: str = Field(..., description="搜索关键词")
    search_type: str = Field("artist", description="搜索类型")
    results_count: int = Field(0, description="结果数量")
    clicked_result_id: Optional[UUID] = Field(None, description="点击的结果ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    created_at: Optional[datetime] = None

# 请求/响应模型
class CreateArtistRequest(BaseModel):
    """创建艺术家请求模型 - 优化后的精简版本"""
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    genres: Optional[List[str]] = None
    is_fuji_rock_artist: Optional[bool] = False

class UpdateArtistRequest(BaseModel):
    """更新艺术家请求模型 - 优化后的精简版本"""
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    genres: Optional[List[str]] = None
    is_fuji_rock_artist: Optional[bool] = None

class CreateSongRequest(BaseModel):
    """创建歌曲请求模型"""
    artist_id: UUID
    title: str
    album_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    preview_url: Optional[str] = None
    spotify_id: Optional[str] = None
    release_date: Optional[date] = None

class CreateAIDescriptionRequest(BaseModel):
    """创建AI描述请求模型"""
    artist_id: UUID
    content: str
    language: str = "zh"
    prompt_template: Optional[str] = None
    source_content: Optional[str] = None
    tokens_used: Optional[int] = None
    generation_time_ms: Optional[int] = None

class CreateFavoriteRequest(BaseModel):
    """创建收藏请求模型"""
    artist_id: UUID
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    search_type: str = "artist"
    limit: int = 10
    offset: int = 0 