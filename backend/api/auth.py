"""
认证 API 路由 - 提供用户认证相关的接口
"""
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# 创建HTTP Bearer认证方案
security = HTTPBearer()

async def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    从请求头中提取JWT Token
    
    Args:
        authorization: Authorization请求头，格式为 "Bearer <token>"
        
    Returns:
        提取出的token字符串，如果没有则返回None
    """
    if not authorization:
        return None
    
    # 检查是否以"Bearer "开头
    if not authorization.startswith("Bearer "):
        return None
    
    # 提取token部分（去掉"Bearer "前缀）
    token = authorization[7:]  # "Bearer " 有7个字符
    return token if token else None

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    获取当前登录用户信息的依赖函数
    这个函数会被其他需要认证的API端点使用
    
    Args:
        authorization: Authorization请求头
        
    Returns:
        当前用户信息字典
        
    Raises:
        HTTPException: 如果token无效或用户未认证
    """
    # 从请求头提取token
    token = await get_token_from_header(authorization)
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证token并获取用户信息
    user_info = auth_service.verify_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info

async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    可选的用户认证依赖函数
    如果有token就验证，没有token也不报错
    适用于一些可选认证的接口
    
    Args:
        authorization: Authorization请求头
        
    Returns:
        用户信息字典或None
    """
    token = await get_token_from_header(authorization)
    
    if not token:
        return None
    
    return auth_service.verify_token(token)

# ==================== 认证相关的API端点 ====================

@router.get("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    验证当前token是否有效
    
    **功能说明：**
    - 验证前端传来的JWT token是否有效
    - 返回当前用户的基本信息
    
    **使用场景：**
    - 前端页面刷新时验证用户登录状态
    - 检查token是否即将过期
    """
    return {
        "success": True,
        "message": "Token is valid",
        "user": {
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "role": current_user["role"]
        }
    }

@router.get("/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    获取当前用户的详细信息
    
    **功能说明：**
    - 返回当前登录用户的详细信息
    - 需要有效的JWT token
    """
    return {
        "success": True,
        "user": current_user
    }

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    用户登出
    
    **功能说明：**
    - 服务端记录用户登出（可以在这里添加登出日志）
    - 实际的token失效需要前端删除本地存储的token
    
    **注意：**
    - JWT是无状态的，服务端无法直接让token失效
    - 真正的登出需要前端清除存储的token
    """
    logger.info(f"User {current_user['user_id']} logged out")
    
    return {
        "success": True,
        "message": "Logged out successfully"
    } 