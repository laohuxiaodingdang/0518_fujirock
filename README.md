# Fuji Rock 2025 音乐探索工具

帮助 Fuji Rock 2025 票务持有者提前了解即将在音乐节演出的艺术家，提供音乐探索和发现功能。

## 项目架构

### 前端 (Next.js)
- 艺术家信息展示
- Spotify 接入
- 毒舌风格 AI 生成艺术家介绍
- 收藏/标记功能
- 相似艺术家推荐

### 后端 (FastAPI)
- Wikipedia API 集成
- AI 风格转换
- Spotify API 接入
- 用户数据管理

## 开发指南

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 技术栈

- 前端：React/Next.js、Tailwind CSS、Framer Motion、Shadcn/ui
- 后端：FastAPI、Python
- 数据库：Supabase (PostgreSQL)
- 第三方服务：Wikipedia API、Spotify API、OpenAI API
