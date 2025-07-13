-- 添加音乐平台URL字段
ALTER TABLE artists
ADD COLUMN IF NOT EXISTS qq_music_url TEXT,
ADD COLUMN IF NOT EXISTS netease_url TEXT;

-- 添加注释
COMMENT ON COLUMN artists.qq_music_url IS 'QQ音乐艺术家页面URL';
COMMENT ON COLUMN artists.netease_url IS '网易云音乐艺术家页面URL';

-- 验证新字段
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'artists' AND column_name IN ('qq_music_url', 'netease_url');
