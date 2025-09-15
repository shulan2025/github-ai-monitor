# 部署指南

本指南将帮助您将 GitHub AI Monitor 部署到 GitHub 并设置自动运行。

## 🚀 部署步骤

### 1. 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `github-ai-monitor`
   - **Description**: `🤖 自动化 GitHub AI 项目监控系统`
   - **Visibility**: Public (推荐) 或 Private
   - **Initialize**: 不要勾选任何选项
4. 点击 "Create repository"

### 2. 上传代码到 GitHub

```bash
# 进入项目目录
cd github-ai-monitor-repo

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "feat: 初始提交 - GitHub AI Monitor v2.1"

# 添加远程仓库 (替换为您的仓库地址)
git remote add origin https://github.com/your-username/github-ai-monitor.git

# 推送到 GitHub
git push -u origin main
```

### 3. 配置 GitHub Secrets

在 GitHub 仓库页面，点击 **Settings** → **Secrets and variables** → **Actions**，添加以下 Secrets：

#### 必需配置
- `GITHUB_TOKEN`: 您的 GitHub Personal Access Token
- `CLOUDFLARE_ACCOUNT_ID`: Cloudflare 账户 ID
- `CLOUDFLARE_API_TOKEN`: Cloudflare API Token
- `D1_DATABASE_ID`: D1 数据库 ID

#### 可选配置 (邮件通知)
- `EMAIL_HOST`: SMTP 服务器地址
- `EMAIL_PORT`: SMTP 端口
- `EMAIL_USER`: 发送邮箱
- `EMAIL_PASSWORD`: 邮箱密码或应用密码
- `EMAIL_TO`: 接收通知的邮箱

### 4. 获取必要的 Token 和 ID

#### GitHub Personal Access Token
1. 访问 [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - `repo` (完整仓库访问)
   - `read:user` (读取用户信息)
   - `read:org` (读取组织信息)
4. 生成并复制 Token

#### Cloudflare 配置
1. **Account ID**: 在 [Cloudflare Dashboard](https://dash.cloudflare.com) 右上角
2. **API Token**: 访问 [API Tokens](https://dash.cloudflare.com/profile/api-tokens)
   - 创建自定义 Token
   - 权限：`Zone:Zone:Read`, `Zone:Zone Settings:Edit`
   - 资源：`Include - All zones`
3. **Database ID**: 在 D1 数据库详情页面

### 5. 初始化数据库

在本地运行数据库初始化：

```bash
# 复制环境变量模板
cp env.template .env

# 编辑 .env 文件，填入配置
nano .env

# 初始化数据库
python3 setup_database.py
```

### 6. 测试配置

```bash
# 测试所有配置
python3 test_config.py

# 小规模测试采集
python3 optimized_fast_collector.py --test --limit 10
```

### 7. 启用 GitHub Actions

1. 推送代码后，GitHub Actions 会自动启用
2. 访问仓库的 **Actions** 页面
3. 点击 "Daily AI Repository Collection" 工作流
4. 可以手动触发测试运行

## ⚙️ 自动化配置

### 定时运行

系统已配置为每天 UTC 00:00 (北京时间 08:00) 自动运行。如需修改时间，编辑 `.github/workflows/daily-collection.yml`：

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 修改这里的时间
```

### 手动触发

在 GitHub Actions 页面可以手动触发采集任务，支持测试模式。

### 邮件通知

配置邮件 Secrets 后，系统会在采集完成后发送统计报告。

## 🔧 监控和维护

### 查看运行状态

1. 访问仓库的 **Actions** 页面
2. 查看最新的工作流运行状态
3. 点击运行记录查看详细日志

### 数据库监控

```bash
# 检查数据库状态
python3 simple_db_check.py

# 查看数据统计
python3 verify_watchers_fix.py
```

### 日志分析

在 GitHub Actions 中下载日志文件进行分析：
- `collection-logs-{run_number}` 包含完整的运行日志

## 🛠️ 故障排除

### 常见问题

1. **GitHub API 速率限制**
   - 检查 Token 权限
   - 查看 API 使用情况

2. **Cloudflare D1 连接失败**
   - 验证 Account ID 和 API Token
   - 检查数据库 ID 是否正确

3. **采集数量不足**
   - 检查关键词配置
   - 调整时间范围参数

4. **邮件通知失败**
   - 验证 SMTP 配置
   - 检查邮箱应用密码

### 调试模式

在本地启用调试模式：

```bash
# 设置环境变量
export DEBUG_MODE=true
export VERBOSE_LOGGING=true

# 运行采集
python3 optimized_fast_collector.py
```

## 📊 性能优化

### 并发设置

在 `config_v2.py` 中调整并发参数：

```python
# 并发请求数
MAX_CONCURRENT_REQUESTS = 5

# 批次大小
BATCH_SIZE = 100
```

### 采集策略

```python
# 采集间隔
COLLECTION_INTERVAL_HOURS = 6

# 目标数量
TARGET_COLLECTION_COUNT = 2500
```

## 🔒 安全建议

1. **Token 安全**
   - 定期轮换 API Token
   - 使用最小权限原则
   - 不要在代码中硬编码 Token

2. **访问控制**
   - 限制仓库访问权限
   - 定期审查 Secrets 配置

3. **数据保护**
   - 定期备份数据库
   - 监控异常访问

## 📈 扩展功能

### 添加新的数据源

1. 扩展 `config_v2.py` 中的关键词配置
2. 修改 `data_processor.py` 处理新数据
3. 更新数据库表结构

### 自定义通知

修改 `.github/workflows/daily-collection.yml` 添加自定义通知逻辑。

### 数据分析

添加数据分析脚本，定期生成报告。

## 📞 支持

如果遇到问题：

1. 查看 [Issues](https://github.com/your-username/github-ai-monitor/issues)
2. 创建新的 Issue 描述问题
3. 查看 [Discussions](https://github.com/your-username/github-ai-monitor/discussions) 获取帮助

---

🎉 部署完成后，您的 GitHub AI Monitor 将每天自动采集最新的 AI 项目数据！
