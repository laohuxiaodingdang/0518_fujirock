"""
Wikipedia 服务 - 处理 Wikipedia API 相关逻辑
"""
import httpx
import logging
import time
from typing import Optional, List, Dict, Any
from fastapi import HTTPException

from config import settings
from models.wikipedia import WikipediaData, WikiThumbnail, WikiReference

logger = logging.getLogger(__name__)

# 简单的内存缓存
_wikipedia_cache = {}
CACHE_DURATION = 3600  # 缓存1小时

# 简单的繁体转简体字典（常用字符）
TRADITIONAL_TO_SIMPLIFIED = {
    '電': '电', '臺': '台', '司': '司', '令': '令', '來': '来', '自': '自', '英': '英', '國': '国',
    '牛': '牛', '津': '津', '郡': '郡', '阿': '阿', '賓': '宾', '頓': '顿', '男': '男', '類': '类',
    '搖': '摇', '滾': '滚', '樂': '乐', '團': '团', '組': '组', '建': '建', '於': '于', '年': '年',
    '樂': '乐', '團': '团', '由': '由', '湯': '汤', '姆': '姆', '約': '约', '克': '克', '主': '主',
    '唱': '唱', '吉': '吉', '他': '他', '鋼': '钢', '琴': '琴', '強': '强', '尼': '尼', '格': '格',
    '林': '林', '伍': '伍', '德': '德', '委': '委', '吉': '吉', '他': '他', '鍵': '键', '盤': '盘',
    '其': '其', '他': '他', '樂': '乐', '器': '器', '艾': '艾', '德': '德', '歐': '欧', '布': '布',
    '萊': '莱', '恩': '恩', '吉': '吉', '他': '他', '合': '合', '聲': '声', '科': '科', '林': '林',
    '格': '格', '林': '林', '伍': '伍', '德': '德', '貝': '贝', '斯': '斯', '與': '与', '菲': '菲',
    '利': '利', '普': '普', '塞': '塞', '爾': '尔', '章': '章', '鼓': '鼓', '打': '打', '擊': '击',
    '樂': '乐', '器': '器', '組': '组', '成': '成', '樂': '乐', '隊': '队', '風': '风', '格': '格',
    '實': '实', '驗': '验', '性': '性', '搖': '摇', '滾': '滚', '電': '电', '子': '子', '音': '音',
    '樂': '乐', '藝': '艺', '術': '术', '搖': '摇', '滾': '滚', '另': '另', '類': '类', '搖': '摇',
    '滾': '滚', '後': '后', '搖': '摇', '滾': '滚', '等': '等', '多': '多', '種': '种', '風': '风',
    '格': '格', '融': '融', '合': '合', '創': '创', '作': '作', '出': '出', '獨': '独', '特': '特',
    '音': '音', '樂': '乐', '風': '风', '格': '格', '專': '专', '輯': '辑', '發': '发', '行': '行',
    '後': '后', '獲': '获', '得': '得', '廣': '广', '泛': '泛', '讚': '赞', '譽': '誉', '並': '并',
    '確': '确', '立': '立', '樂': '乐', '壇': '坛', '地': '地', '位': '位', '樂': '乐', '團': '团',
    '持': '持', '續': '续', '創': '创', '新': '新', '實': '实', '驗': '验', '音': '音', '樂': '乐',
    '風': '风', '格': '格', '影': '影', '響': '响', '無': '无', '數': '数', '後': '后', '輩': '辈',
    '音': '音', '樂': '乐', '人': '人', '被': '被', '認': '认', '為': '为', '當': '当', '代': '代',
    '最': '最', '重': '重', '要': '要', '樂': '乐', '團': '团', '之': '之', '一': '一', '樂': '乐',
    '團': '团', '作': '作', '品': '品', '深': '深', '受': '受', '樂': '乐', '迷': '迷', '喜': '喜',
    '愛': '爱', '並': '并', '在': '在', '全': '全', '球': '球', '範': '范', '圍': '围', '內': '内',
    '擁': '拥', '有': '有', '龐': '庞', '大': '大', '粉': '粉', '絲': '丝', '群': '群', '體': '体'
}

def convert_traditional_to_simplified(text: str) -> str:
    """
    将繁体中文转换为简体中文
    
    Args:
        text: 包含繁体中文的文本
        
    Returns:
        str: 转换后的简体中文文本
    """
    if not text:
        return text
        
    result = ""
    for char in text:
        # 如果字符在转换字典中，使用简体字符，否则保持原字符
        result += TRADITIONAL_TO_SIMPLIFIED.get(char, char)
    
    return result

class WikipediaService:
    """Wikipedia API 服务类"""
    
    def __init__(self):
        self.timeout = settings.WIKIPEDIA_TIMEOUT  # 使用专门的Wikipedia超时配置
        self.retries = settings.HTTP_RETRIES
        self.user_agent = settings.WIKIPEDIA_USER_AGENT
    
    async def get_mock_data(self, artist_name: str, language: str) -> WikipediaData:
        """获取 Mock 数据"""
        logger.info(f"Using MOCK Wikipedia API for {artist_name}")
        
        # 根据艺术家名称提供不同的Mock数据
        mock_data = {
            "Radiohead": {
                "extract": "电台司令是一支来自英国牛津郡阿宾顿的男类摇滚乐团，组建于1985年。乐团由汤姆·约克（主唱、吉他、钢琴），强尼·格林伍德（主委吉他、键盘、其他乐器），艾德·欧布莱恩（吉他、合声），科林·格林伍德（贝斯），与菲利普·塞尔韦（鼓、打击乐器）组成。",
                "categories": ["英国摇滚乐团", "另类摇滚", "实验音乐"],
                "image": "https://i.scdn.co/image/ab6761610000e5eba03696716c9ee605006047fd"
            },
            "Nirvana": {
                "extract": "涅槃乐队是一支来自美国华盛顿州西雅图的摇滚乐队，成立于1987年。乐队由科特·柯本（主唱、吉他）、克里斯特·诺沃塞利奇（贝斯）和戴夫·格罗尔（鼓手）组成。他们是垃圾摇滚运动的先驱，对90年代的音乐产生了深远影响。",
                "categories": ["美国摇滚乐队", "垃圾摇滚", "另类摇滚"],
                "image": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=facearea&w=256&q=80"
            },
            "The Beatles": {
                "extract": "披头士乐队是一支英国摇滚乐队，成立于1960年，来自利物浦。乐队成员包括约翰·列侬、保罗·麦卡特尼、乔治·哈里森和林戈·斯塔尔。他们被广泛认为是流行音乐史上最具影响力的乐队。",
                "categories": ["英国摇滚乐队", "流行摇滚", "经典摇滚"],
                "image": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=facearea&w=256&q=80"
            },
            "Coldplay": {
                "extract": "酷玩乐队是一支英国摇滚乐队，成立于1996年，来自伦敦。乐队由克里斯·马丁（主唱、钢琴）、强尼·巴克兰（吉他）、盖伊·贝里曼（贝斯）和威尔·钱皮恩（鼓手）组成。他们以旋律优美的另类摇滚和流行摇滚而闻名。",
                "categories": ["英国摇滚乐队", "另类摇滚", "流行摇滚"],
                "image": "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=facearea&w=256&q=80"
            }
        }
        
        # 获取特定艺术家的数据，如果没有则使用默认数据
        artist_data = mock_data.get(artist_name, {
            "extract": f"{artist_name}是一位知名的音乐艺术家，以其独特的音乐风格和创作才华而闻名。该艺术家在音乐界有着重要的地位，作品深受听众喜爱。他们的音乐融合了多种风格元素，展现出了卓越的艺术表现力和创新精神。",
            "categories": ["音乐艺术家", "摇滚", "流行音乐"],
            "image": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=facearea&w=256&q=80"
        })
        
        # 应用繁体转简体转换
        simplified_extract = convert_traditional_to_simplified(artist_data["extract"])
        simplified_categories = [convert_traditional_to_simplified(cat) for cat in artist_data["categories"]]
        
        return WikipediaData(
            title=artist_name,
            extract=simplified_extract,
            thumbnail=WikiThumbnail(
                source=artist_data.get("image", "https://via.placeholder.com/800x600/0066cc/ffffff?text=Mock+Image"),
                width=800,
                height=600
            ),
            categories=simplified_categories,
            references=[
                WikiReference(
                    title="官方网站",
                    url="https://example.com/official"
                ),
                WikiReference(
                    title="音乐数据库",
                    url="https://example.com/music-db"
                )
            ]
        )
    
    async def get_real_data(self, artist_name: str, language: str) -> WikipediaData:
        """获取真实 Wikipedia 数据"""
        logger.info(f"Using REAL Wikipedia API for {artist_name} in {language}")
        
        base_url = f"https://{language}.wikipedia.org/api/rest_v1"
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # 获取页面摘要
                summary_response = await client.get(
                    f"{base_url}/page/summary/{artist_name}",
                    headers=headers
                )
                
                if summary_response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "Artist not found",
                            "message": f"Wikipedia page for '{artist_name}' not found in {language}",
                            "suggestion": "Try searching with a different name or language"
                        }
                    )
                elif summary_response.status_code != 200:
                    raise HTTPException(
                        status_code=summary_response.status_code,
                        detail={
                            "error": "Wikipedia API error",
                            "message": f"Failed to fetch data from Wikipedia: {summary_response.text}",
                            "status_code": summary_response.status_code
                        }
                    )
                
                summary_data = summary_response.json()
                
                # 解析缩略图
                thumbnail = None
                if summary_data.get("thumbnail"):
                    thumbnail_data = summary_data["thumbnail"]
                    thumbnail = WikiThumbnail(
                        source=thumbnail_data["source"],
                        width=thumbnail_data["width"],
                        height=thumbnail_data["height"]
                    )
                
                # 获取页面分类（可选）
                categories = await self._get_page_categories(client, base_url, artist_name, headers)
                
                # 获取外部链接作为参考资料（可选）
                references = await self._get_page_references(client, base_url, artist_name, headers)
                
                return WikipediaData(
                    title=summary_data.get("title", artist_name),
                    extract=convert_traditional_to_simplified(summary_data.get("extract", "No description available")),
                    thumbnail=thumbnail,
                    categories=categories,
                    references=references
                )
                
            except httpx.TimeoutException:
                logger.error(f"Wikipedia API timeout for {artist_name}")
                raise HTTPException(
                    status_code=408,
                    detail={
                        "error": "Request timeout",
                        "message": f"Wikipedia API request timeout after {self.timeout} seconds",
                        "retry_suggestion": "Please try again later"
                    }
                )
            except httpx.RequestError as e:
                logger.error(f"Wikipedia API network error: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Network error",
                        "message": f"Failed to connect to Wikipedia API: {str(e)}",
                        "service": "Wikipedia"
                    }
                )
            except HTTPException:
                # 重新抛出已处理的 HTTP 异常
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Wikipedia service: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": "An unexpected error occurred while processing Wikipedia data",
                        "details": str(e)
                    }
                )
    
    async def _get_page_categories(self, client: httpx.AsyncClient, base_url: str, 
                                 page_title: str, headers: Dict[str, str]) -> List[str]:
        """获取页面分类"""
        try:
            # TODO: 实现页面分类获取逻辑
            # Wikipedia API 需要额外的调用来获取分类信息
            # 这里返回空列表，可以后续实现
            return []
        except Exception as e:
            logger.warning(f"Failed to get categories for {page_title}: {str(e)}")
            return []
    
    async def _get_page_references(self, client: httpx.AsyncClient, base_url: str, 
                                 page_title: str, headers: Dict[str, str]) -> List[WikiReference]:
        """获取页面参考资料"""
        try:
            # TODO: 实现参考资料获取逻辑
            # 可以通过获取页面的外部链接来作为参考资料
            # 这里返回空列表，可以后续实现
            return []
        except Exception as e:
            logger.warning(f"Failed to get references for {page_title}: {str(e)}")
            return []
    
    async def get_artist_info(self, artist_name: str, language: str = "en") -> WikipediaData:
        """
        获取艺术家信息 - 优先使用真实数据，失败时回退到 Mock 数据
        支持缓存以提高性能
        
        Args:
            artist_name: 艺术家名称
            language: 语言代码 (zh, en, ja, ko)，默认为英文
            
        Returns:
            WikipediaData: 艺术家的 Wikipedia 信息
            
        Raises:
            HTTPException: 当所有方法都失败时
        """
        # 检查缓存
        cache_key = f"{artist_name}_{language}"
        current_time = time.time()
        
        if cache_key in _wikipedia_cache:
            cached_data, cached_time = _wikipedia_cache[cache_key]
            if current_time - cached_time < CACHE_DURATION:
                logger.info(f"Using cached Wikipedia data for {artist_name}")
                return cached_data
            else:
                # 缓存过期，删除旧数据
                del _wikipedia_cache[cache_key]
        
        try:
            # 首先尝试获取真实数据
            logger.info(f"Attempting to fetch real Wikipedia data for {artist_name}")
            result = await self.get_real_data(artist_name, language)
            
            # 缓存成功的结果
            _wikipedia_cache[cache_key] = (result, current_time)
            logger.info(f"Cached Wikipedia data for {artist_name}")
            
            return result
        except (httpx.TimeoutException, httpx.RequestError, HTTPException) as e:
            # 网络错误或超时时，回退到 Mock 数据
            logger.warning(f"Failed to fetch real Wikipedia data for {artist_name}: {str(e)}")
            logger.info(f"Falling back to mock data for {artist_name}")
            try:
                return await self.get_mock_data(artist_name, language)
            except Exception as mock_error:
                logger.error(f"Mock data also failed for {artist_name}: {str(mock_error)}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Service unavailable",
                        "message": f"Both real and mock Wikipedia data failed for '{artist_name}'",
                        "original_error": str(e),
                        "mock_error": str(mock_error)
                    }
                )
        except Exception as e:
            # 其他未预期的错误
            logger.error(f"Unexpected error fetching Wikipedia data for {artist_name}: {str(e)}")
            logger.info(f"Falling back to mock data for {artist_name}")
            try:
                return await self.get_mock_data(artist_name, language)
            except Exception as mock_error:
                logger.error(f"Mock data also failed for {artist_name}: {str(mock_error)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": f"Failed to get Wikipedia data for '{artist_name}'",
                        "original_error": str(e),
                        "mock_error": str(mock_error)
                    }
                )
    
    async def search_artists(self, query: str, language: str = "zh", limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索艺术家
        
        Args:
            query: 搜索关键词
            language: 语言代码
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        if not settings.is_production:
            # TODO: 在开发环境返回 Mock 搜索结果
            logger.info(f"Using MOCK search for query: {query}")
            return [
                {
                    "title": f"Mock Artist {i}",
                    "description": f"This is a mock search result for '{query}'",
                    "url": f"https://example.com/artist-{i}"
                }
                for i in range(1, min(limit + 1, 4))
            ]
        
        # 真实搜索实现
        base_url = f"https://{language}.wikipedia.org/api/rest_v1"
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # TODO: 实现真实的 Wikipedia 搜索 API 调用
                # 使用 Wikipedia 的搜索 API
                search_response = await client.get(
                    f"https://{language}.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "format": "json",
                        "list": "search",
                        "srsearch": query,
                        "srlimit": limit
                    },
                    headers=headers
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    results = []
                    
                    for item in search_data.get("query", {}).get("search", []):
                        results.append({
                            "title": item.get("title", ""),
                            "description": item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                            "url": f"https://{language}.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}"
                        })
                    
                    return results
                else:
                    logger.error(f"Wikipedia search API error: {search_response.status_code}")
                    return []
                    
            except Exception as e:
                logger.error(f"Wikipedia search error: {str(e)}")
                return []

# 创建全局实例供其他模块使用
wikipedia_service = WikipediaService() 