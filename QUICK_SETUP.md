# ⚡ 快速设置指南

> 5分钟快速部署GitHub AI Repository Monitor v1.0

## 🚀 一键部署到GitHub

### 步骤1: Fork项目到您的GitHub

1. 点击右上角的 **Fork** 按钮
2. 选择您的GitHub账户
3. 等待Fork完成

### 步骤2: 配置API密钥

在您Fork的项目中设置以下Secrets:

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret** 添加以下密钥:

```bash
# GitHub API Token
名称: GITHUB_TOKEN  
值: 您的GitHub Personal Access Token

# Cloudflare配置
名称: CLOUDFLARE_API_TOKEN
值: 您的Cloudflare API Token

名称: CLOUDFLARE_ACCOUNT_ID  
值: 您的Cloudflare Account ID

名称: D1_DATABASE_ID
值: 您的D1数据库ID
```

### 步骤3: 创建D1数据库

1. 登录 [Cloudflare控制台](https://dash.cloudflare.com/)
2. 选择 **D1** → **Create database**
3. 输入数据库名称: `ai-repos`
4. 在控制台执行以下SQL:

```sql
-- 创建基础表
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

### 步骤4: 手动触发第一次运行

1. 进入 **Actions** 页面
2. 选择 **AI Repository Monitor Sync** 工作流
3. 点击 **Run workflow** → **Run workflow**
4. 等待运行完成 (约5-10分钟)

### 步骤5: 验证结果

在Cloudflare D1控制台执行查询验证数据:

```sql
-- 查看收集到的项目数量
SELECT COUNT(*) as total_projects FROM repos;

-- 查看最活跃的项目
SELECT name, owner, stars, activity_score 
FROM repos 
WHERE activity_score > 0 
ORDER BY activity_score DESC, stars DESC 
LIMIT 10;
```

---

## 🔧 本地开发设置

### 快速本地运行

```bash
# 1. 克隆项目
git clone https://github.com/your-username/github-ai-monitor.git
cd github-ai-monitor

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件填入API密钥

# 4. 测试配置
python3 test_config.py

# 5. 运行数据收集
python3 sync_d1.py

# 6. 更新活跃度数据
python3 update_activity_data.py
```

---

## 🎯 获取API密钥指南

### 📍 GitHub Personal Access Token

1. 访问 [GitHub Settings](https://github.com/settings/tokens)
2. 点击 **Generate new token (classic)**
3. 设置权限: `public_repo` (读取公共仓库)
4. 复制生成的token

### ☁️ Cloudflare API配置

1. 访问 [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. 点击 **Create Token**
3. 使用 **Custom token** 模板
4. 设置权限:
   - `Account:D1:Edit`
   - `Zone:Zone:Read`
5. 复制生成的token

### 🗄️ 获取Account ID和Database ID

**Account ID**:
- 在Cloudflare控制台右侧栏可找到

**Database ID**:  
- 创建D1数据库后，在数据库详情页面可找到

---

## ⚙️ 配置选项

### 修改搜索参数

编辑 `search_config.py`:

```python
SEARCH_CONFIG = {
    "min_stars": 100,        # 最低星标要求
    "days_back": 30,         # 搜索最近30天
    "per_page": 100          # 每页结果数
}

# 启用搜索领域
ENABLE_DOMAINS = {
    "LLM": True,             # 大语言模型
    "RAG": True,             # 检索增强生成
    "Diffusion": True,       # 扩散模型
    "MachineLearning": True, # 机器学习
    "ComputerVision": True,  # 计算机视觉
    "DataScience": True      # 数据科学
}
```

### 调整运行时间

编辑 `.github/workflows/sync.yml`:

```yaml
on:
  schedule:
    # 每天 UTC 22:00 运行 (北京时间 6:00)
    - cron: '0 22 * * *'
    
    # 改为其他时间，例如UTC 14:00 (北京时间 22:00)
    # - cron: '0 14 * * *'
```

---

## 🔍 故障排除

### 常见问题

**1. GitHub API 401错误**
- 检查GITHUB_TOKEN是否正确
- 确认token权限包含`public_repo`

**2. Cloudflare连接失败**  
- 验证CLOUDFLARE_API_TOKEN正确性
- 检查Account ID和Database ID

**3. 数据库表不存在**
- 在D1控制台执行建表SQL
- 确认数据库名称正确

**4. Actions运行失败**
- 检查所有Secrets是否正确设置
- 查看Actions日志具体错误信息

### 调试命令

```bash
# 测试GitHub API连接
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/rate_limit

# 测试配置文件
python3 test_config.py

# 检查数据库连接
python3 -c "
from test_config import test_database_connection
test_database_connection()
"
```

---

## 📊 验证成功部署

### 检查数据收集

```sql
-- 1. 检查总项目数
SELECT COUNT(*) as total FROM repos;

-- 2. 检查活跃项目
SELECT COUNT(*) as active FROM repos WHERE activity_score > 0;

-- 3. 查看最新收集的项目
SELECT name, owner, stars, sync_time 
FROM repos 
ORDER BY sync_time DESC 
LIMIT 5;

-- 4. 检查不同活跃度级别的分布
SELECT 
  CASE 
    WHEN activity_score >= 8 THEN '高活跃'
    WHEN activity_score >= 6 THEN '中等活跃' 
    WHEN activity_score > 0 THEN '低活跃'
    ELSE '未更新'
  END as level,
  COUNT(*) as count
FROM repos 
GROUP BY level;
```

### 预期结果

成功部署后，您应该看到：
- ✅ 总项目数: 20-100个
- ✅ 活跃项目: 10-50个  
- ✅ 数据完整性: >95%
- ✅ API调用成功率: 100%

---

## 🎉 部署完成

恭喜！您的GitHub AI Repository Monitor v1.0已成功部署！

### 下一步操作

1. **⭐ 给项目加星**: 如果觉得有用，请给原项目点个star
2. **🔄 定期检查**: 每周查看一次数据更新情况
3. **📊 数据分析**: 使用SQL查询分析AI技术趋势
4. **🛠️ 自定义配置**: 根据需求调整搜索参数

### 获得帮助

- 📖 **完整文档**: [README.md](README.md)
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-username/github-ai-monitor/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/your-username/github-ai-monitor/discussions)

**🚀 开始探索AI技术的无限可能吧！**
