-- 升级 D1 数据库表结构
-- 在 Cloudflare D1 控制台中执行此 SQL 语句

-- 添加新字段
ALTER TABLE repos ADD COLUMN category TEXT;
ALTER TABLE repos ADD COLUMN tags TEXT;
ALTER TABLE repos ADD COLUMN summary TEXT;
ALTER TABLE repos ADD COLUMN relevance_score INTEGER DEFAULT 0;

-- 创建新索引
CREATE INDEX IF NOT EXISTS idx_repos_category ON repos(category);
CREATE INDEX IF NOT EXISTS idx_repos_relevance_score ON repos(relevance_score DESC);
