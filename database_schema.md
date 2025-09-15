# GitHub AI 仓库数据库表结构说明

## 📊 数据库表：`repos`

### 🎯 表概述
存储从 GitHub 搜索到的 AI/ML 相关仓库信息，包含基础数据、智能分类、技术标签和相关性评分。

---

## 📋 字段详细说明

| 字段名 | 数据类型 | 约束 | 说明 | 示例值 |
|--------|----------|------|------|--------|
| **id** | TEXT | PRIMARY KEY | GitHub 仓库唯一ID | "123456789" |
| **name** | TEXT | NOT NULL | 仓库名称 | "xllm" |
| **owner** | TEXT | NOT NULL | 仓库所有者用户名 | "microsoft" |
| **stars** | INTEGER | DEFAULT 0 | 星标数量 | 1573 |
| **forks** | INTEGER | DEFAULT 0 | Fork 数量 | 245 |
| **description** | TEXT | NULL | 仓库描述（GitHub原始） | "A high-performance inference engine for LLMs" |
| **url** | TEXT | NOT NULL | 仓库 GitHub 链接 | "https://github.com/microsoft/xllm" |
| **created_at** | TEXT | NULL | 仓库创建时间 | "2025-08-15T10:30:00Z" |
| **updated_at** | TEXT | NULL | 仓库最后更新时间 | "2025-09-05T14:20:00Z" |
| **sync_time** | DATETIME | DEFAULT CURRENT_TIMESTAMP | 数据同步时间 | "2025-09-05 16:45:23" |
| **category** | TEXT | NULL | 🤖 智能分类 | "LLM服务与工具" |
| **tags** | TEXT | NULL | 🏷️ 技术标签（逗号分隔） | "LLM, API, CLI, PyTorch" |
| **summary** | TEXT | NULL | 📝 项目摘要 | "xllm - 高性能LLM推理引擎" |
| **relevance_score** | INTEGER | DEFAULT 0 | 📊 AI相关性评分 (1-10分) | 8 |

---

## 🗂️ 索引结构

| 索引名 | 字段 | 类型 | 用途 |
|--------|------|------|------|
| **PRIMARY** | id | UNIQUE | 主键，确保仓库唯一性 |
| **idx_repos_stars** | stars DESC | BTREE | 按星标数降序排序 |
| **idx_repos_owner** | owner | BTREE | 按所有者查询 |
| **idx_repos_created_at** | created_at | BTREE | 按创建时间查询 |
| **idx_repos_category** | category | BTREE | 按分类查询 |
| **idx_repos_relevance_score** | relevance_score DESC | BTREE | 按相关性评分排序 |

---

## 🤖 智能分类系统

### 项目分类 (`category` 字段)

| 分类名称 | 英文标识 | 说明 | 示例项目 |
|----------|----------|------|----------|
| **LLM服务与工具** | llm-services | LLM推理引擎、API服务、CLI工具 | xllm, osaurus, vllm-cli |
| **LLM应用** | llm-apps | 聊天应用、客户端界面 | hanlin-ai, SwiftAI |
| **LLM研究** | llm-research | 学术研究、算法论文实现 | semantic-router, ThinkMesh |
| **RAG技术** | rag-tech | 检索增强生成相关 | ComoRAG, medical-rag |
| **生成式AI** | generative-ai | 扩散模型、图像/视频生成 | StableAvatar, Stable Diffusion |
| **计算机视觉** | computer-vision | 图像识别、目标检测 | YOLO, OpenCV项目 |
| **AI资源与工具** | ai-resources | 数据集、框架、工具包 | ai-engineering-toolkit |
| **移动端AI** | mobile-ai | iOS/Android AI应用 | Flutter LLM客户端 |
| **智能体与强化学习** | agents-rl | 智能代理、强化学习 | nano-agent |
| **其他AI技术** | other-ai | 其他AI相关技术 | FastVGGT |

---

## 🏷️ 技术标签系统

### 标签分类 (`tags` 字段)

| 标签类别 | 标签示例 | 说明 |
|----------|----------|------|
| **核心技术** | LLM, Transformer, RAG, Diffusion | 主要AI技术栈 |
| **框架工具** | PyTorch, TensorFlow, Hugging Face | 开发框架 |
| **服务类型** | API, CLI, Chat, Mobile | 应用类型 |
| **厂商/平台** | OpenAI, Vector DB, Benchmark | 相关平台 |

### 标签提取规则
- 最多5个标签
- 逗号分隔
- 按重要性排序
- 自动从项目名称和描述中提取

---

## 📊 相关性评分系统

### 评分规则 (`relevance_score` 字段)

| 分数范围 | 质量等级 | 说明 | 示例项目 |
|----------|----------|------|----------|
| **8-10分** | 🥇 顶级 | 高权重关键词多次匹配 | osaurus (8分) |
| **6-7分** | 🥈 优秀 | 多个中高权重关键词匹配 | RLinf (7分), ComoRAG (6分) |
| **4-5分** | 🥉 良好 | 部分高权重关键词匹配 | xllm (4分) |
| **2-3分** | ✅ 合格 | 基本AI相关性确认 | semantic-router (3分) |
| **0-1分** | ❌ 不合格 | 相关性不足，被过滤 | - |

### 评分算法
- **高权重关键词** (+3分): 深度学习、LLM、计算机视觉等
- **中等权重关键词** (+1分): AI、ML、算法等
- **排除关键词** (-5分): UI框架、前端、区块链等
- **语言教程关键词** (-3分): 编程教程、练习等

---

## 📈 数据查询示例

### 1. 获取顶级LLM项目
```sql
SELECT name, summary, stars, relevance_score
FROM repos 
WHERE category = 'LLM服务与工具' 
ORDER BY relevance_score DESC, stars DESC 
LIMIT 10;
```

### 2. 按分类统计项目数量
```sql
SELECT category, COUNT(*) as count, AVG(stars) as avg_stars
FROM repos 
GROUP BY category 
ORDER BY count DESC;
```

### 3. 查找特定技术标签
```sql
SELECT name, summary, tags, stars
FROM repos 
WHERE tags LIKE '%PyTorch%' 
ORDER BY stars DESC;
```

### 4. 获取高质量项目
```sql
SELECT name, category, summary, relevance_score, stars
FROM repos 
WHERE relevance_score >= 6 AND stars >= 500
ORDER BY relevance_score DESC;
```

---

## 🔧 维护说明

### 数据更新频率
- **建议频率**: 每日更新
- **搜索范围**: 最近30天
- **星标阈值**: 100+ (可配置)

### 数据清理
- 自动去重（基于仓库ID）
- 更新已存在项目的星标数和描述
- 保留历史同步时间

### 配置文件
所有搜索参数可通过 `search_config.py` 进行调整：
- 星标要求
- 时间范围  
- 搜索领域
- 相关性阈值

---

## 📝 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2025-09-05 | 基础表结构，包含GitHub基本信息 |
| v2.0 | 2025-09-05 | 新增智能分类、标签、摘要和评分系统 |

---

*最后更新：2025年9月5日*
