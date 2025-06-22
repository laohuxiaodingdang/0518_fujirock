"""
需要认证的API示例 - 演示如何在API中使用JWT认证
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from api.auth import get_current_user, get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/protected", tags=["Protected APIs"])

@router.get("/user-favorites")
async def get_user_favorites(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    获取用户收藏的艺术家列表（需要登录）
    
    **功能说明：**
    - 只有登录用户才能访问
    - 返回当前用户收藏的艺术家信息
    - 演示如何在API中使用JWT认证
    
    **认证要求：**
    - 需要在请求头中提供有效的JWT Token
    - 格式：Authorization: Bearer <your_jwt_token>
    """
    # 这里可以根据用户ID从数据库查询用户的收藏数据
    # 现在先返回示例数据
    user_id = current_user["user_id"]
    
    # 模拟数据库查询
    mock_favorites = [
        {
            "artist_id": 1,
            "artist_name": "King Gnu",
            "added_date": "2024-01-15"
        },
        {
            "artist_id": 2,
            "artist_name": "Perfume",
            "added_date": "2024-01-20"
        }
    ]
    
    return {
        "success": True,
        "user_id": user_id,
        "favorites": mock_favorites,
        "total": len(mock_favorites)
    }

@router.post("/add-favorite")
async def add_to_favorites(
    artist_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    将艺术家添加到用户收藏（需要登录）
    
    **功能说明：**
    - 只有登录用户才能添加收藏
    - 将指定艺术家添加到当前用户的收藏列表
    
    **认证要求：**
    - 需要有效的JWT Token
    """
    user_id = current_user["user_id"]
    
    # 这里应该将数据保存到数据库
    # 现在只是返回成功消息
    
    logger.info(f"User {user_id} added artist {artist_id} to favorites")
    
    return {
        "success": True,
        "message": f"Artist {artist_id} added to favorites",
        "user_id": user_id
    }

@router.get("/public-with-user-context")
async def public_api_with_optional_auth(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    公开API，但如果用户登录了会提供个性化内容
    
    **功能说明：**
    - 不需要登录就能访问
    - 如果用户已登录，会返回个性化内容
    - 演示可选认证的使用场景
    
    **认证要求：**
    - 不强制要求JWT Token
    - 如果提供了有效Token，会返回个性化内容
    """
    if current_user:
        # 用户已登录，返回个性化内容
        return {
            "success": True,
            "message": f"Welcome back, {current_user['email']}!",
            "user_logged_in": True,
            "personalized_content": [
                "Based on your listening history...",
                "Recommended artists for you...",
                "Your favorite genres..."
            ]
        }
    else:
        # 用户未登录，返回通用内容
        return {
            "success": True,
            "message": "Welcome to Fuji Rock 2025!",
            "user_logged_in": False,
            "general_content": [
                "Featured artists",
                "Popular tracks",
                "Festival schedule"
            ]
        } 