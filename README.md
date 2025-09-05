# 🚀 GitHub AI Repository Monitor v1.0

> 智能AI项目监控系统 - 自动发现、评估和追踪GitHub上的优质AI项目

[![GitHub release](https://img.shields.io/badge/release-v1.0-blue.svg)](https://github.com/your-username/github-ai-monitor/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

## 📋 项目简介

GitHub AI Repository Monitor 是一个智能的AI项目监控系统，能够：

- 🔍 **自动发现** GitHub上的优质AI项目
- 📊 **智能评估** 项目质量和活跃度  
- 🤖 **AI分类** 自动识别项目类型和技术栈
- 📈 **活跃度追踪** 基于推送时间的10分制评分
- 👀 **热度分析** 星标、分叉、关注者综合评估
- ☁️ **云端存储** 使用Cloudflare D1数据库
- ⏰ **定时任务** 每日自动更新数据
- 🔄 **智能去重** 30天时间窗口去重机制

## ✨ 核心特性

### 🎯 **智能评分系统**
- **活跃度评分** (0-10分): 基于最后推送时间的智能评分
- **质量评分** (0-50分): 综合星标、分叉、文档、社区等指标
- **创新指数** (0-20分): AI技术前沿性和研究质量评估

### 🤖 **AI智能分析**
- **框架识别**: PyTorch, TensorFlow, HuggingFace, LangChain等
- **模型分类**: LLM, CV, NLP, RAG, Agent系统等
- **前沿技术**: GPT-4, Claude, Multimodal, Reasoning等

### 📊 **数据丰富度**
- **基础指标**: 星标、分叉、关注者、问题数等
- **时间指标**: 创建时间、更新时间、推送时间
- **活跃度指标**: 贡献者、提交频率、发布版本
- **质量指标**: 许可证、文档、CI/CD、测试覆盖

## 🚀 快速开始

### 环境要求

- Python 3.8+
- GitHub Personal Access Token
- Cloudflare账户 (D1数据库)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 配置API密钥：
```bash
# GitHub API
GITHUB_TOKEN=your_github_token_here

# Cloudflare D1
CLOUDFLARE_API_TOKEN=your_cloudflare_token
CLOUDFLARE_ACCOUNT_ID=your_account_id  
D1_DATABASE_ID=your_database_id
```

### 数据库初始化

在Cloudflare D1控制台执行：

```sql
-- 创建基础表结构
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
    sync_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    relevance_score INTEGER DEFAULT 0,
    category TEXT,
    tags TEXT,
    summary TEXT,
    -- 活跃度字段
    pushed_at TEXT,
    watchers INTEGER DEFAULT 0,
    activity_score INTEGER DEFAULT 0,
    days_since_pushed INTEGER DEFAULT 0
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_repos_stars ON repos(stars DESC);
CREATE INDEX IF NOT EXISTS idx_repos_activity ON repos(activity_score DESC);
CREATE INDEX IF NOT EXISTS idx_repos_watchers ON repos(watchers DESC);
CREATE INDEX IF NOT EXISTS idx_repos_pushed_at ON repos(pushed_at DESC);
```

### 快速测试

```bash
# 测试配置
python3 test_config.py

# 收集数据
python3 sync_d1.py

# 更新活跃度数据
python3 update_activity_data.py
```

## 📊 使用指南

### 基础数据收集

```bash
# 运行主数据收集脚本
python3 sync_d1.py
```

**配置参数** (`search_config.py`):
```python
SEARCH_CONFIG = {
    "min_stars": 100,        # 最低星标数
    "days_back": 30,         # 搜索时间范围(天)
    "per_page": 100          # 每页结果数
}
```

### 活跃度数据更新

```bash
# 更新项目活跃度数据
python3 update_activity_data.py
```

支持的操作：
1. 📊 批量更新活跃度数据 (前10个)
2. 📊 批量更新活跃度数据 (前50个)  
3. 🧪 测试活跃度评分算法
4. 📈 查看活跃度统计

### 数据查询示例

#### 🏆 查找最活跃的AI项目
```sql
SELECT name, owner, stars, watchers, activity_score, days_since_pushed
FROM repos 
WHERE activity_score >= 8
ORDER BY activity_score DESC, stars DESC
LIMIT 20;
```

#### 📈 综合质量筛选
```sql
SELECT name, owner, stars, watchers, activity_score, category
FROM repos 
WHERE activity_score >= 6 
  AND stars >= 1000 
  AND watchers >= 500
ORDER BY activity_score DESC, stars DESC;
```

#### 🔍 按技术栈分析
```sql
SELECT category, COUNT(*) as count, AVG(stars) as avg_stars
FROM repos 
WHERE category IS NOT NULL
GROUP BY category
ORDER BY count DESC;
```

## ⚙️ 自动化部署

### GitHub Actions (推荐)

创建 `.github/workflows/sync.yml`:

```yaml
name: AI Repository Sync

on:
  schedule:
    - cron: '0 22 * * *'  # 每天UTC 22:00 (北京时间6:00)
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Run data sync
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
        CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        D1_DATABASE_ID: ${{ secrets.D1_DATABASE_ID }}
      run: |
        python3 sync_d1.py
```

### 本地定时任务 (macOS)

```bash
# 设置定时任务
python3 setup_scheduler.py
```

自动创建LaunchAgent配置文件，每天早上6:00自动运行。

## 📂 项目结构

```
github-ai-monitor/
├── 📄 README.md                    # 项目文档
├── 📋 requirements.txt             # 依赖包
├── ⚙️ .env.example                 # 环境变量模板
├── 🔧 配置文件/
│   ├── search_config.py            # 搜索配置
│   └── time_based_dedup_config.py  # 去重配置
├── 🚀 核心脚本/
│   ├── sync_d1.py                  # 主数据收集脚本
│   ├── update_activity_data.py     # 活跃度数据更新
│   └── test_config.py              # 配置测试
├── 🗄️ 数据库脚本/
│   ├── create_table.sql            # 建表脚本
│   └── add_key_fields.sql          # 字段升级脚本
├── 📊 分析工具/
│   ├── metrics_dashboard.py        # 数据可视化
│   └── check_duplicates.py         # 数据验证
├── ⏰ 自动化/
│   ├── setup_scheduler.py          # 定时任务设置
│   └── .github/workflows/          # GitHub Actions
└── 📖 文档/
    ├── USAGE_GUIDE.md              # 使用指南
    ├── DATABASE_UPGRADE_GUIDE.md   # 数据库升级
    └── ACTIVITY_FIELDS_GUIDE.md    # 活跃度字段指南
```

## 🎯 评分算法

### 活跃度评分 (0-10分)

```python
def calculate_activity_score(days_since_pushed):
    if days_since_pushed <= 7:     return 10  # 🔥 极活跃
    elif days_since_pushed <= 30:  return 8   # 🚀 高活跃
    elif days_since_pushed <= 90:  return 6   # 📈 中等活跃
    elif days_since_pushed <= 180: return 4   # 📊 一般
    elif days_since_pushed <= 365: return 2   # 🐌 不活跃
    else:                          return 0   # ❌ 停止维护
```

### AI项目分类

| 分类 | 关键词 | 示例项目 |
|:----:|--------|----------|
| **LLM服务与工具** | llm, gpt, language-model | ChatGPT, LangChain |
| **计算机视觉** | cv, vision, image | YOLO, OpenCV |
| **RAG技术** | rag, retrieval, vector | LlamaIndex, Chroma |
| **生成式AI** | diffusion, generation | Stable Diffusion |
| **机器学习框架** | pytorch, tensorflow | PyTorch, TensorFlow |
| **通用AI工具** | ai, machine-learning | Hugging Face |

## 🔧 高级配置

### 搜索策略配置

```python
# search_config.py
SEARCH_CONFIG = {
    "min_stars": 100,           # 最低星标要求
    "days_back": 30,            # 搜索最近N天
    "per_page": 100,            # 每页结果数
}

# 启用的搜索领域
ENABLE_DOMAINS = {
    "LLM": True,                # 大语言模型
    "RAG": True,                # 检索增强生成  
    "Diffusion": True,          # 扩散模型
    "MachineLearning": True,    # 机器学习
    "ComputerVision": True,     # 计算机视觉
    "DataScience": True         # 数据科学
}
```

### 去重策略配置

```python
# time_based_dedup_config.py
DEDUP_CONFIG = {
    "dedup_window_days": 30,    # 30天内不重复
    "reentry_conditions": {
        "min_days_since_last": 30,
        "star_growth_threshold": 10,
        "activity_required": True
    }
}
```

## 📊 数据分析

### 生成分析报告

```bash
# 生成HTML可视化报告
python3 metrics_dashboard.py
```

生成包含以下内容的专业报告：
- 📈 项目活跃度分布
- 🏆 顶级AI项目排行榜
- 🤖 技术栈使用统计
- 📊 趋势分析图表

### API使用监控

```bash
# 检查GitHub API使用情况
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/rate_limit
```

## ⚠️ 注意事项

### API限制
- **GitHub API**: 5000次/小时 (认证用户)
- **建议频率**: 每次请求间隔2秒
- **监控**: 定期检查API使用量

### 数据质量
- 🔍 **智能过滤**: 自动过滤低质量项目
- 🎯 **相关性评分**: AI相关性阈值筛选
- 📊 **多维评估**: 星标、活跃度、质量综合评估

### 成本控制
- ☁️ **Cloudflare D1**: 免费额度充足
- 📊 **数据量**: 每日新增约20-50个项目
- 💾 **存储**: 文本数据，存储成本极低

## 🤝 贡献指南

### 开发环境

```bash
# 克隆项目
git clone https://github.com/your-username/github-ai-monitor.git
cd github-ai-monitor

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件添加API密钥

# 运行测试
python3 test_config.py
```

### 提交PR

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- 🐛 **Bug报告**: [Issues](https://github.com/your-username/github-ai-monitor/issues)
- 💡 **功能建议**: [Discussions](https://github.com/your-username/github-ai-monitor/discussions)
- 📧 **联系邮箱**: your-email@example.com

## 🙏 致谢

- [GitHub API](https://docs.github.com/en/rest) - 数据源
- [Cloudflare D1](https://developers.cloudflare.com/d1/) - 数据库服务
- [Python社区](https://python.org) - 开发工具

---

**🌟 如果这个项目对您有帮助，请给我们一个星标！**

📊 **统计数据**: 已监控 877+ AI项目 | 🔥 活跃项目 20+ | 📈 数据完整性 98%+