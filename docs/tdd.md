# Fuji Rock 2025 音乐探索工具 - 第三方 API 集成技术设计文档

## 1. Wikipedia API 集成

### 1.1 获取艺术家基本信息
- **接口名称**: `getArtistWikiInfo`
- **请求路径**: `GET /api/artists/{artist_name}/wiki`
- **请求参数**:
  ```json
  {
    "artist_name": "string",  // 艺术家名称
    "language": "string"      // 可选，默认 "zh"，支持 "en"
  }
  ```
- **依赖服务**: Wikipedia API
- **示例返回**:
  ```json
  {
    "success": true,
    "data": {
      "title": "艺术家名称",
      "extract": "艺术家简介",
      "thumbnail": {
        "source": "图片URL",
        "width": 800,
        "height": 600
      },
      "categories": ["音乐家", "摇滚乐", "日本音乐"],
      "references": [
        {
          "title": "参考来源标题",
          "url": "参考来源URL"
        }
      ]
    }
  }
  ```

## 2. OpenAI API 集成

### 2.1 生成毒舌风格介绍
- **接口名称**: `generateSassyDescription`
- **请求路径**: `POST /api/ai/generate-description`
- **请求参数**:
  ```json
  {
    "wiki_content": "string",     // Wikipedia 原始内容
    "style_intensity": "number",  // 毒舌程度，1-10
    "language": "string",         // 输出语言，默认 "zh"
    "max_length": "number"        // 最大长度，默认 500
  }
  ```
- **依赖服务**: OpenAI API (GPT-4)
- **示例返回**:
  ```json
  {
    "success": true,
    "data": {
      "original_content": "原始Wikipedia内容",
      "sassy_description": "毒舌风格介绍",
      "style_metrics": {
        "humor_level": 8,
        "sarcasm_level": 7,
        "fact_accuracy": 0.95
      },
      "generated_at": "2024-05-18T10:00:00Z"
    }
  }
  ```

## 3. Spotify API 集成

### 3.1 获取艺术家信息
- **接口名称**: `getArtistSpotifyInfo`
- **请求路径**: `GET /api/artists/{spotify_id}/spotify`
- **请求参数**:
  ```json
  {
    "spotify_id": "string"  // Spotify 艺术家 ID
  }
  ```
- **依赖服务**: Spotify Web API
- **示例返回**:
  ```json
  {
    "success": true,
    "data": {
      "id": "spotify_artist_id",
      "name": "艺术家名称",
      "images": [
        {
          "url": "图片URL",
          "height": 640,
          "width": 640
        }
      ],
      "genres": ["摇滚", "另类摇滚", "独立摇滚"],
      "popularity": 85,
      "followers": {
        "total": 1000000
      }
    }
  }
  ```

### 3.2 获取艺术家热门歌曲
- **接口名称**: `getArtistTopTracks`
- **请求路径**: `GET /api/artists/{spotify_id}/top-tracks`
- **请求参数**:
  ```json
  {
    "spotify_id": "string",  // Spotify 艺术家 ID
    "limit": "number",       // 可选，默认 10
    "market": "string"       // 可选，默认 "JP"
  }
  ```
- **依赖服务**: Spotify Web API
- **示例返回**:
  ```json
  {
    "success": true,
    "data": {
      "tracks": [
        {
          "id": "track_id",
          "name": "歌曲名称",
          "album": {
            "id": "album_id",
            "name": "专辑名称",
            "images": [
              {
                "url": "专辑封面URL",
                "height": 640,
                "width": 640
              }
            ]
          },
          "duration_ms": 180000,
          "popularity": 85,
          "preview_url": "预览音频URL"
        }
      ]
    }
  }
  ```

### 3.3 创建播放列表
- **接口名称**: `createArtistPlaylist`
- **请求路径**: `POST /api/artists/{spotify_id}/playlist`
- **请求参数**:
  ```json
  {
    "spotify_id": "string",     // Spotify 艺术家 ID
    "playlist_name": "string",  // 播放列表名称
    "description": "string",    // 播放列表描述
    "public": "boolean"         // 是否公开，默认 false
  }
  ```
- **依赖服务**: Spotify Web API
- **示例返回**:
  ```json
  {
    "success": true,
    "data": {
      "playlist_id": "playlist_id",
      "name": "播放列表名称",
      "description": "播放列表描述",
      "tracks": {
        "total": 20,
        "items": [
          {
            "id": "track_id",
            "name": "歌曲名称",
            "duration_ms": 180000
          }
        ]
      },
      "external_urls": {
        "spotify": "Spotify播放列表URL"
      }
    }
  }
  ```

## 4. 错误处理

所有 API 接口在发生错误时都会返回统一格式的错误响应：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {
      // 可选的详细错误信息
    }
  }
}
```

常见错误代码：
- `WIKI_API_ERROR`: Wikipedia API 调用失败
- `OPENAI_API_ERROR`: OpenAI API 调用失败
- `SPOTIFY_API_ERROR`: Spotify API 调用失败
- `RATE_LIMIT_EXCEEDED`: API 调用频率超限
- `INVALID_PARAMETERS`: 参数验证失败
- `SERVICE_UNAVAILABLE`: 服务暂时不可用 