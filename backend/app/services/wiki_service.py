import wikipediaapi
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def get_artist_info(artist_name: str) -> Dict[str, Any]:
    """
    Fetch artist information from Wikipedia
    """
    try:
        wiki_wiki = wikipediaapi.Wikipedia('fujirock-app (info@example.com)', 'zh')
        page = wiki_wiki.page(artist_name)
        
        if not page.exists():
            # Try English Wikipedia if Chinese page doesn't exist
            wiki_wiki = wikipediaapi.Wikipedia('fujirock-app (info@example.com)', 'en')
            page = wiki_wiki.page(artist_name)
            
        if not page.exists():
            return {"error": "No Wikipedia page found for this artist."}
            
        # Extract the content
        summary = page.summary
        full_text = page.text
        
        # Get sections
        sections = {}
        for section in page.sections:
            sections[section.title] = section.text
            
        return {
            "title": page.title,
            "summary": summary,
            "full_text": full_text,
            "sections": sections,
            "url": page.fullurl,
            "lang": page.language
        }
    except Exception as e:
        logger.error(f"Error fetching Wikipedia data: {str(e)}")
        return {"error": str(e)}
