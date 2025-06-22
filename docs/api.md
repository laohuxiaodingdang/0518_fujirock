# Fuji Rock 2025 API 接口文档

## 概述

Fuji Rock 2025 音乐探索工具的 RESTful API 文档。本 API 提供艺术家信息查询、AI 生成内容和音乐播放等功能。

**基础信息：**
- 基础 URL: `http://localhost:8000`
- API 版本: `v1.0.0`
- 文档格式: OpenAPI 3.0
- 交互式文档: `/docs` (Swagger UI) 和 `/redoc` (ReDoc)

## 认证

### API 认证
- 部分接口需要 API Key
- 在请求头中添加: `Authorization: Bearer <token>`

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体数据内容
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": "error_code",
  "message": "错误描述",
  "details": "详细错误信息"
}
```

## API 端点

### 1. 系统健康检查

#### 1.1 健康检查
```http
GET /health
```

**响应示例：**
```json
{
  "status": "healthy",
  "environment": "development",
  "apis": {
    "wikipedia": "real",
    "deepseek": "mock",
    "spotify": "real"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 1.2 系统状态
```http
GET /status
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "app_name": "Fuji Rock 2025 API",
    "app_version": "1.0.0",
    "environment": "development",
    "api_keys": {
      "deepseek": true,
      "spotify": true,
      "wikipedia": true
    }
  }
}
```

### 2. Wikipedia API

#### 2.1 获取艺术家信息
```http
GET /api/wikipedia/artists/{artist_name}
```

**参数：**
- `artist_name` (path): 艺术家名称
- `language` (query): 语言代码 (zh/en/ja/ko)，默认 zh

**响应示例：**
```json
{
  "success": true,
  "data": {
    "title": "Radiohead",
    "extract": "Radiohead are an English rock band...",
    "thumbnail": {
      "source": "https://example.com/image.jpg",
      "width": 800,
      "height": 600
    },
    "categories": ["Rock", "Alternative"],
    "references": [
      {
        "title": "Official Website",
        "url": "https://radiohead.com"
      }
    ]
  }
}
```

#### 2.2 搜索艺术家
```http
GET /api/wikipedia/search
```

**参数：**
- `query` (query): 搜索关键词
- `language` (query): 语言代码，默认 zh
- `limit` (query): 结果数量限制 (1-50)，默认 10

### 3. DeepSeek AI API

#### 3.1 生成艺术家介绍
```http
POST /api/ai/generate-description
```

**请求体：**
```json
{
  "artist_name": "Radiohead",
  "wiki_content": "Radiohead are an English rock band...",
  "style_intensity": 8,
  "language": "zh",
  "max_length": 500,
  "temperature": 0.7
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "original_content": "Radiohead are an English rock band...",
    "sassy_description": "这支来自英国的乐队，以其独特的音乐风格著称...",
    "style_metrics": {
      "humor_level": 7,
      "sarcasm_level": 5,
      "fact_accuracy": 0.9
    },
    "tokens_used": 150
  }
}
```

#### 3.2 流式生成介绍
```http
POST /api/ai/generate-description-stream
```

**返回：** Server-Sent Events (SSE) 流

#### 3.3 情感分析
```http
POST /api/ai/analyze-sentiment
```

**请求体：**
```json
{
  "text": "这首歌真的很棒，让人心情愉悦！"
}
```

### 4. Spotify API

#### 4.1 获取艺术家信息
```http
GET /api/spotify/artists/{spotify_id}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "id": "4Z8W4fKeB5YxbusRsdQVPb",
    "name": "Radiohead",
    "genres": ["alternative rock", "art rock"],
    "popularity": 85,
    "followers": {"total": 4500000},
    "images": [
      {
        "url": "https://i.scdn.co/image/example",
        "height": 640,
        "width": 640
      }
    ]
  }
}
```

#### 4.2 获取热门曲目
```http
GET /api/spotify/artists/{spotify_id}/top-tracks
```

**参数：**
- `limit` (query): 曲目数量 (1-50)，默认 10
- `market` (query): 市场代码，默认 JP

#### 4.3 通过名称获取艺术家
```http
GET /api/spotify/artist-by-name/{artist_name}
```

#### 4.4 搜索艺术家
```http
GET /api/spotify/search
```

**参数：**
- `query` (query): 搜索关键词
- `limit` (query): 结果数量 (1-50)
- `market` (query): 市场代码

#### 4.5 通过名称获取热门曲目
```http
GET /api/spotify/artist-by-name/{artist_name}/top-tracks
```

**参数：**
- `limit` (query): 曲目数量 (1-50)，默认 10
- `market` (query): 市场代码，默认 JP

#### 4.6 创建播放列表
```http
POST /api/spotify/artists/{spotify_id}/create-playlist
```

**请求体：**
```json
{
  "playlist_name": "My Radiohead Playlist",
  "description": "Best tracks from Radiohead",
  "public": true
}
```

### 5. iTunes API

#### 5.1 搜索歌曲
```http
GET /api/itunes/search-track
```

**参数：**
- `artist` (query): 艺术家名称
- `track` (query): 歌曲名称
- `limit` (query): 结果数量，默认 5

#### 5.2 获取艺术家歌曲
```http
GET /api/itunes/artist-tracks
```

**参数：**
- `artist` (query): 艺术家名称
- `limit` (query): 结果数量，默认 10

#### 5.3 组合预览
```http
GET /api/spotify/track-with-itunes-preview
```

**参数：**
- `artist` (query): 艺术家名称
- `track` (query): 歌曲名称

**响应示例：**
```json
{
  "spotify_preview_available": false,
  "itunes_preview_available": true,
  "preview_url": "https://audio-ssl.itunes.apple.com/example.m4a",
  "preview_source": "iTunes",
  "track_info": {
    "artist": "Radiohead",
    "track": "Creep"
  },
  "itunes_info": {
    "trackName": "Creep",
    "artistName": "Radiohead",
    "collectionName": "Pablo Honey",
    "previewUrl": "https://audio-ssl.itunes.apple.com/example.m4a"
  }
}
```

## 错误代码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数无效 |
| 401 | Unauthorized | 认证失败 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源未找到 |
| 408 | Request Timeout | 请求超时 |
| 429 | Too Many Requests | 请求频率限制 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

## 速率限制

- 默认限制：每分钟 60 次请求
- AI 生成接口：每分钟 10 次请求
- Spotify API：每分钟 100 次请求
- iTunes API：每分钟 200 次请求

## 示例代码

### JavaScript/TypeScript
```typescript
// 获取艺术家信息
const response = await fetch('/api/wikipedia/artists/Radiohead?language=zh');
const data = await response.json();

// 生成 AI 描述
const aiResponse = await fetch('/api/ai/generate-description', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    artist_name: 'Radiohead',
    wiki_content: 'Wikipedia content...',
    style_intensity: 8
  })
});

// 获取 Spotify 艺术家信息
const spotifyResponse = await fetch('/api/spotify/artist-by-name/Radiohead');
const spotifyData = await spotifyResponse.json();

// 获取音乐预览
const previewResponse = await fetch('/api/spotify/track-with-itunes-preview?artist=Radiohead&track=Creep');
const previewData = await previewResponse.json();
```

### Python
```python
import httpx

# 获取艺术家信息
async with httpx.AsyncClient() as client:
    response = await client.get('/api/wikipedia/artists/Radiohead')
    data = response.json()
    
    # 生成 AI 描述
    ai_response = await client.post('/api/ai/generate-description', json={
        'artist_name': 'Radiohead',
        'wiki_content': data['data']['extract'],
        'style_intensity': 8
    })
    ai_data = ai_response.json()
```

### cURL
```bash
# 获取艺术家信息
curl -X GET "http://localhost:8000/api/wikipedia/artists/Radiohead?language=zh"

# 生成 AI 描述
curl -X POST "http://localhost:8000/api/ai/generate-description" \
  -H "Content-Type: application/json" \
  -d '{"artist_name": "Radiohead", "wiki_content": "...", "style_intensity": 8}'

# 获取音乐预览
curl -X GET "http://localhost:8000/api/spotify/track-with-itunes-preview?artist=Radiohead&track=Creep"
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- Wikipedia API 集成
- DeepSeek AI API 集成
- Spotify API 集成
- iTunes API 集成
- 音乐预览功能

## 支持

如有问题或建议，请联系开发团队或查看项目文档。 