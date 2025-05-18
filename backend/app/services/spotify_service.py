import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Initialize Spotify client
try:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if client_id and client_secret:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        spotify = spotipy.Spotify(auth_manager=auth_manager)
    else:
        logger.warning("Spotify credentials not found in environment variables")
        spotify = None
except Exception as e:
    logger.error(f"Error initializing Spotify client: {str(e)}")
    spotify = None


async def search_artist(artist_name: str) -> Optional[Dict[str, Any]]:
    """
    Search for an artist on Spotify
    """
    if not spotify:
        return None
    
    try:
        results = spotify.search(q=f"artist:{artist_name}", type="artist", limit=1)
        if results and results["artists"]["items"]:
            return results["artists"]["items"][0]
        return None
    except Exception as e:
        logger.error(f"Error searching Spotify: {str(e)}")
        return None


async def get_artist_top_tracks(spotify_id: str) -> List[Dict[str, Any]]:
    """
    Get top tracks for an artist from Spotify
    """
    if not spotify or not spotify_id:
        return []
    
    try:
        results = spotify.artist_top_tracks(spotify_id)
        
        tracks = []
        for track in results["tracks"]:
            tracks.append({
                "id": track["id"],
                "title": track["name"],
                "album": track["album"]["name"],
                "duration": _format_duration(track["duration_ms"]),
                "preview_url": track["preview_url"],
                "platform_links": {
                    "spotify": track["external_urls"].get("spotify", "")
                }
            })
        
        return tracks
    except Exception as e:
        logger.error(f"Error getting Spotify tracks: {str(e)}")
        return []


def _format_duration(duration_ms: int) -> str:
    """
    Format duration from milliseconds to mm:ss
    """
    seconds = duration_ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"
