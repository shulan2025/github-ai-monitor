-- 数据库升级脚本 v2.0
-- 基于用户建议和最佳实践的完整字段增强
-- 执行前请确保备份数据

-- ================================
-- 🎯 基础GitHub指标增强
-- ================================

-- 关注者数 (Watchers) - 重要指标
ALTER TABLE repos ADD COLUMN watchers INTEGER DEFAULT 0;

-- 开放问题数
ALTER TABLE repos ADD COLUMN open_issues INTEGER DEFAULT 0;

-- 项目大小 (KB)
ALTER TABLE repos ADD COLUMN size_kb INTEGER DEFAULT 0;

-- 主要编程语言
ALTER TABLE repos ADD COLUMN language TEXT;

-- 默认分支
ALTER TABLE repos ADD COLUMN default_branch TEXT DEFAULT 'main';

-- 是否为Fork项目
ALTER TABLE repos ADD COLUMN is_fork BOOLEAN DEFAULT 0;

-- ================================
-- ⏰ 时间和活跃度指标
-- ================================

-- 最后推送时间 (重要：从创建时间改为推送时间)
ALTER TABLE repos ADD COLUMN pushed_at TEXT;

-- 最后提交日期
ALTER TABLE repos ADD COLUMN last_commit_date TEXT;

-- 距离最后推送天数
ALTER TABLE repos ADD COLUMN days_since_pushed INTEGER DEFAULT 0;

-- 活跃度评分 (0-10分)
ALTER TABLE repos ADD COLUMN activity_score INTEGER DEFAULT 0;

-- ================================
-- 👥 社区和协作指标
-- ================================

-- 贡献者数量
ALTER TABLE repos ADD COLUMN contributors_count INTEGER DEFAULT 0;

-- 提交总数
ALTER TABLE repos ADD COLUMN commits_count INTEGER DEFAULT 0;

-- Pull Request数量
ALTER TABLE repos ADD COLUMN pull_requests_count INTEGER DEFAULT 0;

-- Issues总数
ALTER TABLE repos ADD COLUMN issues_count INTEGER DEFAULT 0;

-- 发布版本数
ALTER TABLE repos ADD COLUMN releases_count INTEGER DEFAULT 0;

-- Fork比率 (forks/stars)
ALTER TABLE repos ADD COLUMN fork_ratio REAL DEFAULT 0.0;

-- ================================
-- 🏆 质量和成熟度指标
-- ================================

-- 许可证类型
ALTER TABLE repos ADD COLUMN license_type TEXT;

-- 是否有README
ALTER TABLE repos ADD COLUMN has_readme BOOLEAN DEFAULT 0;

-- 是否有Wiki
ALTER TABLE repos ADD COLUMN has_wiki BOOLEAN DEFAULT 0;

-- 是否有GitHub Pages
ALTER TABLE repos ADD COLUMN has_pages BOOLEAN DEFAULT 0;

-- 是否有Issues功能
ALTER TABLE repos ADD COLUMN has_issues BOOLEAN DEFAULT 1;

-- 是否有Projects功能
ALTER TABLE repos ADD COLUMN has_projects BOOLEAN DEFAULT 0;

-- 是否有Discussions
ALTER TABLE repos ADD COLUMN has_discussions BOOLEAN DEFAULT 0;

-- ================================
-- 🤖 AI/ML特定指标
-- ================================

-- AI框架类型
ALTER TABLE repos ADD COLUMN ai_framework TEXT;

-- 模型类型 (LLM, CV, NLP, etc.)
ALTER TABLE repos ADD COLUMN model_type TEXT;

-- 是否包含模型文件
ALTER TABLE repos ADD COLUMN has_model_files BOOLEAN DEFAULT 0;

-- 是否有研究论文
ALTER TABLE repos ADD COLUMN has_paper BOOLEAN DEFAULT 0;

-- 前沿技术评分 (0-25分)
ALTER TABLE repos ADD COLUMN cutting_edge_score INTEGER DEFAULT 0;

-- 实用性评分 (0-20分)
ALTER TABLE repos ADD COLUMN practical_score INTEGER DEFAULT 0;

-- ================================
-- 💼 商业和应用价值
-- ================================

-- 企业采用指标 (0-20分)
ALTER TABLE repos ADD COLUMN enterprise_score INTEGER DEFAULT 0;

-- 生产就绪度 (0-10分)
ALTER TABLE repos ADD COLUMN production_ready_score INTEGER DEFAULT 0;

-- API可用性评分 (0-10分)
ALTER TABLE repos ADD COLUMN api_score INTEGER DEFAULT 0;

-- 文档质量评分 (0-15分)
ALTER TABLE repos ADD COLUMN documentation_score INTEGER DEFAULT 0;

-- 社区健康评分 (0-10分)
ALTER TABLE repos ADD COLUMN community_health_score INTEGER DEFAULT 0;

-- ================================
-- 📊 新增综合评分 (基于50分制)
-- ================================

-- 综合质量评分 (0-50分)
ALTER TABLE repos ADD COLUMN quality_score INTEGER DEFAULT 0;

-- 技术影响力评分 (0-30分)
ALTER TABLE repos ADD COLUMN impact_score INTEGER DEFAULT 0;

-- 创新指数 (0-20分)
ALTER TABLE repos ADD COLUMN innovation_score INTEGER DEFAULT 0;

-- ================================
-- 🏷️ 标签和分类增强
-- ================================

-- GitHub Topics (逗号分隔)
ALTER TABLE repos ADD COLUMN topics TEXT;

-- 技术栈标签
ALTER TABLE repos ADD COLUMN tech_stack TEXT;

-- 应用场景标签
ALTER TABLE repos ADD COLUMN use_cases TEXT;

-- 行业标签
ALTER TABLE repos ADD COLUMN industry_tags TEXT;

-- ================================
-- 📈 趋势和增长指标
-- ================================

-- 星标增长率 (每日)
ALTER TABLE repos ADD COLUMN star_growth_rate REAL DEFAULT 0.0;

-- 趋势评分 (0-10分)
ALTER TABLE repos ADD COLUMN trending_score INTEGER DEFAULT 0;

-- 热度指数
ALTER TABLE repos ADD COLUMN popularity_index REAL DEFAULT 0.0;

-- ================================
-- 🔍 SEO和发现性
-- ================================

-- 搜索关键词权重
ALTER TABLE repos ADD COLUMN keyword_weight INTEGER DEFAULT 0;

-- 相关度评分 (升级版)
ALTER TABLE repos ADD COLUMN relevance_score_v2 INTEGER DEFAULT 0;

-- 推荐优先级
ALTER TABLE repos ADD COLUMN recommendation_priority INTEGER DEFAULT 0;

-- ================================
-- 📋 元数据和管理
-- ================================

-- 数据版本
ALTER TABLE repos ADD COLUMN data_version TEXT DEFAULT 'v2.0';

-- 最后分析时间
ALTER TABLE repos ADD COLUMN last_analyzed_at DATETIME;

-- 分析状态
ALTER TABLE repos ADD COLUMN analysis_status TEXT DEFAULT 'pending';

-- 数据完整性评分
ALTER TABLE repos ADD COLUMN data_completeness_score INTEGER DEFAULT 0;

-- ================================
-- 🚀 性能优化索引
-- ================================

-- 核心查询索引
CREATE INDEX IF NOT EXISTS idx_watchers ON repos(watchers DESC);
CREATE INDEX IF NOT EXISTS idx_quality_score ON repos(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_impact_score ON repos(impact_score DESC);
CREATE INDEX IF NOT EXISTS idx_innovation_score ON repos(innovation_score DESC);

-- 活跃度索引
CREATE INDEX IF NOT EXISTS idx_pushed_at ON repos(pushed_at);
CREATE INDEX IF NOT EXISTS idx_activity_score ON repos(activity_score DESC);
CREATE INDEX IF NOT EXISTS idx_days_since_pushed ON repos(days_since_pushed);

-- AI/ML特定索引
CREATE INDEX IF NOT EXISTS idx_ai_framework ON repos(ai_framework);
CREATE INDEX IF NOT EXISTS idx_model_type ON repos(model_type);
CREATE INDEX IF NOT EXISTS idx_cutting_edge_score ON repos(cutting_edge_score DESC);

-- 商业价值索引
CREATE INDEX IF NOT EXISTS idx_enterprise_score ON repos(enterprise_score DESC);
CREATE INDEX IF NOT EXISTS idx_production_ready ON repos(production_ready_score DESC);

-- 复合索引 (多维度查询优化)
CREATE INDEX IF NOT EXISTS idx_comprehensive_ranking ON repos(quality_score DESC, impact_score DESC, stars DESC);
CREATE INDEX IF NOT EXISTS idx_ai_quality ON repos(ai_framework, model_type, cutting_edge_score DESC);
CREATE INDEX IF NOT EXISTS idx_active_quality ON repos(activity_score DESC, quality_score DESC);

-- 趋势分析索引
CREATE INDEX IF NOT EXISTS idx_trending ON repos(trending_score DESC, star_growth_rate DESC);
CREATE INDEX IF NOT EXISTS idx_language_quality ON repos(language, quality_score DESC);

-- ================================
-- 📝 字段说明注释
-- ================================

/*
🎯 新增字段分类说明:

📊 基础指标增强 (9个字段):
- watchers: 关注者数 (重要的受欢迎程度指标)
- open_issues: 开放问题数 (项目维护状态)
- size_kb: 项目大小 (代码量评估)
- language: 主要编程语言
- default_branch, is_fork: 项目基础属性

⏰ 时间活跃度 (4个字段):
- pushed_at: 最后推送时间 (关键优化点)
- last_commit_date: 最后提交日期
- days_since_pushed: 活跃度量化
- activity_score: 活跃度综合评分

👥 社区协作 (6个字段):
- contributors_count: 贡献者数量
- commits_count, pull_requests_count: 开发活跃度
- issues_count, releases_count: 项目管理
- fork_ratio: 实用性比率

🏆 质量成熟度 (7个字段):
- license_type: 开源许可证
- has_readme, has_wiki, has_pages: 文档完整性
- has_issues, has_projects, has_discussions: 功能启用状态

🤖 AI/ML特定 (6个字段):
- ai_framework, model_type: AI技术分类
- has_model_files, has_paper: AI项目特征
- cutting_edge_score, practical_score: AI技术评估

💼 商业应用 (5个字段):
- enterprise_score: 企业级应用评估
- production_ready_score: 生产就绪度
- api_score: API可用性
- documentation_score, community_health_score: 质量评估

📊 综合评分 (3个字段):
- quality_score: 综合质量 (0-50分)
- impact_score: 技术影响力 (0-30分)
- innovation_score: 创新指数 (0-20分)

🏷️ 标签分类 (4个字段):
- topics: GitHub官方主题
- tech_stack, use_cases, industry_tags: 智能分类标签

📈 趋势增长 (3个字段):
- star_growth_rate: 增长率量化
- trending_score, popularity_index: 热度评估

🔍 发现优化 (3个字段):
- keyword_weight: SEO权重
- relevance_score_v2: 升级版相关度
- recommendation_priority: 推荐优先级

📋 管理元数据 (4个字段):
- data_version, last_analyzed_at: 版本管理
- analysis_status, data_completeness_score: 数据质量管理

总计新增字段: 59个
升级后总字段数: 73个 (14 + 59)
*/
