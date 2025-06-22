"""
配置模块 - 管理环境变量和应用配置
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "Fuji Rock 2025 API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Music exploration tool for Fuji Rock 2025"
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API 密钥配置
    ARK_API_KEY: Optional[str] = os.getenv("ARK_API_KEY")
    SPOTIFY_CLIENT_ID: Optional[str] = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: Optional[str] = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    # Supabase 配置
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    # JWT Secret 用于验证 Supabase 生成的 JWT Token
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")
    
    # Wikipedia API 配置
    WIKIPEDIA_API_URL: str = os.getenv("WIKIPEDIA_API_URL", "https://zh.wikipedia.org/api/rest_v1")
    WIKIPEDIA_USER_AGENT: str = os.getenv("WIKIPEDIA_USER_AGENT", "FujiRock2025API/1.0 (https://github.com/example/fujirock)")
    
    # DeepSeek AI API 配置
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", 1000))
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", 0.8))
    
    # Spotify API 配置
    SPOTIFY_API_URL: str = os.getenv("SPOTIFY_API_URL", "https://api.spotify.com/v1")
    SPOTIFY_AUTH_URL: str = os.getenv("SPOTIFY_AUTH_URL", "https://accounts.spotify.com/api/token")
    
    # HTTP 客户端配置
    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", 30.0))
    HTTP_RETRIES: int = int(os.getenv("HTTP_RETRIES", 3))
    
    # 服务特定超时配置
    WIKIPEDIA_TIMEOUT: float = float(os.getenv("WIKIPEDIA_TIMEOUT", 8.0))  # Wikipedia专用超时：8秒
    SPOTIFY_TIMEOUT: float = float(os.getenv("SPOTIFY_TIMEOUT", 10.0))     # Spotify专用超时：10秒
    ITUNES_TIMEOUT: float = float(os.getenv("ITUNES_TIMEOUT", 5.0))        # iTunes专用超时：5秒
    AI_TIMEOUT: float = float(os.getenv("AI_TIMEOUT", 15.0))               # AI API专用超时：15秒
    
    # CORS 配置
    CORS_ORIGINS: list = ["*"]  # 生产环境中应该设置具体的域名
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.ENVIRONMENT == "production"
    
    def validate_api_keys(self) -> dict:
        """验证 API 密钥配置"""
        validation_result = {
            "deepseek": bool(self.ARK_API_KEY),
            "spotify": bool(self.SPOTIFY_CLIENT_ID and self.SPOTIFY_CLIENT_SECRET),
            "wikipedia": True,  # Wikipedia 不需要密钥
            "supabase": bool(self.SUPABASE_URL and self.SUPABASE_ANON_KEY and self.SUPABASE_SERVICE_ROLE_KEY),
            "supabase_jwt": bool(self.SUPABASE_JWT_SECRET)  # 验证JWT Secret是否配置
        }
        return validation_result
    
    def get_http_headers(self, service: str = "default") -> dict:
        """获取 HTTP 请求头"""
        base_headers = {
            "User-Agent": self.WIKIPEDIA_USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        return base_headers

# 创建全局配置实例
settings = Settings()

# 配置日志
def setup_logging():
    """配置应用日志"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            # 可以添加文件处理器
            # logging.FileHandler('app.log')
        ]
    )

# 初始化日志
setup_logging()
logger = logging.getLogger(__name__)

# 启动时验证配置
def validate_settings():
    """验证应用配置"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    api_validation = settings.validate_api_keys()
    logger.info(f"API Keys validation: {api_validation}")
    
    if settings.is_production and not api_validation["deepseek"]:
        logger.warning("DeepSeek AI API key not configured in production environment")
    
    if not api_validation["supabase"]:
        logger.warning("Supabase configuration incomplete - database features may not work")
    
    return api_validation 