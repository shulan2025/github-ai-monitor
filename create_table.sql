-- 创建 D1 数据库表结构
-- 在 Cloudflare D1 控制台中执行此 SQL 语句

CREATE TABLE IF NOT EXISTS repos (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    description TEXT,
    url TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT,
    sync_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_repos_stars ON repos(stars DESC);
CREATE INDEX IF NOT EXISTS idx_repos_owner ON repos(owner);
CREATE INDEX IF NOT EXISTS idx_repos_created_at ON repos(created_at);
CREATE INDEX IF NOT EXISTS idx_repos_sync_time ON repos(sync_time);
