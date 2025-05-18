from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routers
from app.routers import artists, auth, music, ai

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Fuji Rock 2025 API",
    description="API for Fuji Rock 2025 音乐探索工具",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(artists.router, prefix="/api", tags=["artists"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(music.router, prefix="/api", tags=["music"])
app.include_router(ai.router, prefix="/api", tags=["ai"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Fuji Rock 2025 API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    ) 