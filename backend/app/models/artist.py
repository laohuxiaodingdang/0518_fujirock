from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class Song(BaseModel):
    """Song model"""
    id: str
    title: str
    album: Optional[str] = None
    duration: Optional[str] = None
    platform_links: Optional[Dict[str, str]] = None


class SimilarArtist(BaseModel):
    """Similar artist model"""
    id: UUID
    name: str
    image: Optional[str] = None
    similarity_reason: Optional[str] = None


class ArtistBase(BaseModel):
    """Base artist model"""
    name: str
    description: Optional[str] = None
    spotify_id: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    performance_time: Optional[datetime] = None
    stage_location: Optional[str] = None


class ArtistCreate(ArtistBase):
    """Artist creation model"""
    wiki_data: Optional[Dict[str, Any]] = None


class ArtistResponse(ArtistBase):
    """Artist response model"""
    id: UUID
    ai_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArtistDetail(ArtistResponse):
    """Detailed artist model"""
    songs: Optional[List[Song]] = None
    similar_artists: Optional[List[SimilarArtist]] = None

    class Config:
        from_attributes = True


class UserFavorite(BaseModel):
    """User favorite model"""
    id: UUID
    user_id: UUID
    artist_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True 