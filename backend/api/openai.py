"""
DeepSeek AI API 路由
"""
from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import json

from models.openai import AIRequest, AIResponse
from services.openai_service import DeepSeekAIService

router = APIRouter(prefix="/api/ai", tags=["DeepSeek AI"])

# 创建服务实例
deepseek_service = DeepSeekAIService()

@router.post(
    "/generate-description", 
    response_model=AIResponse,
    summary="生成毒舌风格的艺术家介绍",
    description="""
    使用 DeepSeek AI 模型生成风趣幽默的艺术家介绍。
    
    特点：
    - 可调节毒舌程度（1-10级）
    - 支持多种语言输出
    - 保持事实准确性
    - 风格幽默但不恶意
    
    适用于音乐推荐、娱乐内容创作等场景。
    """,
    responses={
        200: {
            "description": "成功生成毒舌介绍",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "original_content": "Radiohead are an English rock band...",
                            "sassy_description": "这支来自英国的乐队，以其独特的音乐风格著称...",
                            "style_metrics": {
                                "humor_level": 7,
                                "sarcasm_level": 5,
                                "fact_accuracy": 0.9
                            },
                            "generated_at": "2024-01-01T12:00:00",
                            "model_used": "deepseek-chat",
                            "tokens_used": 150
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数无效"},
        401: {"description": "DeepSeek AI API 密钥无效"},
        429: {"description": "API 调用频率限制"},
        500: {"description": "生成服务错误"}
    }
)
async def generate_sassy_description(
    request: AIRequest = Body(
        ...,
        example={
            "wiki_content": "Radiohead are an English rock band formed in Abingdon, Oxfordshire, in 1985.",
            "style_intensity": 5,
            "language": "zh",
            "max_length": 500,
            "temperature": 0.8
        }
    )
):
    """
    生成毒舌风格的艺术家介绍
    
    请求体参数：
    - **wiki_content**: Wikipedia 内容（必需，最少10字符）
    - **style_intensity**: 毒舌程度，1-10级，数值越高越犀利
    - **language**: 输出语言（zh/en/ja/ko），默认中文
    - **max_length**: 最大输出长度，100-2000字符
    - **temperature**: 创造性程度，0.0-2.0，数值越高越有创意
    
    返回生成的毒舌风格介绍，包含风格分析和使用统计。
    """
    try:
        description_data = await deepseek_service.generate_description(request)
        return AIResponse(success=True, data=description_data)
    except HTTPException:
        # 重新抛出已处理的 HTTP 异常
        raise
    except Exception as e:
        # 处理未预期的异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Generation failed",
                "message": "An unexpected error occurred while generating description",
                "service": "DeepSeekAI",
                "details": str(e)
            }
        )

@router.post(
    "/generate-description-stream", 
    summary="生成毒舌风格的艺术家介绍 (流式)",
    description="""
    使用 DeepSeek AI 模型生成风趣幽默的艺术家介绍，支持实时流式输出。
    
    特点：
    - 实时显示生成过程
    - 可调节毒舌程度（1-10级）
    - 支持多种语言输出
    - 显著提升用户体验
    
    返回 Server-Sent Events (SSE) 流，前端可以实时显示生成内容。
    """,
    responses={
        200: {
            "description": "流式生成成功",
            "content": {
                "text/plain": {
                    "example": "data: {\"type\":\"content\",\"content\":\"这支乐队...\",\"is_complete\":false}\n\ndata: {\"type\":\"complete\",\"content\":\"完整内容\",\"is_complete\":true}\n\n"
                }
            }
        },
        400: {"description": "请求参数无效"},
        401: {"description": "DeepSeek AI API 密钥无效"},
        429: {"description": "API 调用频率限制"},
        500: {"description": "生成服务错误"}
    }
)
async def generate_sassy_description_stream(
    request: AIRequest = Body(
        ...,
        example={
            "artist_name": "Nirvana",
            "wiki_content": "Nirvana was an American rock band formed in Aberdeen, Washington, in 1987.",
            "style_intensity": 8,
            "language": "zh",
            "max_length": 500,
            "temperature": 0.7
        }
    )
):
    """
    生成毒舌风格的艺术家介绍 - 流式版本
    
    请求体参数：
    - **artist_name**: 艺术家名称（必需）
    - **wiki_content**: Wikipedia 内容（必需，最少10字符）
    - **style_intensity**: 毒舌程度，1-10级，数值越高越犀利
    - **language**: 输出语言（zh/en/ja/ko），默认中文
    - **max_length**: 最大输出长度，100-2000字符
    - **temperature**: 创造性程度，0.0-2.0，数值越高越有创意
    
    返回 Server-Sent Events 流，包含实时生成的内容。
    """
    async def generate_stream():
        try:
            async for chunk in deepseek_service.generate_description_stream(request):
                # 格式化为 SSE 格式
                data = json.dumps(chunk, ensure_ascii=False)
                yield f"data: {data}\n\n"
                
                # 如果完成或出错，结束流
                if chunk.get("is_complete", False):
                    break
                    
        except Exception as e:
            # 发送错误信息
            error_data = {
                "type": "error",
                "error": str(e),
                "is_complete": True
            }
            data = json.dumps(error_data, ensure_ascii=False)
            yield f"data: {data}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

@router.post(
    "/analyze-sentiment",
    summary="分析文本情感",
    description="""
    分析给定文本的情感倾向和情绪特征。
    
    返回详细的情感分析结果，包括：
    - 情感极性（正面/负面/中性）
    - 置信度评分
    - 情绪标签
    - 主观性程度
    """,
    responses={
        200: {
            "description": "情感分析成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "sentiment": "positive",
                            "confidence": 0.85,
                            "emotions": ["joy", "excitement"],
                            "polarity": 0.6,
                            "subjectivity": 0.7,
                            "source": "deepseek"
                        }
                    }
                }
            }
        },
        400: {"description": "文本参数无效"},
        500: {"description": "分析服务错误"}
    }
)
async def analyze_text_sentiment(
    text: str = Body(
        ..., 
        description="要分析的文本内容",
        min_length=1,
        max_length=5000,
        example="这首歌真的很棒，让人心情愉悦！"
    )
):
    """
    分析文本情感
    
    - **text**: 要分析的文本内容（必需，1-5000字符）
    
    返回详细的情感分析结果，包括情感极性、置信度和情绪标签。
    """
    try:
        sentiment_data = await deepseek_service.analyze_sentiment(text)
        return {
            "success": True,
            "data": sentiment_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "Sentiment analysis failed",
                "message": "Failed to analyze text sentiment",
                "service": "DeepSeekAI",
                "details": str(e)
            }
        )

@router.get(
    "/status",
    summary="获取 DeepSeek AI 服务状态",
    description="""
    检查 DeepSeek AI 服务的可用性和配置状态。
    
    返回服务状态信息，包括：
    - API 密钥配置状态
    - 服务可用性
    - 当前环境信息
    """,
    responses={
        200: {
            "description": "状态检查成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "available": True,
                            "api_key_configured": True,
                            "environment": "development",
                            "model": "deepseek-chat"
                        }
                    }
                }
            }
        }
    }
)
async def get_ai_status():
    """
    获取 DeepSeek AI 服务状态
    
    返回当前 DeepSeek AI 服务的配置和可用性信息。
    """
    try:
        return {
            "success": True,
            "data": {
                "available": deepseek_service.is_available(),
                "api_key_configured": bool(deepseek_service.api_key),
                "environment": "production" if deepseek_service.api_key else "development",
                "model": deepseek_service.model,
                "max_tokens": deepseek_service.max_tokens,
                "service": "DeepSeekAI"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Status check failed",
                "message": "Failed to get DeepSeek AI service status",
                "details": str(e)
            }
        )

@router.get(
    "/usage-stats",
    summary="获取 API 使用统计",
    description="""
    获取 DeepSeek AI API 的使用统计信息。
    
    包括请求次数、token 使用量、响应时间等指标。
    """,
    responses={
        200: {
            "description": "统计信息获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total_requests": 150,
                            "total_tokens": 45000,
                            "average_response_time": 2.5,
                            "success_rate": 0.98,
                            "last_updated": "2024-01-01T12:00:00",
                            "service": "DeepSeekAI"
                        }
                    }
                }
            }
        }
    }
)
async def get_usage_statistics():
    """
    获取 API 使用统计
    
    返回 DeepSeek AI API 的详细使用统计信息。
    """
    try:
        stats = await deepseek_service.get_usage_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Stats retrieval failed",
                "message": "Failed to get usage statistics",
                "details": str(e)
            }
        ) 