"""
Spotify API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Body, status
from typing import List, Dict, Any

from models.spotify import SpotifyResponse, SpotifyPlaylistRequest, SpotifyPlaylistResponse
from services.spotify_service import SpotifyService

router = APIRouter(prefix="/api/spotify", tags=["Spotify"])

# 创建服务实例
spotify_service = SpotifyService()

@router.get(
    "/artists/{spotify_id}",
    response_model=SpotifyResponse,
    summary="获取 Spotify 艺术家信息",
    description="""
    根据 Spotify 艺术家 ID 获取详细信息。
    
    返回信息包括：
    - 艺术家基本信息（姓名、流行度等）
    - 艺术家图片
    - 音乐风格/流派
    - 粉丝数量
    - 外部链接
    """,
    responses={
        200: {
            "description": "成功获取艺术家信息",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "4Z8W4fKeB5YxbusRsdQVPb",
                            "name": "Radiohead",
                            "images": [
                                {
                                    "url": "https://i.scdn.co/image/example",
                                    "height": 640,
                                    "width": 640
                                }
                            ],
                            "genres": ["alternative rock", "art rock"],
                            "popularity": 85,
                            "followers": {"total": 4500000},
                            "external_urls": {
                                "spotify": "https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb"
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "无效的艺术家 ID"},
        404: {"description": "艺术家未找到"},
        401: {"description": "Spotify API 认证失败"},
        503: {"description": "Spotify 服务不可用"}
    }
)
async def get_artist_info(spotify_id: str):
    """
    获取 Spotify 艺术家信息
    
    - **spotify_id**: Spotify 艺术家 ID（URL 路径参数）
    
    返回艺术家的详细信息，包括基本资料、图片、风格和统计数据。
    """
    try:
        artist_data = await spotify_service.get_artist_info(spotify_id)
        return SpotifyResponse(success=True, data=artist_data)
    except HTTPException:
        # 重新抛出已处理的 HTTP 异常
        raise
    except Exception as e:
        # 处理未预期的异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing Spotify artist data",
                "service": "Spotify",
                "artist_id": spotify_id,
                "details": str(e)
            }
        )

@router.get(
    "/artists/{spotify_id}/top-tracks",
    summary="获取艺术家热门曲目",
    description="""
    获取指定艺术家在特定市场的热门曲目列表。
    
    返回信息包括：
    - 曲目基本信息（标题、时长等）
    - 专辑信息
    - 流行度评分
    - 预览链接（如果有）
    """,
    responses={
        200: {
            "description": "成功获取热门曲目",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "artist_id": "4Z8W4fKeB5YxbusRsdQVPb",
                            "tracks": [
                                {
                                    "id": "5u9S6Me0obV508YZtLUtfU",
                                    "name": "Creep",
                                    "album": {
                                        "id": "6400dnyeDyD2mIFHfkwHXN",
                                        "name": "Pablo Honey",
                                        "images": [],
                                        "release_date": "1993-02-22",
                                        "total_tracks": 12
                                    },
                                    "duration_ms": 238640,
                                    "popularity": 85,
                                    "preview_url": "https://p.scdn.co/mp3-preview/example",
                                    "explicit": False
                                }
                            ],
                            "total": 10,
                            "market": "JP"
                        }
                    }
                }
            }
        },
        400: {"description": "无效的请求参数"},
        404: {"description": "艺术家未找到"},
        503: {"description": "Spotify 服务不可用"}
    }
)
async def get_artist_top_tracks(
    spotify_id: str,
    limit: int = Query(
        10, 
        description="返回曲目数量限制",
        ge=1, 
        le=50,
        example=10
    ),
    market: str = Query(
        "JP", 
        description="市场代码（国家/地区），影响曲目可用性和排序",
        pattern="^[A-Z]{2}$",
        example="JP"
    )
):
    """
    获取艺术家热门曲目
    
    - **spotify_id**: Spotify 艺术家 ID（URL 路径参数）
    - **limit**: 返回曲目数量限制，范围 1-50
    - **market**: 市场代码，如 JP（日本）、US（美国）、CN（中国）
    
    返回艺术家在指定市场的热门曲目列表。
    """
    try:
        tracks = await spotify_service.get_top_tracks(spotify_id, limit, market)
        return {
            "success": True,
            "data": {
                "artist_id": spotify_id,
                "tracks": tracks,
                "total": len(tracks),
                "limit": limit,
                "market": market
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing top tracks",
                "service": "Spotify",
                "artist_id": spotify_id,
                "details": str(e)
            }
        )

@router.post(
    "/artists/{spotify_id}/create-playlist",
    response_model=SpotifyPlaylistResponse,
    summary="创建艺术家播放列表",
    description="""
    基于指定艺术家创建播放列表。
    
    注意：当前版本返回模拟数据，真实的播放列表创建需要用户授权。
    
    功能特点：
    - 自定义播放列表名称和描述
    - 设置公开/私有状态
    - 自动添加艺术家热门曲目
    """,
    responses={
        200: {
            "description": "播放列表创建成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "37i9dQZF1DX0XUsuxWHRQd",
                            "name": "My Radiohead Playlist",
                            "description": "Best tracks from Radiohead",
                            "public": True,
                            "tracks": {
                                "total": 20,
                                "items": []
                            },
                            "external_urls": {
                                "spotify": "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数无效"},
        401: {"description": "需要用户授权"},
        404: {"description": "艺术家未找到"}
    }
)
async def create_artist_playlist(
    spotify_id: str,
    request: SpotifyPlaylistRequest = Body(
        ...,
        example={
            "playlist_name": "My Radiohead Playlist",
            "description": "Best tracks from Radiohead",
            "public": True
        }
    )
):
    """
    创建艺术家播放列表
    
    - **spotify_id**: Spotify 艺术家 ID（URL 路径参数）
    
    请求体参数：
    - **playlist_name**: 播放列表名称（必需）
    - **description**: 播放列表描述（可选）
    - **public**: 是否公开播放列表，默认为 true
    
    返回创建的播放列表信息。注意：当前版本返回模拟数据。
    """
    try:
        playlist = await spotify_service.create_playlist(spotify_id, request)
        return SpotifyPlaylistResponse(success=True, data=playlist)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Playlist creation failed",
                "message": "An unexpected error occurred while creating playlist",
                "service": "Spotify",
                "artist_id": spotify_id,
                "details": str(e)
            }
        )

@router.get(
    "/search",
    summary="搜索艺术家",
    description="""
    在 Spotify 中搜索艺术家，返回匹配的结果列表。
    
    支持：
    - 模糊搜索
    - 多市场搜索
    - 结果数量限制
    - 流行度排序
    """,
    responses={
        200: {
            "description": "搜索成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "query": "radiohead",
                            "results": [
                                {
                                    "id": "4Z8W4fKeB5YxbusRsdQVPb",
                                    "name": "Radiohead",
                                    "popularity": 85,
                                    "genres": ["alternative rock", "art rock"],
                                    "external_urls": {
                                        "spotify": "https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb"
                                    },
                                    "images": []
                                }
                            ],
                            "total": 1,
                            "limit": 10,
                            "market": "JP"
                        }
                    }
                }
            }
        },
        400: {"description": "搜索参数无效"},
        500: {"description": "搜索服务错误"}
    }
)
async def search_artists(
    query: str = Query(
        ..., 
        description="搜索关键词，支持艺术家名称或相关词汇",
        min_length=1,
        max_length=100,
        example="radiohead"
    ),
    limit: int = Query(
        10, 
        description="返回结果数量限制",
        ge=1, 
        le=50,
        example=10
    ),
    market: str = Query(
        "JP", 
        description="市场代码，影响搜索结果的可用性",
        pattern="^[A-Z]{2}$",
        example="JP"
    )
):
    """
    搜索艺术家
    
    - **query**: 搜索关键词（必需）
    - **limit**: 返回结果数量限制，范围 1-50
    - **market**: 市场代码，如 JP（日本）、US（美国）
    
    返回匹配的艺术家列表，按流行度排序。
    """
    try:
        results = await spotify_service.search_artists(query, limit, market)
        return {
            "success": True,
            "data": {
                "query": query,
                "results": results,
                "total": len(results),
                "limit": limit,
                "market": market
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Search failed",
                "message": "Failed to search artists in Spotify",
                "service": "Spotify",
                "query": query,
                "details": str(e)
            }
        )

@router.get(
    "/status",
    summary="获取 Spotify 服务状态",
    description="""
    检查 Spotify 服务的可用性和配置状态。
    
    返回服务状态信息，包括：
    - API 凭据配置状态
    - 访问令牌状态
    - 连接测试结果
    - 当前环境信息
    """,
    responses={
        200: {
            "description": "状态检查成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "available": True,
                            "credentials_configured": True,
                            "has_access_token": True,
                            "environment": "development",
                            "api_url": "https://api.spotify.com/v1",
                            "connection_test": "success"
                        }
                    }
                }
            }
        }
    }
)
async def get_spotify_status():
    """
    获取 Spotify 服务状态
    
    返回当前 Spotify 服务的配置和可用性信息。
    """
    try:
        status_info = await spotify_service.get_service_status()
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Status check failed",
                "message": "Failed to get Spotify service status",
                "details": str(e)
            }
        )

@router.get(
    "/artist-by-name/{artist_name}",
    response_model=SpotifyResponse,
    summary="通过艺术家名称获取信息",
    description="""
    通过艺术家名称直接获取艺术家信息，自动处理搜索和ID转换。
    
    工作流程：
    1. 自动搜索艺术家名称
    2. 选择最匹配的结果（通常是流行度最高的）
    3. 返回详细的艺术家信息
    
    返回信息包括：
    - 艺术家基本信息（姓名、流行度等）
    - 艺术家图片
    - 音乐风格/流派
    - 粉丝数量
    - 外部链接
    """,
    responses={
        200: {
            "description": "成功获取艺术家信息",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "6olE6TJLqED3rqDCT0FyPh",
                            "name": "Nirvana",
                            "images": [
                                {
                                    "url": "https://i.scdn.co/image/example",
                                    "height": 640,
                                    "width": 640
                                }
                            ],
                            "genres": ["grunge", "rock"],
                            "popularity": 84,
                            "followers": {"total": 22231568},
                            "external_urls": {
                                "spotify": "https://open.spotify.com/artist/6olE6TJLqED3rqDCT0FyPh"
                            }
                        }
                    }
                }
            }
        },
        404: {"description": "艺术家未找到"},
        400: {"description": "无效的艺术家名称"},
        503: {"description": "Spotify 服务不可用"}
    }
)
async def get_artist_by_name(
    artist_name: str,
    market: str = Query(
        "JP", 
        description="市场代码，影响搜索结果",
        pattern="^[A-Z]{2}$",
        example="JP"
    )
):
    """
    通过艺术家名称获取信息
    
    - **artist_name**: 艺术家名称（URL 路径参数）
    - **market**: 市场代码，如 JP（日本）、US（美国）
    
    自动搜索并返回最匹配的艺术家详细信息。
    """
    try:
        # 1. 先搜索艺术家
        search_results = await spotify_service.search_artists(artist_name, limit=5, market=market)
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Artist not found",
                    "message": f"No artist found with name '{artist_name}'",
                    "service": "Spotify"
                }
            )
        
        # 2. 选择最匹配的结果（通常是第一个，因为按流行度排序）
        best_match = search_results[0]
        spotify_id = best_match["id"]
        
        # 3. 获取详细信息
        artist_data = await spotify_service.get_artist_info(spotify_id)
        
        return SpotifyResponse(success=True, data=artist_data)
        
    except HTTPException:
        # 重新抛出已处理的 HTTP 异常
        raise
    except Exception as e:
        # 处理未预期的异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing artist search",
                "service": "Spotify",
                "artist_name": artist_name,
                "details": str(e)
            }
        )

@router.get(
    "/artist-by-name/{artist_name}/top-tracks",
    summary="通过艺术家名称获取热门曲目",
    description="""
    通过艺术家名称直接获取热门曲目，自动处理搜索和ID转换。
    
    工作流程：
    1. 自动搜索艺术家名称
    2. 选择最匹配的结果
    3. 获取该艺术家的热门曲目
    
    返回信息包括：
    - 曲目基本信息（标题、时长等）
    - 专辑信息
    - 流行度评分
    - 预览链接（如果有）
    """,
    responses={
        200: {
            "description": "成功获取热门曲目",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "artist_name": "Nirvana",
                            "artist_id": "6olE6TJLqED3rqDCT0FyPh",
                            "tracks": [
                                {
                                    "id": "4CeeEOM32jQcH3eN9Q2dGj",
                                    "name": "Smells Like Teen Spirit",
                                    "album": {
                                        "id": "2UJcKiJxNryhL050F5Z1Fk",
                                        "name": "Nevermind (Remastered)",
                                        "images": [],
                                        "release_date": "1991-09-26",
                                        "total_tracks": 13
                                    },
                                    "duration_ms": 301920,
                                    "popularity": 86,
                                    "preview_url": None,
                                    "explicit": False
                                }
                            ],
                            "total": 10,
                            "market": "JP"
                        }
                    }
                }
            }
        },
        404: {"description": "艺术家未找到"},
        400: {"description": "无效的请求参数"},
        503: {"description": "Spotify 服务不可用"}
    }
)
async def get_artist_top_tracks_by_name(
    artist_name: str,
    limit: int = Query(
        10, 
        description="返回曲目数量限制",
        ge=1, 
        le=50,
        example=10
    ),
    market: str = Query(
        "JP", 
        description="市场代码（国家/地区），影响曲目可用性和排序",
        pattern="^[A-Z]{2}$",
        example="JP"
    )
):
    """
    通过艺术家名称获取热门曲目
    
    - **artist_name**: 艺术家名称（URL 路径参数）
    - **limit**: 返回曲目数量限制，范围 1-50
    - **market**: 市场代码，如 JP（日本）、US（美国）
    
    自动搜索艺术家并返回其热门曲目列表。
    """
    try:
        # 1. 先搜索艺术家
        search_results = await spotify_service.search_artists(artist_name, limit=5, market=market)
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Artist not found",
                    "message": f"No artist found with name '{artist_name}'",
                    "service": "Spotify"
                }
            )
        
        # 2. 选择最匹配的结果
        best_match = search_results[0]
        spotify_id = best_match["id"]
        
        # 3. 获取热门曲目
        tracks = await spotify_service.get_top_tracks(spotify_id, limit, market)
        
        return {
            "success": True,
            "data": {
                "artist_name": artist_name,
                "artist_id": spotify_id,
                "tracks": tracks,
                "total": len(tracks),
                "limit": limit,
                "market": market
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing artist tracks search",
                "service": "Spotify",
                "artist_name": artist_name,
                "details": str(e)
            }
        ) 