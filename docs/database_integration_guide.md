# 数据库集成使用指南

## 概述

本文档介绍如何使用 Fuji Rock 2025 API 的数据库功能，包括艺术家信息管理、歌曲数据存储、AI 描述管理和用户收藏功能。

## 环境配置

### 1. 环境变量设置

在 `.env` 文件中添加 Supabase 配置：

```bash
# Supabase 配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### 2. 安装依赖

```bash
pip install supabase==2.3.0
```

## 核心功能

### 1. 艺术家管理

#### 创建艺术家
```python
# POST /api/database/artists
{
    "name": "Radiohead",
    "name_zh": "电台司令",
    "name_en": "Radiohead",
    "description": "英国摇滚乐队",
    "genres": ["alternative rock", "art rock"],
    "is_fuji_rock_artist": true
}
```

#### 获取艺术家信息
```python
# GET /api/database/artists/{artist_id}
# GET /api/database/artists/by-name/{artist_name}
# GET /api/database/artists/by-spotify/{spotify_id}
```

#### 搜索艺术家
```python
# GET /api/database/artists?query=radiohead&limit=10&offset=0
```

#### 更新艺术家数据
```python
# PUT /api/database/artists/{artist_id}/wikipedia
{
    "wiki_data": {...},
    "wiki_extract": "Wikipedia 摘要文本"
}

# PUT /api/database/artists/{artist_id}/spotify
{
    "spotify_data": {...},
    "spotify_id": "4Z8W4fKeB5YxbusRsdQVPb"
}
```

### 2. 歌曲管理

#### 创建歌曲
```python
# POST /api/database/songs
{
    "artist_id": "uuid-here",
    "title": "Creep",
    "album_name": "Pablo Honey",
    "duration_seconds": 238,
    "preview_url": "https://...",
    "spotify_id": "6b2oQwSGFkzsMtQjfvLdaO"
}
```

#### 批量创建歌曲
```python
# POST /api/database/songs/batch
[
    {
        "artist_id": "uuid-here",
        "title": "Creep",
        ...
    },
    {
        "artist_id": "uuid-here",
        "title": "Karma Police",
        ...
    }
]
```

#### 获取艺术家歌曲
```python
# GET /api/database/artists/{artist_id}/songs?limit=10&offset=0
```

### 3. AI 描述管理

#### 创建 AI 描述
```python
# POST /api/database/ai-descriptions
{
    "artist_id": "uuid-here",
    "content": "AI 生成的毒舌描述",
    "language": "zh",
    "source_content": "Wikipedia 原文",
    "tokens_used": 150,
    "generation_time_ms": 2500
}
```

#### 获取最新 AI 描述
```python
# GET /api/database/artists/{artist_id}/ai-descriptions/latest?language=zh
```

### 4. 用户收藏功能

#### 添加收藏
```python
# POST /api/database/users/{user_id}/favorites
{
    "artist_id": "uuid-here",
    "tags": ["rock", "favorite"],
    "notes": "我最喜欢的乐队"
}
```

#### 获取用户收藏
```python
# GET /api/database/users/{user_id}/favorites?limit=20&offset=0
```

#### 根据标签获取收藏
```python
# GET /api/database/users/{user_id}/favorites/by-tag/rock
```

### 5. 搜索历史

#### 记录搜索
```python
# POST /api/database/search-history
{
    "search_query": "radiohead",
    "search_type": "artist",
    "user_id": "uuid-here",
    "results_count": 5
}
```

#### 获取热门搜索
```python
# GET /api/database/search-history/popular?days=7&limit=10
```

## 集成示例

### 完整艺术家设置流程

使用集成 API 可以一次性完成艺术家的完整设置：

```python
# POST /api/integration/artists/{artist_name}/complete-setup?language=zh&save_to_db=true
```

这个接口会：
1. 检查数据库中是否已存在该艺术家
2. 从 Wikipedia 获取艺术家信息
3. 从 Spotify 获取艺术家和歌曲数据
4. 生成 AI 描述
5. 将所有数据保存到数据库

### 增强艺术家信息获取

```python
# GET /api/integration/artists/{artist_name}/enhanced-info?include_songs=true&include_ai_description=true
```

这个接口会：
- 优先从数据库获取信息
- 如果数据库中没有，则从外部 API 获取
- 组合多个数据源的信息

### 搜索并收藏

```python
# POST /api/integration/users/{user_id}/search-and-favorite?search_query=radiohead&auto_favorite=true
```

这个接口会：
- 搜索艺术家
- 记录搜索历史
- 可选择自动收藏第一个结果

## 数据库操作最佳实践

### 1. 错误处理

所有数据库操作都返回统一的响应格式：

```python
{
    "success": true/false,
    "data": {...},  # 成功时的数据
    "error": "...", # 失败时的错误信息
    "message": "..." # 操作结果描述
}
```

### 2. 数据验证

- 使用 Pydantic 模型进行数据验证
- 自动检查重复数据
- 支持部分更新操作

### 3. 性能优化

- 使用批量操作处理大量数据
- 实现数据库连接池
- 添加适当的索引

### 4. 数据一致性

- 使用事务处理复杂操作
- 实现级联删除
- 定期清理过期数据

## 常见使用场景

### 场景 1：从外部 API 获取数据并存储

```python
# 1. 从 Spotify 获取艺术家信息
spotify_result = await spotify_service.get_artist_by_name("Radiohead")

# 2. 创建艺术家记录
artist_data = CreateArtistRequest(
    name="Radiohead",
    genres=spotify_result["data"]["genres"]
)
artist_result = await artist_db_service.create_artist(artist_data)

# 3. 更新 Spotify 数据
await artist_db_service.update_artist_spotify_data(
    artist_id, 
    spotify_result["data"], 
    spotify_result["data"]["id"]
)
```

### 场景 2：用户搜索和收藏流程

```python
# 1. 搜索艺术家
search_result = await artist_db_service.search_artists("radiohead")

# 2. 记录搜索历史
await user_db_service.record_search(
    search_query="radiohead",
    user_id=user_id,
    results_count=len(search_result["data"])
)

# 3. 用户收藏艺术家
favorite_data = CreateFavoriteRequest(
    artist_id=selected_artist_id,
    tags=["rock", "favorite"]
)
await user_db_service.add_favorite(user_id, favorite_data)
```

### 场景 3：AI 描述生成和存储

```python
# 1. 生成 AI 描述
ai_result = await openai_service.generate_sassy_description(
    artist_name="Radiohead",
    wiki_content=wiki_extract
)

# 2. 存储 AI 描述
ai_desc_data = CreateAIDescriptionRequest(
    artist_id=artist_id,
    content=ai_result["data"]["sassy_description"],
    language="zh",
    tokens_used=ai_result["data"]["tokens_used"]
)
await ai_description_db_service.create_ai_description(ai_desc_data)
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 Supabase 配置是否正确
   - 确认网络连接正常

2. **权限错误**
   - 检查 Service Role Key 是否正确
   - 确认 RLS 策略配置

3. **数据验证错误**
   - 检查请求数据格式
   - 确认必填字段已提供

### 调试技巧

1. 查看日志输出
2. 使用 `/health` 接口检查系统状态
3. 测试数据库连接：`/api/database/test-connection`

## 总结

通过这套数据库集成方案，您可以：

- 高效管理艺术家和歌曲数据
- 实现用户收藏和搜索功能
- 存储和管理 AI 生成的内容
- 分析用户行为和搜索模式
- 构建完整的音乐探索应用

所有接口都遵循 RESTful 设计原则，支持标准的 HTTP 状态码和错误处理，便于前端集成和第三方调用。 