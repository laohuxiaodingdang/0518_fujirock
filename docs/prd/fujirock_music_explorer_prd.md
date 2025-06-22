---
title: Fuji Rock 2025 音乐探索工具 PRD
description: 帮助 Fuji Rock 2025 票务持有者提前了解即将在音乐节演出的艺术家，提供音乐探索和发现功能
version: 1.0.0
date: 2024-05-18
status: draft
---

# Fuji Rock 2025 音乐探索工具 PRD

## 1. 产品定位
- **目标用户**：Fuji Rock 2025 票务持有者
- **核心价值**：帮助用户提前了解即将在 Fuji Rock 演出的艺术家，提供音乐探索和发现功能
- **使用场景**：用户搜索某位艺术家，获取其生平介绍、作品歌单、相似艺术家推荐等内容

## 2. 核心功能模块

### 2.1 艺术家信息展示
- [MVP] 艺术家生平介绍
  - 使用 Wikipedia API 获取基础信息
  - AI 将 Wikipedia 内容转化为毒舌风格
  - 保留关键事实信息
  - 添加趣味性解读
  - 标注信息来源
- [MVP] 热门歌曲/代表作品（Spotify）
- 社交媒体链接
- 艺术家八卦
- [MVP] 基础演出信息
- 演出时间表
- 演出舞台位置

### 2.2 音乐播放
- [MVP] Spotify 平台接入
- [MVP] Spotify 登录功能
- [MVP] 播放列表创建和播放
- 后续接入其他平台：
  - 网易云音乐
  - QQ音乐
  - Apple Music

### 2.3 相似艺术家推荐
- 基于音乐风格的推荐
- 基于八卦的趣味推荐
- 推荐 5 个左右相似艺术家
- 提供推荐理由说明

### 2.4 用户功能
- [MVP] 收藏/标记功能（本地存储）
- [MVP] 基础搜索功能
- 分享功能
- 云端数据同步

## 3. 用户流程
1. 首页展示：
   - [MVP] 艺术家列表展示
   - [MVP] 搜索框
   - [MVP] 基础分类导航
   - 基于星座运势随机展示
   - 高级分类筛选

2. 艺术家详情页：
   - [MVP] Wikipedia 数据展示
   - [MVP] AI 毒舌风格介绍
   - [MVP] Spotify 歌单
   - [MVP] 收藏功能
   - 社交媒体链接
   - 艺术家八卦
   - 相似艺术家推荐
   - 分享功能

## 4. 非功能需求
- [MVP] 页面加载速度：3秒内
- [MVP] 本地数据存储
- [MVP] Spotify 登录信息安全存储
- 云端数据同步
- 多设备支持
- 离线访问支持

## 5. 技术实现
- [MVP] Wikipedia API 集成
- [MVP] AI 风格转换（基于 Wikipedia 数据）
- [MVP] Spotify API 接入
- [MVP] 本地数据存储
- 多平台流媒体接入
- 云端数据同步
- 离线功能支持

## 6. 设计风格要求

### 6.1 整体风格
- 参考 aespa 的 Whiplash MV 风格
- 未来感、科技感、赛博朋克元素
- 极简但富有视觉冲击力

### 6.2 具体设计元素
- **配色方案**：
  - 主色调：霓虹蓝、霓虹粉
  - 辅助色：深空灰、纯黑
  - 强调色：荧光绿、霓虹紫
  - 渐变效果：类似 MV 中的光效渐变

- **字体选择**：
  - 标题：科技感无衬线字体
  - 正文：清晰易读的现代字体
  - 强调文字：可考虑使用霓虹灯效果

- **界面元素**：
  - 卡片式设计，带有玻璃态效果
  - 动态光效边框
  - 悬浮效果带有霓虹光晕
  - 按钮和交互元素带有科技感动画

- **动画效果**：
  - 页面切换时的流畅过渡
  - 元素出现时的科技感动画
  - 鼠标悬停时的光效反馈
  - 加载动画带有未来感

### 6.3 响应式设计
- 适配各种设备尺寸
- 保持科技感的同时确保可用性
- 移动端优化，确保流畅体验

### 6.4 交互设计
- 流畅的滚动效果
- 科技感的页面切换
- 富有未来感的加载状态
- 创新的导航方式

## 7. 技术栈

### 7.1 前端技术
- **框架**：React/Next.js
- **样式**：Tailwind CSS + Framer Motion
- **状态管理**：React Query + Zustand
- **UI组件**：Shadcn/ui
- **API客户端**：Axios

### 7.2 后端技术
- **框架**：FastAPI
- **语言**：Python 3.11+
- **API文档**：Swagger/OpenAPI
- **认证**：JWT
- **任务队列**：Celery（用于异步任务）

### 7.3 数据库
- **主数据库**：Supabase（PostgreSQL）
- **缓存**：Redis
- **本地存储**：IndexedDB

### 7.4 第三方服务集成
- **AI服务**：OpenAI API
- **数据源**：
  - [MVP] Wikipedia API
  - [MVP] Spotify API
  - 其他音乐平台 API
- **认证服务**：Supabase Auth
- **文件存储**：Supabase Storage

### 7.5 数据模型（Supabase）

```sql
-- 艺术家表
CREATE TABLE artists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    wiki_data JSONB,  -- 存储Wikipedia原始数据
    ai_description TEXT,
    ai_description_style JSONB,  -- 存储AI生成的风格参数
    spotify_id TEXT,
    social_media JSONB,
    performance_time TIMESTAMP,
    stage_location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 歌曲表
CREATE TABLE songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artist_id UUID REFERENCES artists(id),
    title TEXT NOT NULL,
    platform_links JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户收藏表
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    artist_id UUID REFERENCES artists(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 相似艺术家表
CREATE TABLE similar_artists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artist_id UUID REFERENCES artists(id),
    similar_artist_id UUID REFERENCES artists(id),
    similarity_type TEXT,
    similarity_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 7.6 API 端点设计（FastAPI）

```python
# 艺术家相关
GET /api/artists - 获取艺术家列表
GET /api/artists/{id} - 获取艺术家详情
GET /api/artists/{id}/songs - 获取艺术家歌曲
GET /api/artists/{id}/similar - 获取相似艺术家
GET /api/artists/{id}/wiki - 获取Wikipedia原始数据
GET /api/artists/{id}/ai-description - 获取AI生成的毒舌介绍

# 用户相关
POST /api/auth/login - 用户登录
GET /api/user/favorites - 获取用户收藏
POST /api/user/favorites - 添加收藏
DELETE /api/user/favorites/{id} - 删除收藏

# 音乐平台相关
POST /api/music/connect - 连接音乐平台
GET /api/music/playlists - 获取歌单
POST /api/music/play - 播放音乐

# AI处理相关
POST /api/ai/generate-description - 生成毒舌风格介绍
  - 输入：Wikipedia原始数据
  - 输出：毒舌风格介绍
  - 参数：风格强度、毒舌程度等
```

## 8. 开发计划

### 第一阶段（MVP）
1. [MVP] 基础艺术家信息展示
2. [MVP] Wikipedia API 集成
3. [MVP] AI 毒舌风格转换
   - Wikipedia 数据获取
   - 数据清洗和结构化
   - AI 风格转换
   - 事实性验证
4. [MVP] Spotify 平台接入
5. [MVP] 搜索功能
6. [MVP] 本地收藏功能
7. [MVP] 基础分类导航

### 第二阶段
1. 其他流媒体平台接入
2. 相似艺术家推荐
3. 分享功能
4. 星座运势随机展示
5. 社交媒体链接
6. 艺术家八卦

### 第三阶段
1. 演出时间表
2. 演出舞台位置
3. 云端数据同步
4. 离线功能支持
5. 多设备支持

## 9. 风险评估
- 流媒体平台API限制
- Wikipedia 数据准确性
- AI 风格转换的平衡（趣味性 vs 事实性）
- 数据存储的安全性
- 页面性能优化
- 多平台同步的复杂性

## 10. 成功指标
- 用户停留时间
- 收藏/分享数量
- 音乐播放次数
- 用户反馈评分
- 多平台使用率
- AI 介绍准确度评分
- Wikipedia 数据覆盖率 