"""
API 路由包 - 包含所有路由定义
"""

from .wikipedia import router as wikipedia_router
#from .openai import router as openai_router
from .spotify import router as spotify_router
from .health import router as health_router 