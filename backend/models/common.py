"""
通用数据模型 - 定义通用的响应格式和基础模型
"""
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, Any
from datetime import datetime

# 泛型类型变量
T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """通用响应模型"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = datetime.now()

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    error: dict
    timestamp: datetime = datetime.now()

class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    environment: str
    apis: dict
    timestamp: datetime = datetime.now()

class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = 1
    limit: int = 10
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: list[T]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool 