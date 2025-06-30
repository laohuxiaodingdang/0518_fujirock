# Fuji Rock 2025 音乐探索工具 API

这是一个基于 FastAPI 的音乐探索工具，为 Fuji Rock 2025 音乐节提供艺术家信息查询和个性化介绍生成功能。

## 功能特性

- **Wikipedia 集成**: 获取艺术家基本信息
- **OpenAI 集成**: 生成毒舌风格的艺术家介绍
- **Spotify 集成**: 获取艺术家信息、热门歌曲和创建播放列表

## 快速开始

### 1. 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python3 -m uvicorn main:app --reload
```

### 3. 访问 API 文档

服务器启动后，你可以访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### Wikipedia API
- `GET /api/artists/{artist_name}/wiki` - 获取艺术家 Wikipedia 信息

### OpenAI API
- `POST /api/ai/generate-description` - 生成毒舌风格介绍

### Spotify API
- `GET /api/artists/{spotify_id}/spotify` - 获取 Spotify 艺术家信息
- `GET /api/artists/{spotify_id}/top-tracks` - 获取艺术家热门歌曲
- `POST /api/artists/{spotify_id}/playlist` - 创建艺术家播放列表

## 使用示例

### 获取艺术家 Wikipedia 信息
```bash
curl http://localhost:8000/api/artists/Radiohead/wiki
```

### 生成毒舌风格介绍
```bash
curl -X POST http://localhost:8000/api/ai/generate-description \
  -H "Content-Type: application/json" \
  -d '{"wiki_content": "Some content", "style_intensity": 7}'
```

### 获取 Spotify 艺术家信息
```bash
curl http://localhost:8000/api/artists/123456/spotify
```

## 环境变量配置

创建 `.env` 文件并添加以下配置：

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Spotify API Configuration
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Wikipedia API Configuration
WIKIPEDIA_API_URL=https://zh.wikipedia.org/api/rest_v1
```

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI 服务器
- **python-dotenv**: 环境变量管理

## 注意事项

- 当前版本使用 mock 数据进行演示
- 实际部署时需要配置真实的 API 密钥
- 所有 API 响应都遵循统一的格式规范
# Trigger redeploy Mon Jun 30 09:51:50 CST 2025
