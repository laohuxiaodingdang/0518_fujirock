"""
认证服务 - 处理Supabase JWT Token验证
"""
import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from config import settings

logger = logging.getLogger(__name__)

class AuthService:
    """认证服务类 - 负责JWT Token的验证和用户信息提取"""
    
    def __init__(self):
        # 从环境变量获取JWT Secret，这是Supabase项目的JWT密钥
        self.jwt_secret = settings.SUPABASE_JWT_SECRET
        if not self.jwt_secret:
            logger.warning("SUPABASE_JWT_SECRET not configured - JWT verification will fail")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT Token的有效性并提取用户信息
        
        Args:
            token: Supabase生成的JWT Token
            
        Returns:
            包含用户信息的字典，如果验证失败则返回None
            返回格式: {
                'user_id': str,     # 用户ID
                'email': str,       # 用户邮箱
                'exp': int,         # Token过期时间戳
                'iat': int,         # Token签发时间戳
                'role': str         # 用户角色
            }
        """
        if not self.jwt_secret:
            logger.error("JWT Secret not configured")
            return None
        
        try:
            # 使用PyJWT解码并验证Token
            # 这里验证Token的签名、过期时间等
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],  # Supabase使用HS256算法
                options={
                    "verify_signature": True,   # 验证签名
                    "verify_exp": True,         # 验证过期时间
                    "verify_iat": True,         # 验证签发时间
                }
            )
            
            # 检查Token是否包含必要的用户信息
            if "sub" not in payload:  # sub字段包含用户ID
                logger.warning("Token missing user ID (sub field)")
                return None
            
            # 提取用户信息
            user_info = {
                "user_id": payload["sub"],                    # 用户ID
                "email": payload.get("email", ""),           # 用户邮箱
                "exp": payload.get("exp", 0),                # 过期时间
                "iat": payload.get("iat", 0),                # 签发时间
                "role": payload.get("role", "authenticated") # 用户角色
            }
            
            logger.info(f"Token verified successfully for user: {user_info['user_id']}")
            return user_info
            
        except jwt.ExpiredSignatureError:
            # Token已过期
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            # Token无效（签名错误、格式错误等）
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            # 其他错误
            logger.error(f"Token verification error: {str(e)}")
            return None
    
    def extract_user_id(self, token: str) -> Optional[str]:
        """
        从Token中提取用户ID的便捷方法
        
        Args:
            token: JWT Token
            
        Returns:
            用户ID字符串，如果提取失败则返回None
        """
        user_info = self.verify_token(token)
        return user_info["user_id"] if user_info else None
    
    def is_token_valid(self, token: str) -> bool:
        """
        检查Token是否有效的便捷方法
        
        Args:
            token: JWT Token
            
        Returns:
            True if token is valid, False otherwise
        """
        return self.verify_token(token) is not None

# 创建全局认证服务实例
auth_service = AuthService() 