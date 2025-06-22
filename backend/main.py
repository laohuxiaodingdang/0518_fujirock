"""
Fuji Rock 2025 API - 重构后的主应用文件
"""
import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings, validate_settings

# 导入路由
from api.wikipedia import router as wikipedia_router
from api.openai import router as openai_router
from api.spotify import router as spotify_router
from api.health import router as health_router
from api.database import router as database_router
from api.integration_example import router as integration_router
from api.auth import router as auth_router
from api.protected import router as protected_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化操作
    validate_settings()
    yield
    # 关闭时的清理操作
    pass

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册路由
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(wikipedia_router)
app.include_router(openai_router)
app.include_router(spotify_router)
app.include_router(database_router)
app.include_router(integration_router)
app.include_router(protected_router)

# iTunes API 路由
@app.get("/api/itunes/search-track")
async def search_itunes_track(
    artist: str = Query(..., description="艺术家名称"),
    track: str = Query(..., description="歌曲名称"),
    limit: int = Query(5, description="返回结果数量限制")
):
    """
    在iTunes中搜索歌曲，获取预览URL
    """
    try:
        from services.itunes_service import itunes_service
        result = await itunes_service.search_track(artist, track, limit)
        return result
    except Exception as e:
        logger.error(f"iTunes search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"iTunes search failed: {str(e)}")

@app.get("/api/itunes/artist-tracks")
async def get_itunes_artist_tracks(
    artist: str = Query(..., description="艺术家名称"),
    limit: int = Query(10, description="返回结果数量限制")
):
    """
    获取艺术家在iTunes中的歌曲列表
    """
    try:
        from services.itunes_service import itunes_service
        result = await itunes_service.get_artist_top_tracks(artist, limit)
        return result
    except Exception as e:
        logger.error(f"iTunes artist tracks error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"iTunes artist tracks failed: {str(e)}")

@app.get("/api/spotify/track-with-itunes-preview")
async def get_track_with_itunes_preview(
    artist: str = Query(..., description="艺术家名称"),
    track: str = Query(..., description="歌曲名称")
):
    """
    获取Spotify歌曲信息，并尝试从iTunes获取预览URL
    """
    try:
        from services.itunes_service import itunes_service
        
        # 尝试从iTunes获取预览
        itunes_result = await itunes_service.search_track(artist, track)
        
        response = {
            "spotify_preview_available": False,
            "itunes_preview_available": False,
            "preview_url": None,
            "preview_source": None,
            "track_info": {
                "artist": artist,
                "track": track
            }
        }
        
        if itunes_result and itunes_result.get("success"):
            itunes_data = itunes_result["data"]
            if itunes_data.get("preview_url"):
                response.update({
                    "itunes_preview_available": True,
                    "preview_url": itunes_data["preview_url"],
                    "preview_source": "iTunes",
                    "itunes_info": itunes_data
                })
        
        return response
        
    except Exception as e:
        logger.error(f"Track with iTunes preview error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get track with preview: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # 使用字符串导入以支持 reload
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 