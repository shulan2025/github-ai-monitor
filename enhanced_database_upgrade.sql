-- 增强指标数据库升级脚本
-- 为GitHub AI仓库监控系统添加完善的关键指标支持

-- ================================
-- 🎯 新增核心指标字段
-- ================================

-- 增强评分系统
ALTER TABLE repos ADD COLUMN enhanced_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN ai_maturity_level TEXT DEFAULT 'unknown';
ALTER TABLE repos ADD COLUMN community_health TEXT DEFAULT 'unknown';
ALTER TABLE repos ADD COLUMN innovation_level TEXT DEFAULT 'unknown';
ALTER TABLE repos ADD COLUMN commercial_potential TEXT DEFAULT 'unknown';

-- ================================
-- 📊 GitHub高级指标字段
-- ================================

-- 活跃度和参与度指标
ALTER TABLE repos ADD COLUMN contributors_count INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN issues_count INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN open_issues_count INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN pull_requests_count INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN watchers_count INTEGER DEFAULT 0;

-- 时间和活跃度指标
ALTER TABLE repos ADD COLUMN last_commit_date TEXT;
ALTER TABLE repos ADD COLUMN last_release_date TEXT;
ALTER TABLE repos ADD COLUMN days_since_last_commit INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN commit_frequency_score INTEGER DEFAULT 0;

-- ================================
-- 🤖 AI特定增强指标
-- ================================

-- AI技术成熟度
ALTER TABLE repos ADD COLUMN has_model_files BOOLEAN DEFAULT 0;
ALTER TABLE repos ADD COLUMN has_research_paper BOOLEAN DEFAULT 0;
ALTER TABLE repos ADD COLUMN has_deployment_config BOOLEAN DEFAULT 0;
ALTER TABLE repos ADD COLUMN ai_framework TEXT;
ALTER TABLE repos ADD COLUMN model_type TEXT;

-- AI前沿性指标
ALTER TABLE repos ADD COLUMN cutting_edge_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN research_quality_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN practical_deployment_score INTEGER DEFAULT 0;

-- ================================
-- 🏗️ 项目质量指标
-- ================================

-- 代码质量和结构
ALTER TABLE repos ADD COLUMN primary_language TEXT;
ALTER TABLE repos ADD COLUMN languages_count INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN repo_size_kb INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN has_tests BOOLEAN DEFAULT 0;
ALTER TABLE repos ADD COLUMN has_ci_cd BOOLEAN DEFAULT 0;
ALTER TABLE repos ADD COLUMN has_documentation BOOLEAN DEFAULT 0;

-- 许可证和治理
ALTER TABLE repos ADD COLUMN license_type TEXT;
ALTER TABLE repos ADD COLUMN has_contributing_guide BOOLEAN DEFAULT 0;
ALTER TABLE repos ADD COLUMN has_code_of_conduct BOOLEAN DEFAULT 0;

-- ================================
-- 💼 商业价值指标
-- ================================

-- 企业采用和商业潜力
ALTER TABLE repos ADD COLUMN enterprise_adoption_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN funding_indicators TEXT;
ALTER TABLE repos ADD COLUMN industry_backing TEXT;
ALTER TABLE repos ADD COLUMN dependency_count INTEGER DEFAULT 0;

-- 社交和网络效应
ALTER TABLE repos ADD COLUMN social_media_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN blog_coverage_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN conference_mentions INTEGER DEFAULT 0;

-- ================================
-- 📈 元数据和分析字段
-- ================================

-- 分析和趋势数据
ALTER TABLE repos ADD COLUMN trending_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN growth_velocity REAL DEFAULT 0.0;
ALTER TABLE repos ADD COLUMN star_growth_rate REAL DEFAULT 0.0;
ALTER TABLE repos ADD COLUMN fork_to_star_ratio REAL DEFAULT 0.0;

-- GitHub Topics和标签
ALTER TABLE repos ADD COLUMN github_topics TEXT;
ALTER TABLE repos ADD COLUMN technology_stack TEXT;
ALTER TABLE repos ADD COLUMN use_cases TEXT;

-- 质量和可信度
ALTER TABLE repos ADD COLUMN code_quality_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN maintenance_score INTEGER DEFAULT 0;
ALTER TABLE repos ADD COLUMN security_score INTEGER DEFAULT 0;

-- ================================
-- 📊 性能优化索引
-- ================================

-- 核心指标索引
CREATE INDEX IF NOT EXISTS idx_enhanced_score ON repos(enhanced_score DESC);
CREATE INDEX IF NOT EXISTS idx_ai_maturity_level ON repos(ai_maturity_level);
CREATE INDEX IF NOT EXISTS idx_community_health ON repos(community_health);
CREATE INDEX IF NOT EXISTS idx_innovation_level ON repos(innovation_level);
CREATE INDEX IF NOT EXISTS idx_commercial_potential ON repos(commercial_potential);

-- GitHub指标索引
CREATE INDEX IF NOT EXISTS idx_contributors_count ON repos(contributors_count DESC);
CREATE INDEX IF NOT EXISTS idx_watchers_count ON repos(watchers_count DESC);
CREATE INDEX IF NOT EXISTS idx_last_commit_date ON repos(last_commit_date);
CREATE INDEX IF NOT EXISTS idx_primary_language ON repos(primary_language);

-- AI特定索引
CREATE INDEX IF NOT EXISTS idx_ai_framework ON repos(ai_framework);
CREATE INDEX IF NOT EXISTS idx_model_type ON repos(model_type);
CREATE INDEX IF NOT EXISTS idx_cutting_edge_score ON repos(cutting_edge_score DESC);
CREATE INDEX IF NOT EXISTS idx_has_research_paper ON repos(has_research_paper);

-- 商业价值索引
CREATE INDEX IF NOT EXISTS idx_enterprise_adoption ON repos(enterprise_adoption_score DESC);
CREATE INDEX IF NOT EXISTS idx_dependency_count ON repos(dependency_count DESC);
CREATE INDEX IF NOT EXISTS idx_trending_score ON repos(trending_score DESC);

-- 复合索引 (多维度查询优化)
CREATE INDEX IF NOT EXISTS idx_score_stars_forks ON repos(enhanced_score DESC, stars DESC, forks DESC);
CREATE INDEX IF NOT EXISTS idx_ai_level_score ON repos(ai_maturity_level, enhanced_score DESC);
CREATE INDEX IF NOT EXISTS idx_commercial_innovation ON repos(commercial_potential, innovation_level);

-- ================================
-- 📋 字段说明和数据字典
-- ================================

/*
🎯 增强指标字段说明:

📊 核心评分字段:
- enhanced_score: 增强版综合评分 (0-100分)
- ai_maturity_level: AI成熟度等级 (experimental/developing/mature/production)
- community_health: 社区健康状态 (poor/fair/good/excellent)
- innovation_level: 创新水平 (low/medium/high/cutting-edge)
- commercial_potential: 商业潜力 (low/medium/high/very-high)

🤖 AI特定字段:
- has_model_files: 是否包含模型文件
- has_research_paper: 是否有研究论文支撑
- ai_framework: AI框架类型 (pytorch/tensorflow/huggingface等)
- model_type: 模型类型 (llm/cv/nlp/multimodal等)
- cutting_edge_score: 前沿技术评分 (0-25分)

💼 商业价值字段:
- enterprise_adoption_score: 企业采用评分 (0-20分)
- industry_backing: 行业支持情况
- dependency_count: 被依赖项目数量
- social_media_score: 社交媒体影响力评分

📈 分析字段:
- growth_velocity: 增长速度
- star_growth_rate: 星标增长率
- fork_to_star_ratio: 分叉与星标比例
- trending_score: 趋势评分

📋 质量字段:
- code_quality_score: 代码质量评分
- maintenance_score: 维护质量评分
- security_score: 安全性评分
*/
