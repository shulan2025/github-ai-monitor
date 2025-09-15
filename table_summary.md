# 🗄️ GitHub AI 仓库数据库表字段汇总

## 📊 核心字段表格

| 序号 | 字段名 | 类型 | 约束 | 功能说明 | 示例值 |
|:----:|--------|:----:|:----:|----------|---------|
| 1 | **id** | TEXT | 主键 | GitHub仓库唯一标识 | `"123456789"` |
| 2 | **name** | TEXT | 非空 | 仓库名称 | `"xllm"` |
| 3 | **owner** | TEXT | 非空 | 仓库所有者 | `"microsoft"` |
| 4 | **stars** | INTEGER | 默认0 | ⭐ 星标数量 | `1573` |
| 5 | **forks** | INTEGER | 默认0 | 🍴 Fork数量 | `245` |
| 6 | **description** | TEXT | 可空 | 📝 GitHub原始描述 | `"A high-performance inference engine"` |
| 7 | **url** | TEXT | 非空 | 🔗 仓库链接 | `"https://github.com/microsoft/xllm"` |
| 8 | **created_at** | TEXT | 可空 | 📅 创建时间 | `"2025-08-15T10:30:00Z"` |
| 9 | **updated_at** | TEXT | 可空 | 🔄 更新时间 | `"2025-09-05T14:20:00Z"` |
| 10 | **sync_time** | DATETIME | 当前时间 | ⏰ 同步时间 | `"2025-09-05 16:45:23"` |

## 🆕 智能功能字段

| 序号 | 字段名 | 类型 | 约束 | 功能说明 | 示例值 |
|:----:|--------|:----:|:----:|----------|---------|
| 11 | **category** | TEXT | 可空 | 🤖 **智能分类** | `"LLM服务与工具"` |
| 12 | **tags** | TEXT | 可空 | 🏷️ **技术标签** | `"LLM, API, CLI, PyTorch"` |
| 13 | **summary** | TEXT | 可空 | 📋 **项目摘要** | `"xllm - 高性能LLM推理引擎"` |
| 14 | **relevance_score** | INTEGER | 默认0 | 📊 **AI相关性评分** | `8` |

## 🗂️ 索引汇总

| 索引名称 | 索引字段 | 用途 |
|----------|----------|------|
| `PRIMARY` | id | 🔑 主键唯一性 |
| `idx_repos_stars` | stars DESC | ⭐ 按星标排序 |
| `idx_repos_category` | category | 🤖 按分类查询 |
| `idx_repos_relevance_score` | relevance_score DESC | 📊 按评分排序 |

## 🎯 分类系统速览

| 分类名称 | 项目数量 | 典型示例 |
|----------|:--------:|----------|
| **LLM服务与工具** | ~9个 | xllm, osaurus, vllm-cli |
| **LLM研究** | ~6个 | semantic-router, ThinkMesh |
| **LLM应用** | ~4个 | hanlin-ai, SwiftAI |
| **RAG技术** | ~2个 | ComoRAG, medical-rag |
| **生成式AI** | ~1个 | StableAvatar |
| **其他分类** | ~2个 | 计算机视觉、AI资源等 |

## 🏷️ 常用标签

| 技术标签 | 出现频率 | 说明 |
|----------|:--------:|------|
| **LLM** | 高 | 大语言模型相关 |
| **API** | 高 | 提供API服务 |
| **CLI** | 中 | 命令行工具 |
| **PyTorch** | 中 | 使用PyTorch框架 |
| **Chat** | 中 | 聊天/对话功能 |
| **Mobile** | 低 | 移动端应用 |

## 📊 评分分布

| 分数区间 | 质量等级 | 项目占比 | 说明 |
|:--------:|:--------:|:--------:|------|
| **8-10分** | 🥇 顶级 | ~4% | 极高AI相关性 |
| **6-7分** | 🥈 优秀 | ~12% | 高AI相关性 |
| **4-5分** | 🥉 良好 | ~33% | 中等AI相关性 |
| **2-3分** | ✅ 合格 | ~51% | 基本AI相关性 |

---

💡 **使用提示**: 
- 主要查询字段：`category`, `relevance_score`, `stars`
- 排序推荐：`ORDER BY relevance_score DESC, stars DESC`
- 筛选建议：`WHERE relevance_score >= 4 AND stars >= 100`
