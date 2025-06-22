"""
健康检查和系统状态路由
"""
from fastapi import APIRouter
from datetime import datetime

from config import settings, validate_settings
from models.common import HealthCheckResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    系统健康检查
    """
    api_validation = validate_settings()
    
    return HealthCheckResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        apis={
            "wikipedia": "real" if settings.is_production else "mock",
            "deepseek": "real" if (settings.is_production and api_validation["deepseek"]) else "mock",
            "spotify": "real" if (settings.is_production and api_validation["spotify"]) else "mock"
        },
        timestamp=datetime.now()
    )

@router.get("/status")
async def get_system_status():
    """
    获取详细的系统状态信息
    """
    api_validation = validate_settings()
    
    return {
        "success": True,
        "data": {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "api_keys": api_validation,
            "services": {
                "wikipedia": {
                    "available": True,
                    "base_url": settings.WIKIPEDIA_API_URL
                },
                "deepseek": {
                    "available": api_validation["deepseek"],
                    "configured": bool(settings.ARK_API_KEY)
                },
                "spotify": {
                    "available": api_validation["spotify"],
                    "configured": bool(settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET)
                }
            },
            "timestamp": datetime.now()
        }
    }

@router.get("/")
async def root():
    """
    根路径 - API 信息
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 