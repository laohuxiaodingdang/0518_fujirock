"""
Wikipedia API 路由
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List, Dict, Any

from models.wikipedia import WikipediaResponse
from services.wikipedia_service import WikipediaService

router = APIRouter(prefix="/api/wikipedia", tags=["Wikipedia"])

# 创建服务实例
wikipedia_service = WikipediaService()

@router.get(
    "/artists/{artist_name}", 
    response_model=WikipediaResponse,
    summary="获取艺术家的 Wikipedia 信息",
    description="""
    根据艺术家名称获取其 Wikipedia 页面信息，包括：
    - 页面标题和摘要
    - 缩略图（如果有）
    - 分类信息
    - 参考资料链接
    
    支持多种语言版本的 Wikipedia。
    """,
    responses={
        200: {
            "description": "成功获取艺术家信息",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "title": "Radiohead",
                            "extract": "Radiohead are an English rock band...",
                            "thumbnail": {
                                "source": "https://example.com/image.jpg",
                                "width": 800,
                                "height": 600
                            },
                            "categories": ["Rock", "Alternative"],
                            "references": [
                                {
                                    "title": "Official Website",
                                    "url": "https://radiohead.com"
                                }
                            ]
                        }
                    }
                }
            }
        },
        404: {
            "description": "艺术家未找到",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "Artist not found",
                            "message": "Wikipedia page for 'Unknown Artist' not found in zh",
                            "suggestion": "Try searching with a different name or language"
                        }
                    }
                }
            }
        },
        408: {"description": "请求超时"},
        503: {"description": "Wikipedia 服务不可用"}
    }
)
async def get_artist_wiki_info(
    artist_name: str,
    language: str = Query(
        "zh", 
        description="语言代码，支持的语言：zh(中文), en(英文), ja(日文), ko(韩文)",
        pattern="^(zh|en|ja|ko)$",
        example="zh"
    )
):
    """
    获取艺术家的 Wikipedia 信息
    
    - **artist_name**: 艺术家名称（URL 路径参数）
    - **language**: 语言代码，默认为中文 (zh)
    
    返回艺术家的详细 Wikipedia 信息，包括简介、图片和相关链接。
    """
    try:
        wiki_data = await wikipedia_service.get_artist_info(artist_name, language)
        return WikipediaResponse(success=True, data=wiki_data)
    except HTTPException:
        # 重新抛出已处理的 HTTP 异常
        raise
    except Exception as e:
        # 处理未预期的异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing the request",
                "service": "Wikipedia",
                "details": str(e)
            }
        )

@router.get(
    "/search",
    summary="搜索艺术家",
    description="""
    在 Wikipedia 中搜索艺术家，返回匹配的结果列表。
    
    支持模糊搜索和多语言搜索。
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
                                    "title": "Radiohead",
                                    "description": "English rock band formed in Abingdon...",
                                    "url": "https://zh.wikipedia.org/wiki/Radiohead"
                                }
                            ],
                            "total": 1
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
    language: str = Query(
        "zh", 
        description="搜索语言代码",
        pattern="^(zh|en|ja|ko)$",
        example="zh"
    ),
    limit: int = Query(
        10, 
        description="返回结果数量限制",
        ge=1, 
        le=50,
        example=10
    )
):
    """
    搜索艺术家
    
    - **query**: 搜索关键词（必需）
    - **language**: 搜索语言代码，默认为中文
    - **limit**: 返回结果数量限制，范围 1-50
    
    返回匹配的艺术家列表，包括标题、描述和链接。
    """
    try:
        results = await wikipedia_service.search_artists(query, language, limit)
        return {
            "success": True,
            "data": {
                "query": query,
                "results": results,
                "total": len(results),
                "language": language,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Search failed",
                "message": "Failed to search artists in Wikipedia",
                "service": "Wikipedia",
                "query": query,
                "details": str(e)
            }
        ) 