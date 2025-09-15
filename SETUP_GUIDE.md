# 🚀 GitHub AI Monitor 设置指南

## 📋 概述
本指南将帮助您完成两个目标：
1. **立即运行一次数据采集** - 解决当前3天未采集的问题
2. **设置自动化采集** - 配置 GitHub Actions 实现每日自动采集

## 🔧 第一步：立即运行采集

### 1.1 获取必要的API凭证

#### GitHub Token
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置权限：
   - ✅ `repo` (完整仓库访问)
   - ✅ `read:user` (读取用户信息)
   - ✅ `read:org` (读取组织信息)
4. 复制生成的 token

#### Cloudflare 凭证
1. **Account ID**：
   - 登录 Cloudflare 控制台
   - 在右侧边栏找到 "Account ID"
   - 复制该 ID

2. **API Token**：
   - 访问：https://dash.cloudflare.com/profile/api-tokens
   - 点击 "Create Token"
   - 使用 "Custom token" 模板
   - 设置权限：
     - ✅ `Zone:Zone:Read`
     - ✅ `Zone:Zone Settings:Edit`
     - ✅ `Account:Cloudflare D1:Edit`
   - 复制生成的 token

3. **D1 Database ID**：
   - 在 Cloudflare 控制台进入 D1 数据库
   - 选择您的数据库
   - 在 "Settings" 页面找到 "Database ID"
   - 复制该 ID

### 1.2 配置环境变量
将获取的凭证填入 `.env` 文件：

```bash
# 编辑 .env 文件
nano .env
```

填入实际值：
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
CLOUDFLARE_ACCOUNT_ID=xxxxxxxxxxxxxxxxxxxxxxxx
CLOUDFLARE_API_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
D1_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxx
```

### 1.3 运行采集
```bash
# 安装依赖
pip install -r requirements.txt

# 运行采集
python3 optimized_fast_collector.py
```

## 🚀 第二步：设置自动化采集

### 2.1 创建 GitHub 仓库
1. 在 GitHub 上创建新仓库：`github-ai-monitor`
2. 选择 "Public" 或 "Private"（推荐 Private）

### 2.2 上传代码
```bash
# 初始化 Git
git init
git add .
git commit -m "feat: GitHub AI Monitor v2.1 - 完整验证版本"

# 添加远程仓库
git remote add origin https://github.com/your-username/github-ai-monitor.git

# 推送到 GitHub
git push -u origin main
```

### 2.3 配置 GitHub Secrets
1. 进入仓库的 "Settings" 页面
2. 点击左侧的 "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 添加以下 Secrets：

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `GITHUB_TOKEN` | 您的 GitHub Token | GitHub API 访问 |
| `CLOUDFLARE_ACCOUNT_ID` | 您的 Account ID | Cloudflare 账户标识 |
| `CLOUDFLARE_API_TOKEN` | 您的 API Token | Cloudflare API 访问 |
| `D1_DATABASE_ID` | 您的 Database ID | D1 数据库标识 |

### 2.4 启用 GitHub Actions
1. 进入仓库的 "Actions" 页面
2. 点击 "I understand my workflows, go ahead and enable them"
3. 系统将自动开始运行工作流

### 2.5 验证自动化
1. 在 "Actions" 页面查看工作流状态
2. 点击 "Daily AI Repository Collection" 查看运行日志
3. 确认采集成功完成

## 📊 监控和维护

### 查看采集状态
```bash
# 检查数据库状态
python3 simple_db_check.py

# 查看最新采集数据
python3 -c "
from cloudflare import Cloudflare
from config_v2 import Config
cf = Cloudflare(api_token=Config.CLOUDFLARE_API_TOKEN)
response = cf.d1.database.query(
    database_id=Config.D1_DATABASE_ID,
    account_id=Config.CLOUDFLARE_ACCOUNT_ID,
    sql='SELECT COUNT(*) as total FROM github_ai_post_attr'
)
print(f'总记录数: {response.result[0].results[0][\"total\"]}')
"
```

### 手动触发采集
1. 进入 GitHub 仓库的 "Actions" 页面
2. 选择 "Daily AI Repository Collection"
3. 点击 "Run workflow"
4. 选择参数并运行

## 🔧 故障排除

### 常见问题
1. **环境变量未设置**：检查 `.env` 文件或 GitHub Secrets
2. **API 权限不足**：确认 Token 权限设置正确
3. **数据库连接失败**：检查 Cloudflare 凭证和数据库 ID
4. **采集数量为0**：检查 GitHub API 限制和搜索关键词

### 日志查看
```bash
# 查看采集日志
tail -f collection.log

# 查看错误日志
tail -f error.log
```

## 📈 性能优化

### 调整采集参数
在 `config_v2.py` 中调整：
- `TARGET_COLLECTION_COUNT`: 目标采集数量
- `MIN_STARS`: 最小星标数
- `COLLECTION_INTERVAL_HOURS`: 采集间隔

### 监控指标
- 采集成功率
- 数据质量评分
- API 调用频率
- 存储空间使用

## 🎯 预期结果

设置完成后，系统将：
- ✅ 每天自动采集 2500+ AI 项目
- ✅ 智能去重和分类
- ✅ 质量评分和趋势分析
- ✅ 邮件通知和统计报告
- ✅ 完整的监控和日志

## 📞 支持

如遇问题，请检查：
1. 环境变量配置
2. API 权限设置
3. 网络连接状态
4. 日志文件内容

---

**设置完成后，您的 GitHub AI Monitor 将开始每日自动采集最新的 AI 项目数据！** 🎉
