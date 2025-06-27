"""
数据库 API 路由 - 提供数据库相关的 RESTful API 接口
"""
import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Path, Body, Request
from fastapi.responses import JSONResponse

from services.artist_db_service import artist_db_service
from services.song_db_service import song_db_service
from services.ai_description_db_service import ai_description_db_service
from services.user_db_service import user_db_service
from models.database import (
    CreateArtistRequest, UpdateArtistRequest, CreateSongRequest, 
    CreateAIDescriptionRequest, CreateFavoriteRequest, SearchRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/database", tags=["Database"])

# ==================== 艺术家相关接口 ====================

@router.post("/artists")
async def create_artist(artist_data: CreateArtistRequest):
    """
    创建新艺术家
    
    **功能说明：**
    - 创建新的艺术家记录
    - 自动检查重名艺术家
    - 支持多语言名称
    
    **使用场景：**
    - 从外部API获取艺术家信息后存储到数据库
    - 手动添加新的艺术家
    """
    try:
        result = await artist_db_service.create_artist(artist_data)
        if result["success"]:
            return JSONResponse(content=result, status_code=201)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in create_artist API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/{artist_id}")
async def get_artist(artist_id: UUID = Path(..., description="艺术家UUID")):
    """
    根据ID获取艺术家信息
    
    **功能说明：**
    - 获取艺术家的完整信息
    - 包含Wikipedia、Spotify等平台数据
    """
    try:
        result = await artist_db_service.get_artist_by_id(artist_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_artist API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


    
@router.get("/artists/by-name/{artist_name}")
async def get_artist_by_name(artist_name: str = Path(..., description="艺术家名称")):
    """根据名称获取艺术家信息（支持模糊匹配）"""
    try:
        # 使用模糊匹配方法
        result = await artist_db_service.get_artist_by_name_fuzzy(artist_name)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_artist_by_name API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/artists/by-spotify/{spotify_id}")
async def get_artist_by_spotify_id(spotify_id: str = Path(..., description="Spotify艺术家ID")):
    """
    根据Spotify ID获取艺术家信息
    """
    try:
        result = await artist_db_service.get_artist_by_spotify_id(spotify_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_artist_by_spotify_id API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/artists/{artist_id}")
async def update_artist(
    artist_id: UUID = Path(..., description="艺术家UUID"),
    update_data: UpdateArtistRequest = Body(...)
):
    """
    更新艺术家信息
    
    **功能说明：**
    - 部分更新艺术家信息
    - 只更新提供的字段
    """
    try:
        result = await artist_db_service.update_artist(artist_id, update_data)
        if result["success"]:
            return result
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in update_artist API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/artists/{artist_id}/wikipedia")
async def update_artist_wikipedia_data(
    artist_id: UUID = Path(..., description="艺术家UUID"),
    wiki_data: dict = Body(..., description="Wikipedia原始数据"),
    wiki_extract: str = Body(..., description="Wikipedia摘要文本")
):
    """
    更新艺术家的Wikipedia数据
    
    **功能说明：**
    - 专门用于更新Wikipedia相关数据
    - 自动更新最后更新时间
    
    **使用场景：**
    - Wikipedia API获取数据后存储
    - 定期刷新Wikipedia内容
    """
    try:
        result = await artist_db_service.update_artist_wikipedia_data(artist_id, wiki_data, wiki_extract)
        if result["success"]:
            return result
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in update_artist_wikipedia_data API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/artists/{artist_id}/spotify")
async def update_artist_spotify_data(
    artist_id: UUID = Path(..., description="艺术家UUID"),
    spotify_data: dict = Body(..., description="Spotify艺术家数据"),
    spotify_id: Optional[str] = Body(None, description="Spotify艺术家ID")
):
    """
    更新艺术家的Spotify数据
    
    **功能说明：**
    - 专门用于更新Spotify相关数据
    - 自动提取热度、粉丝数等信息
    
    **使用场景：**
    - Spotify API获取数据后存储
    - 定期刷新Spotify数据
    """
    try:
        result = await artist_db_service.update_artist_spotify_data(artist_id, spotify_data, spotify_id)
        if result["success"]:
            return result
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in update_artist_spotify_data API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists")
async def search_artists(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    搜索艺术家
    
    **功能说明：**
    - 支持多语言模糊搜索
    - 按热度排序返回结果
    """
    try:
        result = await artist_db_service.search_artists(query, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in search_artists API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/fuji-rock")
async def get_fuji_rock_artists(
    limit: int = Query(50, description="返回结果数量限制", ge=1, le=100),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取Fuji Rock艺术家列表
    """
    try:
        result = await artist_db_service.get_fuji_rock_artists(limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_fuji_rock_artists API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/popular")
async def get_popular_artists(
    limit: int = Query(20, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取热门艺术家列表
    """
    try:
        result = await artist_db_service.get_popular_artists(limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_popular_artists API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/artists/{artist_id}")
async def delete_artist(artist_id: UUID = Path(..., description="艺术家UUID")):
    """
    删除艺术家
    
    **注意：**
    - 会级联删除相关的歌曲、AI描述等数据
    - 谨慎使用此接口
    """
    try:
        result = await artist_db_service.delete_artist(artist_id)
        if result["success"]:
            return result
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in delete_artist API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 歌曲相关接口 ====================

@router.post("/songs")
async def create_song(song_data: CreateSongRequest):
    """
    创建新歌曲
    
    **功能说明：**
    - 创建新的歌曲记录
    - 自动检查同一艺术家的重名歌曲
    """
    try:
        result = await song_db_service.create_song(song_data)
        if result["success"]:
            return JSONResponse(content=result, status_code=201)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in create_song API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/songs/batch")
async def batch_create_songs(songs_data: List[CreateSongRequest]):
    """
    批量创建歌曲
    
    **功能说明：**
    - 批量插入多首歌曲
    - 适用于从Spotify API获取艺术家热门歌曲后批量存储
    """
    try:
        result = await song_db_service.batch_create_songs(songs_data)
        if result["success"]:
            return JSONResponse(content=result, status_code=201)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in batch_create_songs API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs/{song_id}")
async def get_song(song_id: UUID = Path(..., description="歌曲UUID")):
    """
    根据ID获取歌曲信息
    """
    try:
        result = await song_db_service.get_song_by_id(song_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_song API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/{artist_id}/songs")
async def get_artist_songs(
    artist_id: UUID = Path(..., description="艺术家UUID"),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取艺术家的歌曲列表
    """
    try:
        result = await song_db_service.get_songs_by_artist(artist_id, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_artist_songs API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs")
async def search_songs(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    搜索歌曲
    
    **功能说明：**
    - 支持歌曲标题和专辑名称搜索
    - 返回结果包含艺术家信息
    """
    try:
        result = await song_db_service.search_songs(query, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in search_songs API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs/with-preview")
async def get_songs_with_preview(
    limit: int = Query(20, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取有预览URL的歌曲列表
    
    **功能说明：**
    - 只返回有音频预览的歌曲
    - 适用于音乐播放功能
    """
    try:
        result = await song_db_service.get_songs_with_preview(limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_songs_with_preview API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI描述相关接口 ====================

@router.post("/ai-descriptions")
async def create_ai_description(description_data: CreateAIDescriptionRequest):
    """
    创建AI描述
    
    **功能说明：**
    - 存储AI生成的艺术家描述
    - 记录生成参数和统计信息
    
    **使用场景：**
    - AI API生成描述后存储到数据库
    """
    try:
        result = await ai_description_db_service.create_ai_description(description_data)
        if result["success"]:
            return JSONResponse(content=result, status_code=201)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in create_ai_description API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/{artist_id}/ai-descriptions")
async def get_artist_ai_descriptions(
    artist_id: UUID = Path(..., description="艺术家UUID"),
    language: Optional[str] = Query(None, description="语言过滤"),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取艺术家的AI描述列表
    """
    try:
        result = await ai_description_db_service.get_ai_descriptions_by_artist(artist_id, language, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_artist_ai_descriptions API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/{artist_id}/ai-descriptions/latest")
async def get_latest_ai_description(
    artist_id: UUID = Path(..., description="艺术家UUID"),
    language: str = Query("zh", description="语言代码")
):
    """
    获取艺术家最新的AI描述
    
    **功能说明：**
    - 获取指定语言的最新AI描述
    - 适用于前端显示艺术家介绍
    """
    try:
        result = await ai_description_db_service.get_latest_ai_description(artist_id, language)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_latest_ai_description API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-descriptions/stats")
async def get_ai_descriptions_stats(
    artist_id: Optional[UUID] = Query(None, description="艺术家UUID（可选）")
):
    """
    获取AI描述统计信息
    
    **功能说明：**
    - 统计AI描述的使用情况
    - 包含token消耗、生成时间等信息
    """
    try:
        result = await ai_description_db_service.get_ai_descriptions_stats(artist_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_ai_descriptions_stats API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 用户收藏相关接口 ====================

@router.post("/users/{user_id}/favorites")
async def add_favorite(
    user_id: UUID = Path(..., description="用户UUID"),
    favorite_data: CreateFavoriteRequest = Body(...)
):
    """
    添加用户收藏
    
    **功能说明：**
    - 将艺术家添加到用户收藏列表
    - 支持添加标签和备注
    """
    try:
        result = await user_db_service.add_favorite(user_id, favorite_data)
        if result["success"]:
            return JSONResponse(content=result, status_code=201)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in add_favorite API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}/favorites/{artist_id}")
async def remove_favorite(
    user_id: UUID = Path(..., description="用户UUID"),
    artist_id: UUID = Path(..., description="艺术家UUID")
):
    """
    移除用户收藏
    """
    try:
        result = await user_db_service.remove_favorite(user_id, artist_id)
        if result["success"]:
            return result
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in remove_favorite API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/favorites")
async def get_user_favorites(
    user_id: UUID = Path(..., description="用户UUID"),
    limit: int = Query(20, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取用户收藏列表
    
    **功能说明：**
    - 获取用户的所有收藏艺术家
    - 包含艺术家基本信息
    """
    try:
        result = await user_db_service.get_user_favorites(user_id, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_user_favorites API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/favorites/by-tag/{tag}")
async def get_favorites_by_tag(
    user_id: UUID = Path(..., description="用户UUID"),
    tag: str = Path(..., description="标签名称"),
    limit: int = Query(20, description="返回结果数量限制", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    根据标签获取用户收藏
    """
    try:
        result = await user_db_service.get_favorites_by_tag(user_id, tag, limit, offset)
        return result
    except Exception as e:
        logger.error(f"Error in get_favorites_by_tag API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 搜索历史相关接口 ====================

@router.post("/search-history")
async def record_search(
    request: Request,
    search_query: str = Body(..., description="搜索关键词"),
    search_type: str = Body("artist", description="搜索类型"),
    user_id: Optional[UUID] = Body(None, description="用户UUID"),
    results_count: int = Body(0, description="结果数量")
):
    """
    记录搜索历史
    
    **功能说明：**
    - 记录用户搜索行为
    - 用于分析和优化搜索体验
    """
    try:
        # 从请求中提取额外信息
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = await user_db_service.record_search(
            search_query, search_type, user_id, results_count, 
            None, ip_address, user_agent
        )
        if result["success"]:
            return JSONResponse(content=result, status_code=201)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        logger.error(f"Error in record_search API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-history/popular")
async def get_popular_searches(
    search_type: Optional[str] = Query(None, description="搜索类型过滤"),
    days: int = Query(7, description="统计最近多少天的数据", ge=1, le=30),
    limit: int = Query(10, description="返回结果数量限制", ge=1, le=50)
):
    """
    获取热门搜索关键词
    
    **功能说明：**
    - 统计热门搜索词
    - 用于搜索建议和热门推荐
    """
    try:
        result = await user_db_service.get_popular_searches(search_type, days, limit)
        return result
    except Exception as e:
        logger.error(f"Error in get_popular_searches API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: UUID = Path(..., description="用户UUID")):
    """
    获取用户统计信息
    
    **功能说明：**
    - 获取用户的收藏数量、搜索次数等统计信息
    - 用于用户个人中心展示
    """
    try:
        result = await user_db_service.get_user_stats(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in get_user_stats API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 