"""
Wikipedia API 相关数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class WikiThumbnail(BaseModel):
    """Wikipedia 缩略图模型"""
    source: str = Field(..., description="图片URL")
    width: int = Field(..., description="图片宽度")
    height: int = Field(..., description="图片高度")

class WikiReference(BaseModel):
    """Wikipedia 参考资料模型"""
    title: str = Field(..., description="参考资料标题")
    url: str = Field(..., description="参考资料URL")

class WikipediaData(BaseModel):
    """Wikipedia 数据模型"""
    title: str = Field(..., description="页面标题")
    extract: str = Field(..., description="页面摘要")
    thumbnail: Optional[WikiThumbnail] = Field(None, description="缩略图")
    categories: List[str] = Field(default_factory=list, description="分类列表")
    references: List[WikiReference] = Field(default_factory=list, description="参考资料列表")

class WikipediaRequest(BaseModel):
    """Wikipedia 请求模型"""
    artist_name: str = Field(..., description="艺术家名称", min_length=1)
    language: str = Field("zh", description="语言代码", pattern="^(zh|en|ja|ko)$")
    include_references: bool = Field(False, description="是否包含参考资料")

class WikipediaResponse(BaseModel):
    """Wikipedia 响应模型"""
    success: bool = True
    data: WikipediaData 