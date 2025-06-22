"""
AI API 相关数据模型（DeepSeek AI）
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class AIRequest(BaseModel):
    """AI 请求模型"""
    artist_name: str = Field(..., description="艺术家名称", min_length=1)
    wiki_content: str = Field(..., description="Wikipedia 内容", min_length=10)
    style_intensity: int = Field(5, description="毒舌程度 (1-10)", ge=1, le=10)
    language: str = Field("zh", description="输出语言", pattern="^(zh|en|ja|ko)$")
    max_length: int = Field(500, description="最大输出长度", ge=100, le=2000)
    temperature: float = Field(0.8, description="创造性程度", ge=0.0, le=2.0)

class StyleMetrics(BaseModel):
    """风格指标模型"""
    humor_level: int = Field(..., description="幽默程度 (1-10)", ge=1, le=10)
    sarcasm_level: int = Field(..., description="讽刺程度 (1-10)", ge=1, le=10)
    fact_accuracy: float = Field(..., description="事实准确性 (0.0-1.0)", ge=0.0, le=1.0)

class AIData(BaseModel):
    """AI 生成数据模型"""
    model_config = ConfigDict(protected_namespaces=())
    
    original_content: str = Field(..., description="原始内容")
    sassy_description: str = Field(..., description="毒舌风格描述")
    style_metrics: StyleMetrics = Field(..., description="风格指标")
    generated_at: datetime = Field(..., description="生成时间")
    model_used: str = Field(..., description="使用的模型")
    tokens_used: Optional[int] = Field(None, description="使用的 token 数量")
    generation_time_ms: Optional[int] = Field(None, description="生成时间(毫秒)")

class AIResponse(BaseModel):
    """AI 响应模型"""
    success: bool = True
    data: AIData

class OpenAIUsageStats(BaseModel):
    """OpenAI 使用统计模型"""
    total_requests: int = Field(..., description="总请求数")
    total_tokens: int = Field(..., description="总 token 数")
    average_response_time: float = Field(..., description="平均响应时间(秒)")
    success_rate: float = Field(..., description="成功率") 