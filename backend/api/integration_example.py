"""
集成示例 - 展示如何在现有API中集成数据库操作
"""
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

# 导入现有服务
from services.wikipedia_service import wikipedia_service
from services.spotify_service import spotify_service
from services.openai_service import openai_service

# 导入数据库服务
from services.artist_db_service import artist_db_service
from services.song_db_service import song_db_service
from services.ai_description_db_service import ai_description_db_service
from services.user_db_service import user_db_service

# 导入数据模型
from models.database import CreateArtistRequest, CreateSongRequest, CreateAIDescriptionRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/integration", tags=["Integration Examples"])

@router.post("/artists/{artist_name}/complete-setup")
async def complete_artist_setup(
    artist_name: str = Path(..., description="艺术家名称"),
    language: str = Query("zh", description="语言代码"),
    save_to_db: bool = Query(True, description="是否保存到数据库")
):
    """
    完整的艺术家设置流程示例
    
    **功能说明：**
    - 从Wikipedia获取艺术家信息
    - 从Spotify获取艺术家和歌曲数据
    - 生成AI描述
    - 将所有数据保存到数据库
    
    **这是一个完整的集成示例，展示了如何组合使用所有服务**
    """
    try:
        result = {
            "artist_name": artist_name,
            "steps_completed": [],
            "data": {},
            "database_operations": []
        }
        
        # 步骤1: 检查数据库中是否已存在该艺术家
        if save_to_db:
            existing_artist = await artist_db_service.get_artist_by_name(artist_name)
            if existing_artist.get("success"):
                result["data"]["existing_artist"] = existing_artist["data"]
                result["steps_completed"].append("found_existing_artist")
                return JSONResponse(content={
                    "success": True,
                    "message": "Artist already exists in database",
                    "result": result
                }, status_code=200)
        
        # 步骤2: 从Wikipedia获取艺术家信息
        try:
            wiki_result = await wikipedia_service.get_artist_info(artist_name, language)
            if wiki_result.get("success"):
                result["data"]["wikipedia"] = wiki_result["data"]
                result["steps_completed"].append("wikipedia_fetched")
                logger.info(f"Wikipedia data fetched for {artist_name}")
            else:
                result["data"]["wikipedia_error"] = wiki_result.get("error", "Unknown error")
        except Exception as e:
            logger.error(f"Wikipedia fetch failed: {str(e)}")
            result["data"]["wikipedia_error"] = str(e)
        
        # 步骤3: 从Spotify获取艺术家信息
        try:
            spotify_artist_result = await spotify_service.get_artist_by_name(artist_name)
            if spotify_artist_result.get("success"):
                result["data"]["spotify_artist"] = spotify_artist_result["data"]
                result["steps_completed"].append("spotify_artist_fetched")
                
                # 获取艺术家热门歌曲
                spotify_id = spotify_artist_result["data"].get("id")
                if spotify_id:
                    tracks_result = await spotify_service.get_artist_top_tracks(spotify_id)
                    if tracks_result.get("success"):
                        result["data"]["spotify_tracks"] = tracks_result["data"]
                        result["steps_completed"].append("spotify_tracks_fetched")
                        logger.info(f"Spotify data fetched for {artist_name}")
            else:
                result["data"]["spotify_error"] = spotify_artist_result.get("error", "Unknown error")
        except Exception as e:
            logger.error(f"Spotify fetch failed: {str(e)}")
            result["data"]["spotify_error"] = str(e)
        
        # 步骤4: 生成AI描述
        try:
            if result["data"].get("wikipedia"):
                wiki_extract = result["data"]["wikipedia"].get("extract", "")
                ai_result = await openai_service.generate_sassy_description(
                    artist_name=artist_name,
                    wiki_content=wiki_extract,
                    style_intensity=8,
                    language=language
                )
                if ai_result.get("success"):
                    result["data"]["ai_description"] = ai_result["data"]
                    result["steps_completed"].append("ai_description_generated")
                    logger.info(f"AI description generated for {artist_name}")
                else:
                    result["data"]["ai_error"] = ai_result.get("error", "Unknown error")
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            result["data"]["ai_error"] = str(e)
        
        # 步骤5: 保存到数据库
        if save_to_db:
            try:
                # 5.1 创建艺术家记录
                artist_data = CreateArtistRequest(
                    name=artist_name,
                    description=result["data"].get("wikipedia", {}).get("extract", "")[:500] if result["data"].get("wikipedia") else None,
                    genres=result["data"].get("spotify_artist", {}).get("genres", []) if result["data"].get("spotify_artist") else None
                )
                
                artist_create_result = await artist_db_service.create_artist(artist_data)
                if artist_create_result.get("success"):
                    artist_id = UUID(artist_create_result["data"]["id"])
                    result["database_operations"].append("artist_created")
                    
                    # 5.2 更新Wikipedia数据
                    if result["data"].get("wikipedia"):
                        wiki_update_result = await artist_db_service.update_artist_wikipedia_data(
                            artist_id,
                            result["data"]["wikipedia"],
                            result["data"]["wikipedia"].get("extract", "")
                        )
                        if wiki_update_result.get("success"):
                            result["database_operations"].append("wikipedia_data_updated")
                    
                    # 5.3 更新Spotify数据
                    if result["data"].get("spotify_artist"):
                        spotify_update_result = await artist_db_service.update_artist_spotify_data(
                            artist_id,
                            result["data"]["spotify_artist"],
                            result["data"]["spotify_artist"].get("id")
                        )
                        if spotify_update_result.get("success"):
                            result["database_operations"].append("spotify_data_updated")
                    
                    # 5.4 保存AI描述
                    if result["data"].get("ai_description"):
                        ai_desc_data = CreateAIDescriptionRequest(
                            artist_id=artist_id,
                            content=result["data"]["ai_description"]["sassy_description"],
                            language=language,
                            source_content=result["data"].get("wikipedia", {}).get("extract", ""),
                            tokens_used=result["data"]["ai_description"].get("tokens_used"),
                            generation_time_ms=result["data"]["ai_description"].get("generation_time_ms")
                        )
                        
                        ai_create_result = await ai_description_db_service.create_ai_description(ai_desc_data)
                        if ai_create_result.get("success"):
                            result["database_operations"].append("ai_description_saved")
                    
                    # 5.5 批量保存歌曲
                    if result["data"].get("spotify_tracks"):
                        songs_data = []
                        for track in result["data"]["spotify_tracks"]["tracks"][:10]:  # 限制前10首
                            song_data = CreateSongRequest(
                                artist_id=artist_id,
                                title=track["name"],
                                album_name=track.get("album", {}).get("name"),
                                duration_seconds=track.get("duration_ms", 0) // 1000,
                                preview_url=track.get("preview_url"),
                                spotify_id=track.get("id")
                            )
                            songs_data.append(song_data)
                        
                        if songs_data:
                            songs_create_result = await song_db_service.batch_create_songs(songs_data)
                            if songs_create_result.get("success"):
                                result["database_operations"].append(f"songs_saved_{len(songs_data)}")
                    
                    result["data"]["artist_id"] = str(artist_id)
                    result["steps_completed"].append("database_saved")
                    
                else:
                    result["database_operations"].append(f"artist_creation_failed: {artist_create_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Database operations failed: {str(e)}")
                result["database_operations"].append(f"database_error: {str(e)}")
        
        # 返回完整结果
        success_count = len(result["steps_completed"])
        total_steps = 5 if save_to_db else 4
        
        return JSONResponse(content={
            "success": True,
            "message": f"Artist setup completed: {success_count}/{total_steps} steps successful",
            "result": result
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"Complete artist setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/{artist_name}/enhanced-info")
async def get_enhanced_artist_info(
    artist_name: str = Path(..., description="艺术家名称"),
    language: str = Query("zh", description="语言代码"),
    include_songs: bool = Query(True, description="是否包含歌曲信息"),
    include_ai_description: bool = Query(True, description="是否包含AI描述")
):
    """
    获取增强的艺术家信息
    
    **功能说明：**
    - 优先从数据库获取信息
    - 如果数据库中没有，则从外部API获取
    - 组合多个数据源的信息
    """
    try:
        result = {
            "artist_name": artist_name,
            "data_sources": [],
            "data": {}
        }
        
        # 1. 尝试从数据库获取艺术家信息
        db_artist = await artist_db_service.get_artist_by_name(artist_name)
        if db_artist.get("success"):
            result["data"]["artist"] = db_artist["data"]
            result["data_sources"].append("database")
            
            artist_id = UUID(db_artist["data"]["id"])
            
            # 获取歌曲信息
            if include_songs:
                songs_result = await song_db_service.get_songs_by_artist(artist_id, limit=10)
                if songs_result.get("success"):
                    result["data"]["songs"] = songs_result["data"]
            
            # 获取AI描述
            if include_ai_description:
                ai_desc_result = await ai_description_db_service.get_latest_ai_description(artist_id, language)
                if ai_desc_result.get("success"):
                    result["data"]["ai_description"] = ai_desc_result["data"]
        
        else:
            # 2. 数据库中没有，从外部API获取
            # Wikipedia信息
            try:
                wiki_result = await wikipedia_service.get_artist_info(artist_name, language)
                if wiki_result.get("success"):
                    result["data"]["wikipedia"] = wiki_result["data"]
                    result["data_sources"].append("wikipedia")
            except Exception as e:
                logger.error(f"Wikipedia API error: {str(e)}")
            
            # Spotify信息
            try:
                spotify_result = await spotify_service.get_artist_by_name(artist_name)
                if spotify_result.get("success"):
                    result["data"]["spotify"] = spotify_result["data"]
                    result["data_sources"].append("spotify")
                    
                    # 获取热门歌曲
                    if include_songs:
                        spotify_id = spotify_result["data"].get("id")
                        if spotify_id:
                            tracks_result = await spotify_service.get_artist_top_tracks(spotify_id)
                            if tracks_result.get("success"):
                                result["data"]["spotify_tracks"] = tracks_result["data"]
            except Exception as e:
                logger.error(f"Spotify API error: {str(e)}")
        
        return JSONResponse(content={
            "success": True,
            "result": result
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"Enhanced artist info failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/search-and-favorite")
async def search_and_favorite(
    user_id: UUID = Path(..., description="用户UUID"),
    search_query: str = Query(..., description="搜索关键词"),
    auto_favorite: bool = Query(False, description="是否自动收藏第一个结果")
):
    """
    搜索并收藏示例
    
    **功能说明：**
    - 搜索艺术家
    - 记录搜索历史
    - 可选择自动收藏第一个结果
    """
    try:
        # 1. 搜索艺术家
        search_result = await artist_db_service.search_artists(search_query, limit=5)
        
        # 2. 记录搜索历史
        search_record_result = await user_db_service.record_search(
            search_query=search_query,
            search_type="artist",
            user_id=user_id,
            results_count=len(search_result.get("data", []))
        )
        
        result = {
            "search_query": search_query,
            "search_results": search_result,
            "search_recorded": search_record_result.get("success", False)
        }
        
        # 3. 自动收藏第一个结果
        if auto_favorite and search_result.get("success") and search_result.get("data"):
            first_artist = search_result["data"][0]
            artist_id = UUID(first_artist["id"])
            
            from models.database import CreateFavoriteRequest
            favorite_data = CreateFavoriteRequest(
                artist_id=artist_id,
                tags=["auto_favorite", "search_result"],
                notes=f"Auto-favorited from search: {search_query}"
            )
            
            favorite_result = await user_db_service.add_favorite(user_id, favorite_data)
            result["favorite_added"] = favorite_result.get("success", False)
            if favorite_result.get("success"):
                result["favorite_data"] = favorite_result["data"]
        
        return JSONResponse(content={
            "success": True,
            "result": result
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"Search and favorite failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 