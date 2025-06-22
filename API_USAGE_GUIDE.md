# Fuji Rock 2025 API 使用指南

## 概述

Fuji Rock 2025 API 是一个音乐探索工具，集成了 Wikipedia、DeepSeek AI 和 Spotify API，为 Fuji Rock 音乐节提供艺术家信息和毒舌风格的介绍。

## 快速开始

### 1. 启动应用

**推荐方式（适用于所有环境）：**
```bash
# 使用 Python 模块方式启动（推荐）
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**如果 uvicorn 命令可用：**
```bash
# 直接使用 uvicorn 命令
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**如果遇到 "command not found: uvicorn" 错误：**

这是因为 uvicorn 可执行文件不在系统 PATH 中。解决方案：

1. **使用 Python 模块方式（推荐）：**
   ```bash
   python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **使用虚拟环境：**
   ```bash
   # 创建并激活虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 现在可以直接使用 uvicorn
   uvicorn main:app --reload
   ```

3. **检查安装状态：**
   ```bash
   # 检查 uvicorn 是否已安装
   pip3 list | grep uvicorn
   
   # 如果未安装，手动安装
   pip3 install uvicorn[standard]
   ```

### 2. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API 端点

### Wikipedia API

#### 获取艺术家信息
```http
GET /api/wikipedia/artists/{artist_name}?language=zh
```

**参数:**
- `artist_name`: 艺术家名称（路径参数）
- `language`: 语言代码 (zh/en/ja/ko)，默认为 zh

**示例:**
```bash
curl "http://localhost:8000/api/wikipedia/artists/Radiohead?language=en"
```

#### 搜索艺术家
```http
GET /api/wikipedia/search?query=radiohead&language=zh&limit=10
```

**参数:**
- `query`: 搜索关键词
- `language`: 语言代码，默认为 zh
- `limit`: 返回数量限制 (1-50)，默认为 10

### DeepSeek AI API

#### 生成毒舌风格介绍
```http
POST /api/ai/generate-description
Content-Type: application/json

{
  "wiki_content": "Radiohead are an English rock band...",
  "style_intensity": 5,
  "language": "zh",
  "max_length": 500,
  "temperature": 0.8
}
```

**参数:**
- `wiki_content`: Wikipedia 内容（必需，最少10字符）
- `style_intensity`: 毒舌程度 (1-10)，数值越高越犀利
- `language`: 输出语言 (zh/en/ja/ko)，默认为 zh
- `max_length`: 最大输出长度 (100-2000)，默认为 500
- `temperature`: 创造性程度 (0.0-2.0)，默认为 0.8

#### 分析文本情感
```http
POST /api/ai/analyze-sentiment
Content-Type: application/json

"这首歌真的很棒，让人心情愉悦！"
```

#### 获取服务状态
```http
GET /api/ai/status
```

#### 获取使用统计
```http
GET /api/ai/usage-stats
```

### Spotify API

#### 获取艺术家信息
```http
GET /api/spotify/artists/{spotify_id}
```

**参数:**
- `spotify_id`: Spotify 艺术家 ID

**示例:**
```bash
curl "http://localhost:8000/api/spotify/artists/4Z8W4fKeB5YxbusRsdQVPb"
```

#### 获取热门曲目
```http
GET /api/spotify/artists/{spotify_id}/top-tracks?limit=10&market=JP
```

**参数:**
- `spotify_id`: Spotify 艺术家 ID
- `limit`: 返回数量限制 (1-50)，默认为 10
- `market`: 市场代码，默认为 JP

#### 创建播放列表
```http
POST /api/spotify/artists/{spotify_id}/create-playlist
Content-Type: application/json

{
  "playlist_name": "My Radiohead Playlist",
  "description": "Best tracks from Radiohead",
  "public": true
}
```

#### 搜索艺术家
```http
GET /api/spotify/search?query=radiohead&limit=10&market=JP
```

#### 获取服务状态
```http
GET /api/spotify/status
```

## 环境配置

### 开发环境 vs 生产环境

应用根据 `ENVIRONMENT` 环境变量自动切换数据源：

- **开发环境** (`ENVIRONMENT=development`): 使用 Mock 数据
- **生产环境** (`ENVIRONMENT=production`): 使用真实 API

### 环境变量配置

复制 `env.example` 文件为 `.env` 并配置以下变量：

```bash
# 应用配置
ENVIRONMENT=development  # 或 production
DEBUG=true
PORT=8000

# API 密钥（生产环境必需）
ARK_API_KEY=your_ark_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# DeepSeek AI 配置
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=1000
DEEPSEEK_TEMPERATURE=0.8

# 其他配置
HTTP_TIMEOUT=30.0
LOG_LEVEL=INFO
```

## 响应格式

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
  "detail": {
    "error": "错误类型",
    "message": "详细错误信息",
    "service": "相关服务",
    "details": "技术细节"
  }
}
```

## 错误处理

### 常见错误码

- **400**: 请求参数无效
- **401**: API 密钥无效或未配置
- **404**: 资源未找到
- **408**: 请求超时
- **429**: API 调用频率限制
- **500**: 内部服务器错误
- **503**: 外部服务不可用

### 重试策略

- 对于 `408` (超时) 和 `503` (服务不可用) 错误，建议实施指数退避重试
- 对于 `429` (频率限制) 错误，请根据 `retry-after` 头部等待

## 使用示例

### 完整工作流程

```bash
# 1. 检查服务健康状态
curl "http://localhost:8000/health"

# 2. 搜索艺术家
curl "http://localhost:8000/api/wikipedia/search?query=radiohead"

# 3. 获取 Wikipedia 信息
curl "http://localhost:8000/api/wikipedia/artists/Radiohead"

# 4. 生成毒舌介绍
curl -X POST "http://localhost:8000/api/ai/generate-description" \
  -H "Content-Type: application/json" \
  -d '{
    "wiki_content": "Radiohead are an English rock band formed in Abingdon, Oxfordshire, in 1985.",
    "style_intensity": 7,
    "language": "zh"
  }'

# 5. 获取 Spotify 信息
curl "http://localhost:8000/api/spotify/artists/4Z8W4fKeB5YxbusRsdQVPb"

# 6. 获取热门曲目
curl "http://localhost:8000/api/spotify/artists/4Z8W4fKeB5YxbusRsdQVPb/top-tracks"
```

## 开发注意事项

### CORS 支持

API 已配置 CORS 支持，允许跨域请求。生产环境中建议配置具体的允许域名。

### 日志记录

应用使用结构化日志记录，可通过 `LOG_LEVEL` 环境变量调整日志级别。

### 性能优化

- 使用异步 HTTP 客户端 (`httpx.AsyncClient`)
- 实施连接池和超时控制
- Spotify API 访问令牌自动缓存和刷新

### 扩展功能

- 支持多语言输出
- 可配置的毒舌程度
- 情感分析功能
- 使用统计追踪

## 故障排除

### 常见问题

1. **应用启动失败**
   - 检查 Python 版本 (需要 3.8+)
   - 确认所有依赖已安装: `pip install -r requirements.txt`

2. **API 调用失败**
   - 检查环境变量配置
   - 验证 API 密钥有效性
   - 查看应用日志获取详细错误信息

3. **Mock 数据 vs 真实数据**
   - 开发环境默认使用 Mock 数据
   - 设置 `ENVIRONMENT=production` 使用真实 API

### 获取帮助

- 查看 Swagger 文档: http://localhost:8000/docs
- 检查应用日志
- 使用健康检查端点诊断服务状态 