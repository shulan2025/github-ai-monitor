# 🚀 GitHub AI 仓库爬虫使用指南

## ⭐ 项目概览
您现在拥有一个完全自动化的AI项目监控系统，每天北京时间6:00自动收集最前沿的AI项目。

## 📊 当前数据状态
- ✅ **24个高质量AI项目** 已收集
- ✅ **智能分类系统** 自动分为9大类
- ✅ **每日自动更新** 北京时间6:00执行
- ✅ **30天时间窗口** + **100+星标要求**

## 🎯 核心功能

### 1. 智能分类
- **LLM服务与工具**: 推理引擎、API服务
- **LLM研究**: 学术研究、算法创新
- **RAG技术**: 检索增强生成
- **生成式AI**: 扩散模型、图像生成
- **LLM应用**: 聊天应用、客户端

### 2. 质量评分 (1-10分)
- **8-10分**: 🥇 顶级项目
- **6-7分**: 🥈 优秀项目 
- **4-5分**: 🥉 良好项目
- **2-3分**: ✅ 合格项目

## 📋 日常使用

### 每天早上 (6:00后)
查看新发现的AI项目：
```sql
SELECT name, category, summary, stars, url
FROM repos 
WHERE DATE(sync_time) = DATE('now')
ORDER BY relevance_score DESC;
```

### 每周分析
技术趋势分析：
```sql
SELECT category, COUNT(*) as projects, AVG(stars) as popularity
FROM repos 
WHERE sync_time >= datetime('now', '-7 days')
GROUP BY category;
```

### 发现明星项目
```sql
SELECT name, summary, stars, relevance_score, url
FROM repos 
WHERE relevance_score >= 6 AND stars >= 500
ORDER BY stars DESC;
```

## 🔧 管理命令

### 定时任务管理
```bash
./manage_launchd.sh status   # 查看运行状态
./manage_launchd.sh logs     # 查看运行日志
./manage_launchd.sh stop     # 停止自动运行
./manage_launchd.sh start    # 启动自动运行
```

### 手动运行
```bash
python3 sync_d1.py          # 立即执行一次数据收集
python3 test_config.py      # 测试API配置
python3 run.py              # 交互式管理界面
```

## ⚙️ 配置调整

编辑 `search_config.py` 可以调整：
- **星标要求**: `min_stars = 100`
- **时间范围**: `days_back = 30`  
- **搜索领域**: `ENABLE_DOMAINS`
- **评分阈值**: `AI_RELEVANCE_THRESHOLD`

## 📈 数据导出

### 导出 CSV
在 D1 Studio 中运行查询后，点击"Export"下载数据

### API 访问
通过 Cloudflare D1 HTTP API 访问数据

## 🚨 故障排除

### 检查日志
```bash
tail -f logs/sync.log        # 查看最新日志
tail -f logs/sync_error.log  # 查看错误日志
```

### 常见问题
1. **API限制**: 检查 GitHub Token 是否有效
2. **网络问题**: 查看错误日志
3. **数据库连接**: 验证 Cloudflare 凭证

## 📞 维护联系
- 配置文件: `search_config.py`
- 主脚本: `sync_d1.py`
- 数据库: Cloudflare D1 Studio
- 日志: `logs/` 目录

---
*最后更新: 2025年9月5日*
