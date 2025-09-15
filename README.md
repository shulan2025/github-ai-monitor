# GitHub AI Monitor

🤖 自动化 GitHub AI 项目监控系统 - 每日采集高热度 AI 仓库数据

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-自动运行-blue)](https://github.com/your-username/github-ai-monitor/actions)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![Cloudflare D1](https://img.shields.io/badge/Cloudflare-D1-orange)](https://developers.cloudflare.com/d1/)

## 🎯 项目简介

GitHub AI Monitor 是一个自动化数据采集系统，专门用于监控和收集 GitHub 上高热度的人工智能相关项目。系统通过智能关键词匹配、多维度评分和去重机制，每日自动采集最新的 AI 项目数据并存储到 Cloudflare D1 数据库中。

## ✨ 核心功能

- 🔍 **智能搜索**: 基于 495+ 个 AI 关键词的智能搜索策略
- 📊 **多维度评分**: 质量评分、热度评分、AI 相关性评分
- 🚫 **智能去重**: 7天窗口期去重，支持 fork 增长重新收录
- ⚡ **高性能**: 异步并发处理，支持 2500+ 项目/次采集
- 🕐 **自动化**: GitHub Actions 每日自动运行
- 📈 **实时监控**: 完整的日志和统计报告

## 🏗️ 系统架构

```
GitHub API → 数据采集器 → 数据处理器 → 去重管理器 → Cloudflare D1
     ↓              ↓           ↓           ↓
  搜索策略      异步并发    智能评分    7天去重    数据存储
```

## 📋 数据字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `id` | INTEGER | GitHub 仓库 ID |
| `full_name` | TEXT | 仓库完整名称 |
| `name` | TEXT | 仓库名称 |
| `owner` | TEXT | 仓库所有者 |
| `description` | TEXT | 仓库描述 |
| `url` | TEXT | 仓库 URL |
| `stargazers_count` | INTEGER | 星标数量 |
| `forks_count` | INTEGER | Fork 数量 |
| `watchers_count` | INTEGER | 关注者数量 |
| `created_at` | TEXT | 创建时间 (北京时间) |
| `updated_at` | TEXT | 更新时间 (北京时间) |
| `pushed_at` | TEXT | 最后推送时间 (北京时间) |
| `language` | TEXT | 主要编程语言 |
| `topics` | TEXT | 仓库标签 |
| `ai_category` | TEXT | AI 分类 |
| `ai_tags` | TEXT | AI 标签 |
| `quality_score` | REAL | 质量评分 (0-100) |
| `trending_score` | REAL | 热度评分 (0-100) |
| `collection_round` | INTEGER | 采集轮次 |
| `last_fork_count` | INTEGER | 上次采集时的 Fork 数 |
| `fork_growth` | INTEGER | Fork 增长数 |
| `collection_hash` | TEXT | 采集哈希值 |
| `collection_time` | TEXT | 采集时间 (北京时间) |

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/your-username/github-ai-monitor.git
cd github-ai-monitor

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板并填写配置：

```bash
cp .env.template .env
```

编辑 `.env` 文件：

```env
# GitHub API 配置
GITHUB_TOKEN=your_github_token_here

# Cloudflare D1 配置
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
D1_DATABASE_ID=your_database_id

# 邮件通知配置 (可选)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com
```

### 3. 数据库初始化

```bash
# 创建数据库表
python3 setup_database.py
```

### 4. 测试运行

```bash
# 测试配置
python3 test_config.py

# 小规模测试采集 (100条)
python3 optimized_fast_collector.py --test --limit 100

# 完整采集
python3 optimized_fast_collector.py
```

## ⚙️ 配置说明

### 采集配置

在 `config_v2.py` 中可以调整以下参数：

```python
# 采集频率
COLLECTION_INTERVAL_HOURS = 6  # 每6小时采集一次

# 采集数量
TARGET_COLLECTION_COUNT = 2500  # 每次采集目标数量

# 时间范围
CREATED_YEARS_BACK = 10  # 创建时间范围：10年内
UPDATED_DAYS_BACK = 365  # 更新时间范围：1年内

# 最小星标数
MIN_STARS = 100  # 最小星标数要求
```

### 去重配置

```python
# 去重窗口期
DEDUP_WINDOW_DAYS = 7  # 7天去重窗口

# Fork 增长阈值
FORK_GROWTH_THRESHOLD = 1  # Fork 增长1个即可重新收录
```

## 🔄 GitHub Actions 自动化

系统已配置 GitHub Actions 工作流，支持：

- **每日自动运行**: 每天 UTC 00:00 自动执行采集
- **邮件通知**: 采集完成后发送统计报告
- **错误处理**: 自动重试和错误通知
- **日志记录**: 完整的运行日志

### 工作流配置

```yaml
# .github/workflows/daily-collection.yml
name: Daily AI Repository Collection

on:
  schedule:
    - cron: '0 0 * * *'  # 每天 UTC 00:00 运行
  workflow_dispatch:  # 支持手动触发

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run collection
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          D1_DATABASE_ID: ${{ secrets.D1_DATABASE_ID }}
        run: python3 optimized_fast_collector.py
```

## 📊 数据统计

### 关键词库统计
- **总关键词数量**: 495
- **总分类数量**: 54
- **搜索轮次**: 5
- **高优先级关键词**: 6

### 采集统计示例
```
📊 采集统计信息:
   总搜索关键词: 495
   成功采集项目: 2,456
   新增项目: 1,234
   更新项目: 1,222
   跳过项目: 0
   采集成功率: 100.0%
   平均质量评分: 78.5
   平均热度评分: 82.3
```

## 🛠️ 工具脚本

### 数据管理
- `simple_db_check.py` - 数据库状态检查
- `fix_watchers_count.py` - 修复关注者数量字段
- `verify_watchers_fix.py` - 验证修复结果

### 测试工具
- `test_config.py` - 配置测试
- `enhanced_data_processor.py` - 增强数据处理

## 📈 性能优化

- **异步并发**: 使用 `asyncio` 和 `aiohttp` 实现高并发
- **智能限流**: 自动处理 GitHub API 速率限制
- **批量处理**: 批量数据库操作提高效率
- **内存优化**: 流式处理大量数据

## 🔧 故障排除

### 常见问题

1. **API 速率限制**
   ```bash
   # 检查 GitHub API 使用情况
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
   ```

2. **数据库连接失败**
   ```bash
   # 测试数据库连接
   python3 simple_db_check.py
   ```

3. **采集数量不足**
   - 检查关键词库配置
   - 调整时间范围参数
   - 降低最小星标数要求

### 日志查看

```bash
# 查看详细日志
tail -f collection.log

# 查看错误日志
grep "ERROR" collection.log
```

## 📝 更新日志

### v2.1 (2025-09-12)
- ✅ 修复 `watchers_count` 字段问题
- ✅ 新增数据修复工具
- ✅ 优化采集性能
- ✅ 完善错误处理

### v2.0 (2025-09-11)
- ✅ 重构采集架构
- ✅ 实现智能去重
- ✅ 添加多维度评分
- ✅ 支持 GitHub Actions

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- **项目维护者**: [Your Name](https://github.com/your-username)
- **问题反馈**: [Issues](https://github.com/your-username/github-ai-monitor/issues)
- **讨论区**: [Discussions](https://github.com/your-username/github-ai-monitor/discussions)

## 🙏 致谢

- [GitHub API](https://docs.github.com/en/rest) - 数据源
- [Cloudflare D1](https://developers.cloudflare.com/d1/) - 数据存储
- [Python asyncio](https://docs.python.org/3/library/asyncio.html) - 异步处理

---

⭐ 如果这个项目对您有帮助，请给它一个星标！