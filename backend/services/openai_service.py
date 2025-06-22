"""
DeepSeek AI 服务 - 处理 DeepSeek AI API 相关逻辑
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import HTTPException
from volcenginesdkarkruntime import Ark

from config import settings
from models.openai import AIRequest, AIData, StyleMetrics

logger = logging.getLogger(__name__)

class DeepSeekAIService:
    """DeepSeek AI API 服务类"""
    
    def __init__(self):
        self.api_key = settings.ARK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.max_tokens = settings.DEEPSEEK_MAX_TOKENS
        self.timeout = settings.HTTP_TIMEOUT
        self.client = None
        
        if self.api_key:
            try:
                self.client = Ark(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize DeepSeek AI client: {str(e)}")
    
    async def get_mock_data(self, request: AIRequest) -> AIData:
        """获取 Mock 数据"""
        logger.info(f"Using MOCK DeepSeek AI API with intensity: {request.style_intensity}")
        
        # 根据毒舌程度生成不同的 Mock 内容
        intensity_descriptions = {
            1: "这位艺术家还算不错，虽然有些地方可以改进。",
            2: "嗯，这个艺术家有点意思，但也就那样吧。",
            3: "说实话，这位艺术家的作品有些让人摸不着头脑。",
            4: "这个艺术家的风格...怎么说呢，挺独特的（褒义）。",
            5: "中等毒舌：这位艺术家的音乐就像是在考验听众的耐心。",
            6: "这个艺术家的作品让人想起了那些'实验性'音乐的魅力。",
            7: "高级毒舌：听这位艺术家的音乐需要一定的...勇气。",
            8: "这位艺术家成功地重新定义了什么叫'与众不同'。",
            9: "极度毒舌：这个艺术家的音乐是对传统美学的一次大胆挑战。",
            10: "终极毒舌：这位艺术家的作品让人深刻理解了'艺术无界限'这句话。"
        }
        
        mock_description = intensity_descriptions.get(
            request.style_intensity, 
            f"Mock 毒舌评价 (强度: {request.style_intensity}/10)"
        )
        
        return AIData(
            original_content=request.wiki_content[:200] + "..." if len(request.wiki_content) > 200 else request.wiki_content,
            sassy_description=mock_description,
            style_metrics=StyleMetrics(
                humor_level=min(request.style_intensity + 2, 10),
                sarcasm_level=request.style_intensity,
                fact_accuracy=0.95
            ),
            generated_at=datetime.now(),
            model_used="mock-deepseek-chat",
            tokens_used=len(mock_description.split()) * 2  # 模拟 token 使用量
        )
    
    async def get_real_data(self, request: AIRequest) -> AIData:
        """获取真实 DeepSeek AI 数据"""
        if not self.client:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "API key not configured",
                    "message": "DeepSeek AI API key is not configured. Please set ARK_API_KEY in environment variables.",
                    "service": "DeepSeekAI"
                }
            )
        
        logger.info(f"Using REAL DeepSeek AI API with model: {self.model}, intensity: {request.style_intensity}")
        
        # 构建提示词
        system_prompt = self._build_system_prompt(request)
        user_prompt = f"请为以下艺术家写一段毒舌介绍：\n\n{request.wiki_content}"
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=min(request.max_length // 2, self.max_tokens),
                temperature=request.temperature,
            )
            
            if not completion.choices or len(completion.choices) == 0:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "No response generated",
                        "message": "DeepSeek AI API did not return any content",
                        "service": "DeepSeekAI"
                    }
                )
            
            generated_text = completion.choices[0].message.content
            usage_data = completion.usage if hasattr(completion, 'usage') else None
            tokens_used = usage_data.total_tokens if usage_data else None
            
            # 分析生成内容的风格指标
            style_metrics = self._analyze_style_metrics(generated_text, request.style_intensity)
            
            return AIData(
                original_content=request.wiki_content[:200] + "..." if len(request.wiki_content) > 200 else request.wiki_content,
                sassy_description=generated_text.strip(),
                style_metrics=style_metrics,
                generated_at=datetime.now(),
                model_used=self.model,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            logger.error(f"DeepSeek AI API error: {str(e)}")
            
            # 处理不同类型的错误
            if "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": "DeepSeek AI API rate limit exceeded. Please try again later.",
                        "service": "DeepSeekAI"
                    }
                )
            elif "unauthorized" in str(e).lower() or "invalid" in str(e).lower():
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "Authentication failed",
                        "message": "Invalid DeepSeek AI API key",
                        "service": "DeepSeekAI"
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "AI service error",
                        "message": f"DeepSeek AI API error: {str(e)}",
                        "service": "DeepSeekAI"
                    }
                )
    
    def _build_system_prompt(self, request: AIRequest) -> str:
        """构建系统提示词"""
        language_map = {
            "zh": "中文",
            "en": "English",
            "ja": "日本語",
            "ko": "한국어"
        }
        
        language_name = language_map.get(request.language, "中文")
        
        return f"""
你是一个风趣幽默的音乐评论家，擅长用毒舌但不失准确的方式介绍艺术家。

要求：
- 毒舌程度：{request.style_intensity}/10 (1=温和调侃，10=犀利毒舌)
- 输出语言：{language_name}
- 最大长度：{request.max_length} 字符
- 保持事实准确性，不编造虚假信息
- 风格要幽默但不恶意，避免人身攻击
- 可以适当使用比喻、讽刺和双关语
- 重点评价音乐风格、作品特点和艺术成就

请确保内容既有趣又尊重艺术家的成就，即使是毒舌也要有建设性。
        """.strip()
    
    def _analyze_style_metrics(self, text: str, target_intensity: int) -> StyleMetrics:
        """分析生成文本的风格指标"""
        # TODO: 实现更精确的文本分析逻辑
        # 这里使用简单的启发式方法
        
        # 计算幽默程度（基于特定词汇和句式）
        humor_indicators = ["哈", "呵", "嗯", "居然", "竟然", "不得不说", "说实话"]
        humor_count = sum(1 for indicator in humor_indicators if indicator in text)
        humor_level = min(target_intensity + humor_count, 10)
        
        # 讽刺程度基本等于目标强度
        sarcasm_level = target_intensity
        
        # 事实准确性（在真实 API 中应该更高）
        fact_accuracy = 0.9
        
        return StyleMetrics(
            humor_level=humor_level,
            sarcasm_level=sarcasm_level,
            fact_accuracy=fact_accuracy
        )
    
    async def generate_description(self, request: AIRequest) -> AIData:
        """
        生成毒舌风格介绍 - 根据环境选择数据源
        
        Args:
            request: AI 请求参数
            
        Returns:
            AIData: 生成的毒舌风格介绍
            
        Raises:
            HTTPException: 当 API 调用失败时
        """
        if settings.is_production and self.api_key:
            return await self.get_real_data(request)
        else:
            return await self.get_mock_data(request)
    
    async def generate_description_stream(self, request: AIRequest):
        """
        生成毒舌风格介绍 - 流式版本
        
        Args:
            request: AI 请求参数
            
        Yields:
            Dict: 流式数据块，包含 type, content, is_complete 等字段
        """
        try:
            if settings.is_production and self.api_key:
                # 真实流式 API 调用
                async for chunk in self._generate_real_stream(request):
                    yield chunk
            else:
                # Mock 流式数据
                async for chunk in self._generate_mock_stream(request):
                    yield chunk
        except Exception as e:
            logger.error(f"Stream generation error: {str(e)}")
            yield {
                "type": "error",
                "error": str(e),
                "is_complete": True
            }
    
    async def _generate_mock_stream(self, request: AIRequest):
        """生成 Mock 流式数据"""
        import asyncio
        
        logger.info(f"Using MOCK stream for {request.style_intensity} intensity")
        
        # 根据毒舌程度生成不同的内容
        mock_content = f"这位艺术家的音乐风格独特，毒舌程度 {request.style_intensity}/10。他们的作品展现了独特的艺术表现力，虽然有些地方可以改进，但整体来说还是很有特色的。"
        
        # 模拟流式输出
        words = mock_content.split()
        current_content = ""
        
        for i, word in enumerate(words):
            current_content += word
            if i < len(words) - 1:
                current_content += ""
            
            # 模拟网络延迟
            await asyncio.sleep(0.1)
            
            yield {
                "type": "content",
                "content": current_content,
                "is_complete": False
            }
        
        # 最终完成消息
        yield {
            "type": "complete",
            "content": current_content,
            "is_complete": True,
            "style_metrics": {
                "humor_level": min(request.style_intensity + 2, 10),
                "sarcasm_level": request.style_intensity,
                "fact_accuracy": 0.95
            },
            "generated_at": datetime.now().isoformat(),
            "model_used": "mock-deepseek-chat",
            "tokens_used": len(words) * 2
        }
    
    async def _generate_real_stream(self, request: AIRequest):
        """生成真实流式数据"""
        if not self.client:
            raise HTTPException(
                status_code=500,
                detail="DeepSeek AI client not initialized"
            )
        
        logger.info(f"Using REAL stream API with model: {self.model}")
        
        # 构建提示词
        system_prompt = self._build_system_prompt(request)
        user_prompt = f"请为以下艺术家写一段毒舌介绍：\n\n{request.wiki_content}"
        
        try:
            # 使用流式 API
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=min(request.max_length // 2, self.max_tokens),
                temperature=request.temperature,
                stream=True
            )
            
            current_content = ""
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        current_content += delta.content
                        
                        yield {
                            "type": "content",
                            "content": current_content,
                            "is_complete": False
                        }
            
            # 分析风格指标
            style_metrics = self._analyze_style_metrics(current_content, request.style_intensity)
            
            # 最终完成消息
            yield {
                "type": "complete",
                "content": current_content,
                "is_complete": True,
                "style_metrics": {
                    "humor_level": style_metrics.humor_level,
                    "sarcasm_level": style_metrics.sarcasm_level,
                    "fact_accuracy": style_metrics.fact_accuracy
                },
                "generated_at": datetime.now().isoformat(),
                "model_used": self.model,
                "tokens_used": len(current_content.split()) * 2  # 估算
            }
            
        except Exception as e:
            logger.error(f"Real stream API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Stream generation failed: {str(e)}"
            )
    
    async def generate_sassy_description(self, artist_name: str, wiki_content: str, style_intensity: int = 8, language: str = "zh", max_length: int = 500, temperature: float = 0.8) -> Dict[str, Any]:
        """
        生成毒舌风格介绍 - 兼容旧接口
        
        Args:
            artist_name: 艺术家名称
            wiki_content: Wikipedia 内容
            style_intensity: 毒舌程度 (1-10)
            language: 语言代码
            max_length: 最大长度
            temperature: 创造性程度
            
        Returns:
            Dict: 包含生成结果的字典
        """
        from models.openai import AIRequest
        
        request = AIRequest(
            wiki_content=wiki_content,
            style_intensity=style_intensity,
            language=language,
            max_length=max_length,
            temperature=temperature
        )
        
        try:
            result = await self.generate_description(request)
            return {
                "success": True,
                "data": {
                    "sassy_description": result.sassy_description,
                    "style_metrics": {
                        "humor_level": result.style_metrics.humor_level,
                        "sarcasm_level": result.style_metrics.sarcasm_level,
                        "fact_accuracy": result.style_metrics.fact_accuracy
                    },
                    "generated_at": result.generated_at.isoformat(),
                    "model_used": result.model_used,
                    "tokens_used": result.tokens_used,
                    "generation_time_ms": 1000  # Mock 值
                }
            }
        except HTTPException as e:
            return {
                "success": False,
                "error": e.detail,
                "details": "HTTPException occurred"
            }
        except Exception as e:
            logger.error(f"Unexpected error in generate_sassy_description: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "details": "Unexpected error occurred"
            }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        分析文本情感 - 扩展功能
        
        Args:
            text: 要分析的文本
            
        Returns:
            Dict: 情感分析结果
        """
        if not settings.is_production or not self.api_key:
            # TODO: 返回 Mock 情感分析结果
            logger.info(f"Using MOCK sentiment analysis for text: {text[:50]}...")
            return {
                "sentiment": "neutral",
                "confidence": 0.8,
                "emotions": ["humor", "sarcasm"],
                "polarity": 0.1,  # -1 (negative) to 1 (positive)
                "subjectivity": 0.7,  # 0 (objective) to 1 (subjective)
                "source": "mock"
            }
        
        # TODO: 实现真实的情感分析 API 调用
        # 可以使用 DeepSeek AI 的 API 或其他情感分析服务
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "分析以下文本的情感，返回 JSON 格式：{\"sentiment\": \"positive/negative/neutral\", \"confidence\": 0.0-1.0, \"emotions\": [\"list\"], \"polarity\": -1.0-1.0}"
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            if completion.choices and len(completion.choices) > 0:
                result_text = completion.choices[0].message.content
                
                # 尝试解析 JSON 结果
                import json
                try:
                    sentiment_result = json.loads(result_text)
                    sentiment_result["source"] = "deepseek"
                    return sentiment_result
                except json.JSONDecodeError:
                    # 如果解析失败，返回默认结果
                    return {
                        "sentiment": "neutral",
                        "confidence": 0.5,
                        "emotions": ["unknown"],
                        "polarity": 0.0,
                        "source": "deepseek_fallback",
                        "raw_response": result_text
                    }
            else:
                logger.error("Sentiment analysis API returned no choices")
                return {
                    "sentiment": "unknown",
                    "confidence": 0.0,
                    "emotions": ["error"],
                    "error": "No response from API"
                }
                    
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                "sentiment": "unknown",
                "confidence": 0.0,
                "emotions": ["error"],
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """检查 DeepSeek AI 服务是否可用"""
        return bool(self.api_key)
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取 API 使用统计 - 扩展功能
        
        Returns:
            Dict: 使用统计信息
        """
        # TODO: 实现真实的使用统计获取
        # 这需要维护本地的使用记录或调用 DeepSeek AI 的使用统计 API
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "average_response_time": 0.0,
            "success_rate": 1.0,
            "last_updated": datetime.now().isoformat(),
            "note": "Usage statistics not implemented yet",
            "service": "DeepSeekAI"
        }


# 创建服务实例
openai_service = DeepSeekAIService() 