from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.models.artist import ArtistResponse, ArtistDetail, SimilarArtist
from app.services import wiki_service, spotify_service, ai_service
from app import db

router = APIRouter()


@router.get("/artists", response_model=List[ArtistResponse])
async def get_artists():
    """
    Get all artists performing at Fuji Rock 2025
    """
    try:
        artists = await db.get_all_artists()
        return artists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/{artist_id}", response_model=ArtistDetail)
async def get_artist(artist_id: UUID):
    """
    Get detailed information about a specific artist
    """
    try:
        # Get base artist info
        artist = await db.get_artist_by_id(artist_id)
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        
        # Get songs from Spotify
        songs = await spotify_service.get_artist_top_tracks(artist.get("spotify_id"))
        
        # Get similar artists
        similar_artists = await db.get_similar_artists(artist_id)
        
        # Combine all data
        artist_detail = {**artist, "songs": songs, "similar_artists": similar_artists}
        
        return artist_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/{artist_id}/wiki", response_model=dict)
async def get_artist_wiki_data(artist_id: UUID):
    """
    Get original Wikipedia data for an artist
    """
    try:
        artist = await db.get_artist_by_id(artist_id)
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        
        # Return stored wiki data if available
        if artist.get("wiki_data"):
            return artist.get("wiki_data")
        
        # Otherwise fetch from Wikipedia
        wiki_data = await wiki_service.get_artist_info(artist.get("name"))
        
        # Store the data for future use
        # (implementation would update the database)
        
        return wiki_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/{artist_id}/ai-description", response_model=str)
async def get_artist_ai_description(artist_id: UUID):
    """
    Get AI-generated sarcastic description of an artist
    """
    try:
        artist = await db.get_artist_by_id(artist_id)
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        
        # Return stored AI description if available
        if artist.get("ai_description"):
            return artist.get("ai_description")
        
        # Get Wikipedia data
        wiki_data = await get_artist_wiki_data(artist_id)
        
        # Generate AI description
        ai_description = await ai_service.generate_sarcastic_description(
            artist.get("name"), wiki_data
        )
        
        # Store the AI description for future use
        # (implementation would update the database)
        
        return ai_description
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/{artist_id}/similar", response_model=List[SimilarArtist])
async def get_similar_artists(artist_id: UUID):
    """
    Get similar artists for a specific artist
    """
    try:
        similar_artists = await db.get_similar_artists(artist_id)
        return similar_artists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/{artist_id}/songs")
async def get_artist_songs(artist_id: UUID):
    """
    Get songs for a specific artist from Spotify
    """
    try:
        artist = await db.get_artist_by_id(artist_id)
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        
        if not artist.get("spotify_id"):
            raise HTTPException(status_code=404, detail="Artist does not have Spotify ID")
        
        songs = await spotify_service.get_artist_top_tracks(artist.get("spotify_id"))
        return songs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 