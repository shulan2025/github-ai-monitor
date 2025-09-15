-- 添加关键字段：Pushed At (活跃度) 和关注数
-- 在 Cloudflare D1 控制台中执行

-- ================================
-- 🎯 添加关键活跃度字段
-- ================================

-- 1. 最后推送时间 (Pushed At) - 关键活跃度指标
ALTER TABLE repos ADD COLUMN pushed_at TEXT;

-- 2. 关注者数量 (Watchers) - 项目关注度
ALTER TABLE repos ADD COLUMN watchers INTEGER DEFAULT 0;

-- 3. 活跃度评分 (基于推送时间计算)
ALTER TABLE repos ADD COLUMN activity_score INTEGER DEFAULT 0;

-- 4. 距离最后推送天数 (用于快速筛选)
ALTER TABLE repos ADD COLUMN days_since_pushed INTEGER DEFAULT 0;

-- ================================
-- 🔍 添加性能优化索引
-- ================================

-- 推送时间索引 (用于活跃度查询)
CREATE INDEX IF NOT EXISTS idx_pushed_at ON repos(pushed_at DESC);

-- 关注者数量索引 (用于热度排序)
CREATE INDEX IF NOT EXISTS idx_watchers ON repos(watchers DESC);

-- 活跃度评分索引 (用于活跃项目筛选)
CREATE INDEX IF NOT EXISTS idx_activity_score ON repos(activity_score DESC);

-- 距离推送天数索引 (用于快速筛选活跃项目)
CREATE INDEX IF NOT EXISTS idx_days_since_pushed ON repos(days_since_pushed);

-- 复合索引 (活跃度+星标综合排序)
CREATE INDEX IF NOT EXISTS idx_activity_stars ON repos(activity_score DESC, stars DESC);

-- ================================
-- 📝 字段说明
-- ================================

/*
新增字段说明:

1. pushed_at (TEXT):
   - 存储最后推送时间 (ISO 8601格式)
   - 示例: "2024-01-05T14:30:00Z"
   - 用途: 评估项目活跃度，识别活跃维护的项目

2. watchers (INTEGER):
   - 存储GitHub关注者数量
   - 默认值: 0
   - 用途: 评估项目受关注程度，辅助评估项目热度

3. activity_score (INTEGER):
   - 活跃度评分 (0-10分)
   - 基于pushed_at时间计算
   - 评分规则:
     * 7天内推送: 10分 (极活跃)
     * 30天内推送: 8分 (活跃)
     * 90天内推送: 6分 (中等活跃)
     * 180天内推送: 4分 (一般)
     * 365天内推送: 2分 (不活跃)
     * 超过365天: 0分 (停止维护)

4. days_since_pushed (INTEGER):
   - 距离最后推送的天数
   - 用于快速筛选和排序
   - 便于查询活跃项目
*/
