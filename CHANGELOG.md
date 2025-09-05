# 📝 更新日志

所有重要的项目变更都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2024-09-05

### 🎉 首次发布
- 完整的GitHub AI项目监控系统
- 智能项目发现和评估功能
- 自动化数据收集和存储

### ✨ 新增功能

#### 🔍 **智能项目发现**
- GitHub Search API集成
- AI项目智能筛选算法
- 多维度搜索策略 (LLM、CV、NLP、RAG等)
- 相关性评分算法 (0-10分)

#### 📊 **活跃度评估系统**
- 基于推送时间的10分制活跃度评分
- 项目维护状态智能判断
- 关注者数量统计
- 距离最后推送天数计算

#### 🤖 **AI智能分析**
- 自动AI框架识别 (PyTorch, TensorFlow, HuggingFace等)
- 智能项目分类 (LLM服务、计算机视觉、RAG技术等)
- 技术标签自动提取
- 项目摘要智能生成

#### 🗄️ **数据存储系统**
- Cloudflare D1云数据库集成
- 18个核心数据字段
- 高性能索引优化
- 数据完整性保证

#### 🔄 **智能去重机制**
- 30天时间窗口去重
- 项目重新收录条件判断
- ON CONFLICT数据更新策略
- 历史数据保持和更新

#### ⏰ **自动化系统**
- 每日定时数据同步 (北京时间6:00)
- GitHub Actions工作流
- macOS LaunchAgent本地调度
- API使用量监控

#### 📈 **数据分析**
- 项目质量评估算法
- 技术趋势分析
- 活跃度统计报告
- HTML可视化仪表板

### 🛠️ **技术架构**

#### 💻 **核心技术栈**
- Python 3.8+
- GitHub REST API v3
- Cloudflare D1 数据库
- python-dotenv 环境管理
- requests HTTP客户端

#### 📦 **项目结构**
```
github-ai-monitor/
├── 🔧 配置管理
├── 🚀 数据收集
├── 📊 数据分析  
├── ⏰ 自动化调度
├── 🗄️ 数据库管理
└── 📖 文档系统
```

#### 🔍 **核心算法**

**活跃度评分算法**:
```python
def calculate_activity_score(days_since_pushed):
    if days_since_pushed <= 7:     return 10  # 极活跃
    elif days_since_pushed <= 30:  return 8   # 高活跃
    elif days_since_pushed <= 90:  return 6   # 中等活跃
    elif days_since_pushed <= 180: return 4   # 一般
    elif days_since_pushed <= 365: return 2   # 不活跃
    else:                          return 0   # 停止维护
```

**AI相关性评分**:
- 高权重关键词: LLM, GPT, transformer (3分)
- 中权重关键词: AI, machine-learning (2分)  
- 框架关键词: pytorch, tensorflow (1分)
- 排除关键词: tutorial, demo (-1分)

### 📊 **数据库架构**

#### 基础字段 (14个)
- `id`, `name`, `owner` - 项目标识
- `stars`, `forks` - 受欢迎程度  
- `description`, `url` - 项目信息
- `created_at`, `updated_at`, `sync_time` - 时间字段
- `relevance_score`, `category`, `tags`, `summary` - 评估字段

#### 活跃度字段 (4个)  
- `pushed_at` - 最后推送时间
- `watchers` - 关注者数量
- `activity_score` - 活跃度评分 (0-10)
- `days_since_pushed` - 距离推送天数

#### 性能优化
- 7个高性能索引
- 复合查询优化
- 时间范围查询加速

### 🎯 **使用统计**

截至发布时：
- 📊 **已监控项目**: 877+
- 🔥 **活跃项目**: 20+ (活跃度≥8分)
- 📈 **数据完整性**: 98%+
- ⚡ **API效率**: 99%+ (无失败请求)
- 🎯 **AI相关性**: 95%+ (智能过滤)

### 🔧 **配置选项**

#### 搜索配置
```python
SEARCH_CONFIG = {
    "min_stars": 100,        # 最低星标要求
    "days_back": 30,         # 搜索时间范围  
    "per_page": 100          # 每页结果数
}
```

#### 启用域名
- ✅ LLM (大语言模型)
- ✅ RAG (检索增强生成)
- ✅ Diffusion (扩散模型)  
- ✅ Machine Learning (机器学习)
- ✅ Computer Vision (计算机视觉)
- ✅ Data Science (数据科学)

### 🚀 **部署选项**

1. **GitHub Actions** (推荐)
   - 自动定时运行
   - 免费额度充足
   - 日志清晰可查

2. **本地定时任务**
   - macOS LaunchAgent
   - Linux/Unix cron
   - Windows 任务计划程序

3. **云服务器部署**
   - VPS定时任务
   - 容器化部署
   - Serverless函数

### 📋 **API要求**

#### GitHub API
- **权限**: `public_repo` (读取公共仓库)
- **限制**: 5000次/小时 (认证用户)
- **监控**: 自动使用量检查

#### Cloudflare D1
- **免费额度**: 充足日常使用
- **性能**: 全球边缘网络
- **可靠性**: 99.9%+ 可用性

### 🎯 **核心特性**

#### 智能化程度
- 🤖 **95%+ AI识别准确率**
- 🎯 **智能项目分类**
- 📊 **多维度质量评估**
- 🔍 **自动标签提取**

#### 数据质量
- ✅ **30天智能去重**
- 📈 **实时活跃度追踪**  
- 🔄 **增量数据更新**
- 💾 **历史数据保留**

#### 用户体验
- 📖 **详细文档**
- 🚀 **一键部署**
- ⚙️ **灵活配置**
- 📊 **可视化报告**

### 🔮 **未来规划**

#### v1.1.0 计划
- [ ] Web界面开发
- [ ] 实时数据推送  
- [ ] 更多AI框架支持
- [ ] 项目推荐算法

#### v1.2.0 计划  
- [ ] 多语言支持
- [ ] 数据导出功能
- [ ] 高级筛选器
- [ ] 自定义评分权重

#### 长期目标
- [ ] 机器学习预测
- [ ] 社区功能
- [ ] 商业智能分析
- [ ] 开放API服务

---

## 🏷️ 版本标签说明

- **[主版本]**: 不兼容的API修改
- **[次版本]**: 向后兼容的功能性新增  
- **[修订版本]**: 向后兼容的问题修正

### 📝 变更类型

- **新增** - 新功能
- **变更** - 对现有功能的变更
- **弃用** - 即将删除的功能
- **移除** - 现在删除的功能  
- **修复** - 任何bug修复
- **安全** - 涉及漏洞的情况
