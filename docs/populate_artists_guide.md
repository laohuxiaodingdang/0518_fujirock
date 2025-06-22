# Fuji Rock 2025 艺术家数据库填充指南

## 概述

本指南介绍如何使用脚本批量填充 Fuji Rock 2025 的艺术家数据到数据库中。我们提供了两个脚本：
- **测试脚本**：处理少量知名艺术家，用于测试功能
- **完整脚本**：处理所有 Fuji Rock 2025 艺术家

## 前置条件

### 1. 环境配置

确保 `.env` 文件包含所有必要的 API 密钥：

```bash
# Supabase 数据库配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Spotify API 配置
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key

# Wikipedia API（通常不需要密钥）
WIKIPEDIA_API_URL=https://zh.wikipedia.org/api/rest_v1
```

### 2. 依赖安装

```bash
pip install -r requirements.txt
```

### 3. 数据库表结构

确保 Supabase 数据库中已创建以下表：
- `artists` - 艺术家基本信息
- `songs` - 歌曲信息
- `ai_descriptions` - AI 生成的描述
- `user_favorites` - 用户收藏
- `search_history` - 搜索历史

## 使用方法

### 方法一：测试脚本（推荐先运行）

测试脚本只处理 5 个知名艺术家，用于验证功能是否正常：

```bash
# 从项目根目录运行
python scripts/test_populate_sample.py
```

**测试艺术家列表：**
- VAMPIRE WEEKEND
- RADWIMPS
- JAMES BLAKE
- FOUR TET
- THE HIVES

**预期输出：**
```
🎸 Fuji Rock 2025 艺术家数据库填充测试开始
✅ 数据库连接正常
📝 将处理 5 个测试艺术家

============================================================
处理进度: 1/5 - VAMPIRE WEEKEND
============================================================
🎵 开始处理艺术家: VAMPIRE WEEKEND
📖 获取 Wikipedia 数据: VAMPIRE WEEKEND
✅ Wikipedia 数据获取成功
🎧 获取 Spotify 数据: VAMPIRE WEEKEND
✅ Spotify 数据获取成功
✅ 热门歌曲获取成功
🤖 生成 AI 描述: VAMPIRE WEEKEND
✅ AI 描述生成成功
💾 保存到数据库: VAMPIRE WEEKEND
✅ 艺术家记录创建成功
🎉 艺术家 VAMPIRE WEEKEND 处理完成！
```

### 方法二：完整脚本

处理所有 Fuji Rock 2025 艺术家（约 140+ 个）：

```bash
# 从项目根目录运行
python scripts/populate_fuji_rock_artists.py
```

**注意事项：**
- 完整脚本需要较长时间运行（预计 1-2 小时）
- 会消耗 API 配额（Spotify、OpenAI）
- 建议在网络稳定的环境下运行
- 支持中断恢复（已处理的艺术家会被跳过）

## 脚本功能详解

### 数据获取流程

每个艺术家的处理流程包括：

1. **检查重复**：查询数据库是否已存在该艺术家
2. **Wikipedia 数据**：获取艺术家的基本信息和描述
3. **Spotify 数据**：获取艺术家信息、热门歌曲、流行度等
4. **AI 描述生成**：基于 Wikipedia 内容生成有趣的中文描述
5. **数据库存储**：将所有数据保存到相应的表中

### 数据库操作

脚本会执行以下数据库操作：

1. **创建艺术家记录**
   ```sql
   INSERT INTO artists (name, description, genres, is_fuji_rock_artist, ...)
   ```

2. **更新 Wikipedia 数据**
   ```sql
   UPDATE artists SET wiki_data = ?, wiki_extract = ?, wiki_last_updated = ?
   ```

3. **更新 Spotify 数据**
   ```sql
   UPDATE artists SET spotify_data = ?, spotify_id = ?, popularity = ?, ...
   ```

4. **保存 AI 描述**
   ```sql
   INSERT INTO ai_descriptions (artist_id, content, language, ...)
   ```

5. **批量保存歌曲**
   ```sql
   INSERT INTO songs (artist_id, title, album_name, preview_url, ...)
   ```

### 错误处理

脚本具有完善的错误处理机制：

- **API 限制**：自动添加延迟避免超出 API 限制
- **网络错误**：重试机制和详细错误日志
- **数据验证**：Pydantic 模型确保数据格式正确
- **部分失败**：单个艺术家失败不影响其他艺术家处理

## 验证结果

### 1. 通过 API 查看

```bash
# 获取所有 Fuji Rock 艺术家
curl "http://localhost:8000/api/database/artists/fuji-rock"

# 搜索特定艺术家
curl "http://localhost:8000/api/database/artists?query=VAMPIRE"

# 获取艺术家详细信息
curl "http://localhost:8000/api/database/artists/by-name/VAMPIRE%20WEEKEND"
```

### 2. 通过 Web 界面

访问 `http://localhost:8000/docs` 查看 API 文档并测试接口。

### 3. 数据库直接查询

```sql
-- 查看艺术家总数
SELECT COUNT(*) FROM artists WHERE is_fuji_rock_artist = true;

-- 查看有 Spotify 数据的艺术家
SELECT name, popularity, followers_count FROM artists 
WHERE spotify_id IS NOT NULL 
ORDER BY popularity DESC;

-- 查看有 AI 描述的艺术家
SELECT a.name, ai.content 
FROM artists a 
JOIN ai_descriptions ai ON a.id = ai.artist_id 
WHERE a.is_fuji_rock_artist = true;
```

## 性能优化

### 批处理配置

可以调整脚本中的参数来优化性能：

```python
await populator.populate_all_artists(
    batch_size=3,  # 每批处理的艺术家数量
    delay=1.5      # API 调用间隔（秒）
)
```

### API 配额管理

- **Spotify API**：每小时约 1000 次请求
- **OpenAI API**：根据你的订阅计划
- **Wikipedia API**：通常无限制

建议在非高峰时段运行完整脚本。

## 故障排除

### 常见问题

1. **数据库连接失败**
   ```
   ❌ 数据库连接失败，请检查 Supabase 配置
   ```
   - 检查 `SUPABASE_URL` 和 `SUPABASE_SERVICE_ROLE_KEY`
   - 确认网络连接正常

2. **Spotify API 错误**
   ```
   ⚠️ Spotify 数据获取失败: Invalid client credentials
   ```
   - 检查 `SPOTIFY_CLIENT_ID` 和 `SPOTIFY_CLIENT_SECRET`
   - 确认 Spotify 应用配置正确

3. **OpenAI API 错误**
   ```
   ⚠️ AI 描述生成失败: Insufficient quota
   ```
   - 检查 OpenAI 账户余额
   - 考虑降低 AI 描述生成频率

4. **艺术家名称问题**
   ```
   ⚠️ Wikipedia 数据获取失败: Page not found
   ```
   - 某些艺术家可能在 Wikipedia 上没有页面
   - 这是正常现象，脚本会继续处理其他数据源

### 日志分析

脚本会生成详细的日志文件：

```bash
# 查看完整日志
tail -f fuji_rock_populate.log

# 查看错误信息
grep "ERROR" fuji_rock_populate.log

# 查看成功处理的艺术家
grep "处理完成" fuji_rock_populate.log
```

## 自定义配置

### 修改艺术家列表

如果需要添加或修改艺术家列表，编辑脚本中的 `FUJI_ROCK_2025_ARTISTS` 数组：

```python
FUJI_ROCK_2025_ARTISTS = [
    "YOUR_ARTIST_NAME",
    "ANOTHER_ARTIST",
    # ... 更多艺术家
]
```

### 调整 AI 描述风格

修改 AI 描述生成参数：

```python
ai_result = await openai_service.generate_sassy_description(
    artist_name=artist_name,
    wiki_content=wiki_extract,
    style_intensity=8,  # 1-10，数字越大越"毒舌"
    language="zh"       # 支持 "zh", "en", "ja"
)
```

## 最佳实践

1. **先运行测试脚本**：确保所有配置正确
2. **监控 API 配额**：避免超出限制
3. **定期备份数据库**：防止数据丢失
4. **分批运行**：如果艺术家数量很多，可以分批处理
5. **日志保存**：保留日志文件用于问题排查

## 总结

通过这些脚本，你可以：

- ✅ 自动获取 Fuji Rock 2025 所有艺术家的详细信息
- ✅ 整合 Wikipedia、Spotify、AI 等多个数据源
- ✅ 生成有趣的中文艺术家描述
- ✅ 构建完整的音乐数据库
- ✅ 为前端应用提供丰富的数据支持

数据库填充完成后，你就可以使用完整的 API 来构建 Fuji Rock 2025 音乐探索应用了！ 