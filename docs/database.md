# Fuji Rock 2025 数据库设计文档

## 概述

本文档为 Fuji Rock 2025 音乐探索工具的数据库设计方案，基于 MVP 需求设计了完整的 Supabase PostgreSQL 数据库结构和对象存储方案。

## 1. 数据库表设计

### 1.1 核心实体关系

```
艺术家 (artists) 
    ├── 歌曲 (songs) [一对多]
    ├── AI描述 (ai_descriptions) [一对多]
    └── 演出信息 (performances) [一对多]

用户 (auth.users) [Supabase内置]
    └── 用户收藏 (user_favorites) [一对多]
```

### 1.2 表结构详细设计

#### 1.2.1 艺术家表 (artists)

存储艺术家的基础信息、Wikipedia 数据和平台关联信息。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY | 主键，自动生成 |
| name | TEXT | NOT NULL | 艺术家名称 |
| name_zh | TEXT | | 中文名称 |
| name_en | TEXT | | 英文名称 |
| name_ja | TEXT | | 日文名称 |
| description | TEXT | | 简短描述 |
| wiki_data | JSONB | | Wikipedia 原始数据 |
| wiki_extract | TEXT | | Wikipedia 摘要文本 |
| wiki_last_updated | TIMESTAMP | | Wikipedia 数据最后更新时间 |
| spotify_id | TEXT | UNIQUE | Spotify 艺术家 ID |
| spotify_data | JSONB | | Spotify 艺术家数据缓存 |
| external_urls | JSONB | | 外部链接 (官网、社交媒体等) |
| genres | TEXT[] | | 音乐风格标签数组 |
| popularity | INTEGER | DEFAULT 0 | 热度评分 (0-100) |
| followers_count | INTEGER | DEFAULT 0 | 粉丝数量 |
| image_url | TEXT | | 主要头像图片 URL |
| images | JSONB | | 多尺寸图片 URLs |
| is_fuji_rock_artist | BOOLEAN | DEFAULT false | 是否为 Fuji Rock 艺术家 |
| search_vector | TSVECTOR | | 全文搜索向量 |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 |

#### 1.2.2 歌曲表 (songs)

存储艺术家的热门歌曲和平台链接信息。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY | 主键，自动生成 |
| artist_id | UUID | REFERENCES artists(id) | 关联艺术家 |
| title | TEXT | NOT NULL | 歌曲标题 |
| album_name | TEXT | | 专辑名称 |
| duration_seconds | INTEGER | | 歌曲时长(秒) |
| preview_url | TEXT | | 预览音频 URL |
| spotify_id | TEXT | UNIQUE | Spotify 歌曲 ID |
| spotify_data | JSONB | | Spotify 歌曲完整数据 |
| itunes_data | JSONB | | iTunes 搜索结果数据 |
| release_date | DATE | | 发行日期 |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 |

#### 1.2.3 AI描述表 (ai_descriptions)

存储 AI 生成的毒舌风格艺术家介绍，支持版本管理。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY | 主键，自动生成 |
| artist_id | UUID | REFERENCES artists(id) | 关联艺术家 |
| content | TEXT | NOT NULL | AI 生成的描述内容 |
| language | TEXT | DEFAULT 'zh' | 语言代码 |
| prompt_template | TEXT | | 使用的提示模板 |
| source_content | TEXT | | 源内容 (Wikipedia 摘要) |
| tokens_used | INTEGER | | 消耗的 token 数量 |
| generation_time_ms | INTEGER | | 生成耗时 |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 |

#### 1.2.4 用户收藏表 (user_favorites)

存储用户收藏的艺术家，支持本地收藏功能的云端同步。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY | 主键，自动生成 |
| user_id | UUID | REFERENCES auth.users(id) | 关联用户 |
| artist_id | UUID | REFERENCES artists(id) | 关联艺术家 |
| tags | TEXT[] | | 用户自定义标签 |
| notes | TEXT | | 用户备注 |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | 收藏时间 |

#### 1.2.5 演出信息表 (performances)

存储 Fuji Rock 2025 的演出安排信息。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY | 主键，自动生成 |
| artist_id | UUID | REFERENCES artists(id) | 关联艺术家 |
| stage_name | TEXT | NOT NULL | 舞台名称 |
| performance_date | DATE | NOT NULL | 演出日期 |
| start_time | TIME | NOT NULL | 开始时间 |
| end_time | TIME | | 结束时间 |
| duration_minutes | INTEGER | | 演出时长(分钟) |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 |

#### 1.2.6 搜索历史表 (search_history)

存储用户搜索历史，用于优化搜索体验。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY | 主键，自动生成 |
| user_id | UUID | REFERENCES auth.users(id) | 关联用户 (可为空) |
| search_query | TEXT | NOT NULL | 搜索关键词 |
| search_type | TEXT | DEFAULT 'artist' | 搜索类型 |
| results_count | INTEGER | DEFAULT 0 | 结果数量 |
| clicked_result_id | UUID | | 点击的结果 ID |
| session_id | TEXT | | 会话 ID |
| ip_address | INET | | IP 地址 |
| user_agent | TEXT | | 用户代理 |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | 搜索时间 |

## 2. SQL 建表语句

### 2.1 启用必要的扩展

```sql
-- 启用 UUID 生成扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 启用全文搜索扩展
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### 2.2 创建表结构

```sql
-- 艺术家表
CREATE TABLE artists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    name_zh TEXT,
    name_en TEXT,
    name_ja TEXT,
    description TEXT,
    wiki_data JSONB,
    wiki_extract TEXT,
    wiki_last_updated TIMESTAMP WITH TIME ZONE,
    spotify_id TEXT UNIQUE,
    spotify_data JSONB,
    external_urls JSONB,
    genres TEXT[],
    popularity INTEGER DEFAULT 0 CHECK (popularity >= 0 AND popularity <= 100),
    followers_count INTEGER DEFAULT 0 CHECK (followers_count >= 0),
    image_url TEXT,
    images JSONB,
    is_fuji_rock_artist BOOLEAN DEFAULT false,
    search_vector TSVECTOR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 歌曲表
CREATE TABLE songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    album_name TEXT,
    duration_seconds INTEGER CHECK (duration_seconds > 0),
    preview_url TEXT,
    spotify_id TEXT UNIQUE,
    spotify_data JSONB,
    itunes_data JSONB,
    release_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI描述表
CREATE TABLE ai_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    language TEXT DEFAULT 'zh' CHECK (language IN ('zh', 'en', 'ja', 'ko')),
    prompt_template TEXT,
    source_content TEXT,
    tokens_used INTEGER CHECK (tokens_used > 0),
    generation_time_ms INTEGER CHECK (generation_time_ms > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户收藏表
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, artist_id)
);

-- 演出信息表
CREATE TABLE performances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    stage_name TEXT NOT NULL,
    performance_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    duration_minutes INTEGER CHECK (duration_minutes > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 搜索历史表
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    search_query TEXT NOT NULL,
    search_type TEXT DEFAULT 'artist' CHECK (search_type IN ('artist', 'song', 'general')),
    results_count INTEGER DEFAULT 0 CHECK (results_count >= 0),
    clicked_result_id UUID,
    session_id TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.3 创建索引

```sql
-- 艺术家表索引
CREATE INDEX idx_artists_name ON artists USING gin(name gin_trgm_ops);
CREATE INDEX idx_artists_name_zh ON artists USING gin(name_zh gin_trgm_ops);
CREATE INDEX idx_artists_name_en ON artists USING gin(name_en gin_trgm_ops);
CREATE INDEX idx_artists_spotify_id ON artists(spotify_id);
CREATE INDEX idx_artists_popularity ON artists(popularity DESC);
CREATE INDEX idx_artists_fuji_rock ON artists(is_fuji_rock_artist) WHERE is_fuji_rock_artist = true;
CREATE INDEX idx_artists_search_vector ON artists USING gin(search_vector);
CREATE INDEX idx_artists_genres ON artists USING gin(genres);

-- 歌曲表索引
CREATE INDEX idx_songs_artist_id ON songs(artist_id);
CREATE INDEX idx_songs_title ON songs USING gin(title gin_trgm_ops);
CREATE INDEX idx_songs_spotify_id ON songs(spotify_id);
CREATE INDEX idx_songs_artist_duration ON songs(artist_id, duration_seconds DESC);

-- AI描述表索引
CREATE INDEX idx_ai_descriptions_artist_id ON ai_descriptions(artist_id);
CREATE INDEX idx_ai_descriptions_language ON ai_descriptions(language);

-- 用户收藏表索引
CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_artist_id ON user_favorites(artist_id);
CREATE INDEX idx_user_favorites_created_at ON user_favorites(created_at DESC);

-- 演出信息表索引
CREATE INDEX idx_performances_artist_id ON performances(artist_id);
CREATE INDEX idx_performances_date ON performances(performance_date);
CREATE INDEX idx_performances_stage ON performances(stage_name);
CREATE INDEX idx_performances_time ON performances(performance_date, start_time);

-- 搜索历史表索引
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_query ON search_history USING gin(search_query gin_trgm_ops);
CREATE INDEX idx_search_history_created_at ON search_history(created_at DESC);
CREATE INDEX idx_search_history_session ON search_history(session_id);
```

### 2.4 创建触发器和函数

```sql
-- 更新时间戳函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间戳触发器
CREATE TRIGGER update_artists_updated_at BEFORE UPDATE ON artists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_songs_updated_at BEFORE UPDATE ON songs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performances_updated_at BEFORE UPDATE ON performances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 搜索向量更新函数
CREATE OR REPLACE FUNCTION update_artist_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('simple', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.name_zh, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.name_en, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.name_ja, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('simple', COALESCE(array_to_string(NEW.genres, ' '), '')), 'B');
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 搜索向量触发器
CREATE TRIGGER update_artist_search_vector_trigger 
    BEFORE INSERT OR UPDATE ON artists
    FOR EACH ROW EXECUTE FUNCTION update_artist_search_vector();
```

### 2.5 行级安全策略 (RLS)

```sql
-- 启用行级安全
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;

-- 用户收藏策略：用户只能访问自己的收藏
CREATE POLICY "Users can view own favorites" ON user_favorites
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own favorites" ON user_favorites
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own favorites" ON user_favorites
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own favorites" ON user_favorites
    FOR DELETE USING (auth.uid() = user_id);

-- 搜索历史策略：用户只能访问自己的搜索历史
CREATE POLICY "Users can view own search history" ON search_history
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert own search history" ON search_history
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);
```

## 3. Supabase Storage 对象存储设计

### 3.1 Bucket 结构

```sql
-- 创建存储桶
INSERT INTO storage.buckets (id, name, public) VALUES 
    ('artist-images', 'artist-images', true),
    ('album-covers', 'album-covers', true),
    ('user-uploads', 'user-uploads', false);
```

### 3.2 存储桶组织结构

#### 3.2.1 艺术家图片存储 (artist-images)

```
artist-images/
├── avatars/
│   ├── {artist_id}/
│   │   ├── original.jpg          # 原始高清图片
│   │   ├── large.jpg            # 大尺寸 (640x640)
│   │   ├── medium.jpg           # 中等尺寸 (320x320)
│   │   └── small.jpg            # 小尺寸 (160x160)
├── banners/
│   └── {artist_id}/
│       ├── desktop.jpg          # 桌面端横幅 (1920x600)
│       └── mobile.jpg           # 移动端横幅 (750x300)
└── gallery/
    └── {artist_id}/
        ├── photo_1.jpg          # 艺术家相册图片
        ├── photo_2.jpg
        └── ...
```

#### 3.2.2 专辑封面存储 (album-covers)

```
album-covers/
├── spotify/
│   └── {album_id}/
│       ├── large.jpg            # 640x640
│       ├── medium.jpg           # 320x320
│       └── small.jpg            # 160x160
├── itunes/
│   └── {album_id}/
│       └── cover.jpg
└── custom/
    └── {album_id}/
        └── cover.jpg
```

#### 3.2.3 用户上传内容 (user-uploads)

```
user-uploads/
├── {user_id}/
│   ├── avatars/
│   │   └── avatar.jpg           # 用户头像
│   ├── playlists/
│   │   └── {playlist_id}/
│   │       └── cover.jpg        # 自定义播放列表封面
│   └── notes/
│       └── {note_id}/
│           ├── image_1.jpg      # 笔记附图
│           └── image_2.jpg
```

### 3.3 存储策略配置

```sql
-- 艺术家图片存储策略 (公开访问)
CREATE POLICY "Artist images are publicly accessible" ON storage.objects
    FOR SELECT USING (bucket_id = 'artist-images');

CREATE POLICY "Service role can manage artist images" ON storage.objects
    FOR ALL USING (bucket_id = 'artist-images' AND auth.role() = 'service_role');

-- 专辑封面存储策略 (公开访问)
CREATE POLICY "Album covers are publicly accessible" ON storage.objects
    FOR SELECT USING (bucket_id = 'album-covers');

CREATE POLICY "Service role can manage album covers" ON storage.objects
    FOR ALL USING (bucket_id = 'album-covers' AND auth.role() = 'service_role');

-- 用户上传内容策略 (私有访问)
CREATE POLICY "Users can view own uploads" ON storage.objects
    FOR SELECT USING (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can upload own content" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can update own uploads" ON storage.objects
    FOR UPDATE USING (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own uploads" ON storage.objects
    FOR DELETE USING (bucket_id = 'user-uploads' AND auth.uid()::text = (storage.foldername(name))[1]);
```

### 3.4 文件命名规范

#### 3.4.1 艺术家图片命名

```
格式：{type}/{artist_id}/{size}.{ext}
示例：
- avatars/550e8400-e29b-41d4-a716-446655440000/original.jpg
- banners/550e8400-e29b-41d4-a716-446655440000/desktop.jpg
```

#### 3.4.2 专辑封面命名

```
格式：{platform}/{album_id}/{size}.{ext}
示例：
- spotify/4aawyAB9vmqN3uQ7FjRGTy/large.jpg
- itunes/1234567890/cover.jpg
```

#### 3.4.3 用户上传文件命名

```
格式：{user_id}/{category}/{item_id}/{filename}.{ext}
示例：
- 123e4567-e89b-12d3-a456-426614174000/avatars/avatar.jpg
- 123e4567-e89b-12d3-a456-426614174000/playlists/my-playlist-1/cover.jpg
```

## 4. 数据库性能优化建议

### 4.1 查询优化

1. **艺术家搜索优化**
   - 使用 GIN 索引支持模糊搜索
   - 实现搜索结果缓存
   - 使用全文搜索向量提升搜索质量

2. **热门内容缓存**
   - 缓存热门艺术家列表
   - 缓存 Fuji Rock 演出时间表
   - 缓存用户收藏统计

3. **分页查询优化**
   - 使用游标分页替代 OFFSET
   - 预加载关联数据减少 N+1 查询

### 4.2 数据维护

1. **定期清理**
   - 清理过期的搜索历史
   - 清理未使用的 AI 描述版本
   - 压缩历史数据

2. **数据同步**
   - 定期同步 Spotify 数据
   - 更新 Wikipedia 内容
   - 刷新艺术家热度排名

## 5. 部署和初始化

### 5.1 初始化脚本

```sql
-- 创建初始化函数
CREATE OR REPLACE FUNCTION initialize_fuji_rock_database()
RETURNS void AS $$
BEGIN
    -- 插入示例数据可以在这里添加
    RAISE NOTICE 'Fuji Rock 2025 database initialized successfully!';
END;
$$ LANGUAGE plpgsql;

-- 执行初始化
SELECT initialize_fuji_rock_database();
```

### 5.2 数据迁移考虑

1. **版本控制**
   - 使用 Supabase 迁移功能
   - 保持向后兼容性
   - 记录所有结构变更

2. **数据备份**
   - 定期备份关键数据
   - 测试恢复流程
   - 监控数据完整性

这个数据库设计支持 MVP 的所有核心功能，包括艺术家信息管理、AI 内容生成、用户收藏、搜索功能和 Fuji Rock 演出信息管理。设计考虑了性能、安全性和可扩展性，为后续功能扩展预留了充足空间。 