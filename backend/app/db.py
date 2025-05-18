import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in environment variables")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Example query functions
async def get_all_artists():
    """Get all artists from database"""
    response = supabase.table("artists").select("*").execute()
    return response.data


async def get_artist_by_id(artist_id: str):
    """Get artist by ID"""
    response = supabase.table("artists").select("*").eq("id", artist_id).execute()
    if response.data:
        return response.data[0]
    return None


async def get_favorite_artists(user_id: str):
    """Get favorite artists for a user"""
    response = (
        supabase.table("user_favorites")
        .select("artist_id(*)")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data


async def add_favorite_artist(user_id: str, artist_id: str):
    """Add artist to user favorites"""
    response = (
        supabase.table("user_favorites")
        .insert({"user_id": user_id, "artist_id": artist_id})
        .execute()
    )
    return response.data


async def remove_favorite_artist(user_id: str, artist_id: str):
    """Remove artist from user favorites"""
    response = (
        supabase.table("user_favorites")
        .delete()
        .eq("user_id", user_id)
        .eq("artist_id", artist_id)
        .execute()
    )
    return response.data


async def get_similar_artists(artist_id: str):
    """Get similar artists for an artist"""
    response = (
        supabase.table("similar_artists")
        .select("similar_artist_id(*), similarity_reason")
        .eq("artist_id", artist_id)
        .execute()
    )
    return response.data 