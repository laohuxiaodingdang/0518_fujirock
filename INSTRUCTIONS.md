# Fuji Rock 2025 音乐探索工具 - 安装指南

## 环境要求

- Python 3.10+
- Node.js 18+
- 以下API密钥:
  - Spotify API (Client ID & Secret)
  - OpenAI API
  - Supabase 项目密钥

## 后端设置

1. 进入后端目录并创建虚拟环境:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 创建 `.env` 文件设置环境变量:

```
OPENAI_API_KEY=your_openai_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

4. 启动开发服务器:

```bash
uvicorn main:app --reload
```

现在后端应该在 http://localhost:8000 运行，可以通过 http://localhost:8000/docs 访问API文档。

## 前端设置

1. 进入前端目录:

```bash
cd frontend
```

2. 安装依赖:

```bash
npm install
```

3. 创建 `.env.local` 文件设置环境变量:

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. 启动开发服务器:

```bash
npm run dev
```

前端应用应该在 http://localhost:3000 运行。

## 数据库设置

1. 在 Supabase 中创建以下表:
   - artists
   - songs
   - user_favorites
   - similar_artists

2. 按照 README 中的数据模型设置表结构

## 其他配置

### Spotify API 设置
1. 在 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) 创建一个应用
2. 设置重定向 URI: `http://localhost:3000/api/auth/callback/spotify`
3. 获取 Client ID 和 Client Secret 并更新环境变量

### OpenAI API 设置
1. 在 [OpenAI](https://platform.openai.com/signup) 创建一个账户
2. 获取 API 密钥并更新环境变量 