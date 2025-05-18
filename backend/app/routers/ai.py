from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import logging

from app.services import ai_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ai/generate-description")
async def generate_artist_description(data: Dict[str, Any] = Body(...)):
    """
    Generate an AI description of an artist
    """
    try:
        artist_name = data.get("name")
        wiki_data = data.get("wiki_data", {})
        
        if not artist_name:
            raise HTTPException(status_code=400, detail="Artist name is required")
            
        description = await ai_service.generate_sarcastic_description(artist_name, wiki_data)
        return {"description": description}
    except Exception as e:
        logger.error(f"Error generating AI description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/generate-similarity")
async def generate_similarity_reason(data: Dict[str, Any] = Body(...)):
    """
    Generate a reason why two artists are similar
    """
    try:
        # This would be implemented to generate similarity explanations
        artist1 = data.get("artist1", {}).get("name", "Unknown Artist 1")
        artist2 = data.get("artist2", {}).get("name", "Unknown Artist 2")
        
        # Placeholder response
        return {
            "reason": f"{artist1}和{artist2}的风格都融合了电子元素和流行旋律，他们的音乐都能让你在深夜开车时感到一种奇妙的共鸣。"
        }
    except Exception as e:
        logger.error(f"Error generating similarity reason: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
