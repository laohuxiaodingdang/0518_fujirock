import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        logger.warning("OpenAI API key not found in environment variables")
        client = None
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    client = None


async def generate_sarcastic_description(artist_name: str, wiki_data: Dict[str, Any]) -> str:
    """
    Generate a sarcastic description of an artist based on Wikipedia data
    """
    if not client:
        return "AI description unavailable (API key not configured)."
    
    if not wiki_data or "error" in wiki_data:
        return f"没有找到关于 {artist_name} 的足够信息，无法生成介绍。"
    
    try:
        # Extract relevant info from wiki_data
        summary = wiki_data.get("summary", "")
        
        # Truncate if too long
        if len(summary) > 1500:
            summary = summary[:1500] + "..."
        
        # Create prompt
        prompt = f"""
        你是一个音乐评论家，风格有点毒舌但保持幽默，绝不刻薄。
        请基于以下维基百科的内容，为艺术家 "{artist_name}" 创作一段介绍。
        介绍应该：
        1. 长度大约200-300字
        2. 包含艺术家的关键事实信息
        3. 使用轻微毒舌但幽默的风格
        4. 偶尔加入有趣的评论或观点
        5. 结尾提及他们在富士摇滚音乐节的演出是值得期待的

        维基百科内容:
        {summary}
        """
        
        # Generate completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个专业的音乐评论家，风格略带毒舌但具有幽默感。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract and return the generated description
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content.strip()
        return f"无法为 {artist_name} 生成介绍。"
    
    except Exception as e:
        logger.error(f"Error generating AI description: {str(e)}")
        return f"生成 {artist_name} 的AI介绍时出错: {str(e)}"
