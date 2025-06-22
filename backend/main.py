"""
Fuji Rock 2025 API - 重构后的主应用文件
"""
import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

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
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    
    # 验证配置
    validation_result = validate_settings()
    
    if settings.is_production:
        logger.info("🔒 Production mode - Enhanced security enabled")
    else:
        logger.info("🛠️ Development mode - Relaxed CORS settings")
    
    yield
    
    # 关闭时的清理操作
    logger.info("🔄 Shutting down application...")

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# # 添加可信主机中间件（生产环境安全措施）
# if settings.is_production:
#     app.add_middleware(
#         TrustedHostMiddleware, 
#         allowed_hosts=["toxicfjr.xyz", "www.toxicfjr.xyz", "api.toxicfjr.xyz"]
#     )

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    
    if settings.is_production:
        # 生产环境不暴露详细错误信息
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    else:
        # 开发环境返回详细错误信息
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )

# 注册路由 - 使用统一的 /api/v1 前缀
API_V1_PREFIX = ""

app.include_router(health_router)  # 健康检查不需要版本前缀
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(wikipedia_router, prefix=API_V1_PREFIX)  
app.include_router(openai_router, prefix=API_V1_PREFIX)
app.include_router(spotify_router, prefix=API_V1_PREFIX)
app.include_router(database_router, prefix=API_V1_PREFIX)
app.include_router(integration_router, prefix=API_V1_PREFIX)
app.include_router(protected_router, prefix=API_V1_PREFIX)

# iTunes API 路由 - 移到统一前缀下
@app.get(f"{API_V1_PREFIX}/itunes/search-track")
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

@app.get(f"{API_V1_PREFIX}/itunes/artist-tracks")
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

@app.get(f"{API_V1_PREFIX}/spotify/track-with-itunes-preview")
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

# 根路径重定向到健康检查
@app.get("/")
async def root():
    """根路径 - 返回 API 信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "docs_url": "/docs" if not settings.is_production else "disabled",
        "health_check": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # 使用字符串导入以支持 reload
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.is_development  # 生产环境可关闭访问日志以提升性能
    ) 