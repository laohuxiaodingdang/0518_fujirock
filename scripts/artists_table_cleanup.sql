-- Fuji Rock 2025 Artists 表结构优化 SQL 脚本
-- 执行前请确保已备份数据

-- 删除冗余字段
ALTER TABLE artists DROP COLUMN IF EXISTS name_zh;
ALTER TABLE artists DROP COLUMN IF EXISTS name_en;
ALTER TABLE artists DROP COLUMN IF EXISTS name_ja;
ALTER TABLE artists DROP COLUMN IF EXISTS external_urls;
ALTER TABLE artists DROP COLUMN IF EXISTS popularity;
ALTER TABLE artists DROP COLUMN IF EXISTS followers_count;
ALTER TABLE artists DROP COLUMN IF EXISTS image_url;
ALTER TABLE artists DROP COLUMN IF EXISTS images;
ALTER TABLE artists DROP COLUMN IF EXISTS search_vector;
ALTER TABLE artists DROP COLUMN IF EXISTS spotify_data;

-- 验证表结构
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'artists' 
ORDER BY ordinal_position;

-- 验证数据
SELECT id, name, spotify_id, is_fuji_rock_artist, created_at 
FROM artists 
LIMIT 5; 