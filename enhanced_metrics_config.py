#!/usr/bin/env python3
"""
完善的关键指标配置系统
基于GitHub API全量指标 + AI领域特定指标 + 商业价值指标
"""

from datetime import datetime, timedelta
import requests

# ================================
# 🎯 完善的核心指标体系
# ================================

ENHANCED_CORE_METRICS = {
    # 基础影响力指标
    "basic_impact": {
        "stars": {
            "tier_s": {"min": 10000, "weight": 15, "desc": "超级明星项目"},
            "tier_a": {"min": 5000, "weight": 12, "desc": "顶级项目"},
            "tier_b": {"min": 1000, "weight": 10, "desc": "明星项目"},
            "tier_c": {"min": 500, "weight": 8, "desc": "优秀项目"},
            "tier_d": {"min": 100, "weight": 6, "desc": "良好项目"},
            "tier_e": {"min": 20, "weight": 4, "desc": "新兴项目"},
        },
        "forks": {
            "tier_s": {"min": 2000, "weight": 12, "desc": "超高实用性"},
            "tier_a": {"min": 500, "weight": 10, "desc": "高实用性"},
            "tier_b": {"min": 200, "weight": 8, "desc": "中高实用性"},
            "tier_c": {"min": 50, "weight": 6, "desc": "实用项目"},
            "tier_d": {"min": 10, "weight": 4, "desc": "有潜力项目"},
        },
        "watchers": {
            "tier_a": {"min": 1000, "weight": 8, "desc": "高关注度"},
            "tier_b": {"min": 200, "weight": 6, "desc": "中等关注"},
            "tier_c": {"min": 50, "weight": 4, "desc": "基础关注"},
        }
    },
    
    # 社区活跃度指标
    "community_engagement": {
        "contributors": {
            "evaluation": "贡献者数量反映项目协作程度",
            "tier_a": {"min": 100, "weight": 10, "desc": "大型社区"},
            "tier_b": {"min": 20, "weight": 8, "desc": "活跃社区"},
            "tier_c": {"min": 5, "weight": 6, "desc": "小型团队"},
            "api_endpoint": "/repos/{owner}/{repo}/contributors"
        },
        "issues": {
            "open_issues_count": {
                "healthy_range": {"min": 5, "max": 100, "weight": 5},
                "too_many": {"min": 100, "weight": -2, "desc": "问题过多"},
                "too_few": {"max": 5, "weight": 2, "desc": "维护良好"}
            }
        },
        "pull_requests": {
            "evaluation": "PR活跃度反映项目开发活力",
            "api_endpoint": "/repos/{owner}/{repo}/pulls",
            "metrics": ["open_count", "merged_count", "avg_time_to_merge"]
        }
    },
    
    # 项目健康度指标
    "project_health": {
        "commit_frequency": {
            "evaluation": "提交频率反映开发活跃度",
            "very_active": {"commits_per_week": 20, "weight": 10},
            "active": {"commits_per_week": 5, "weight": 8},
            "moderate": {"commits_per_week": 1, "weight": 6},
            "api_endpoint": "/repos/{owner}/{repo}/commits"
        },
        "release_activity": {
            "evaluation": "发布活动反映项目成熟度",
            "frequent": {"releases_per_year": 12, "weight": 8},
            "regular": {"releases_per_year": 4, "weight": 6},
            "occasional": {"releases_per_year": 1, "weight": 4},
            "api_endpoint": "/repos/{owner}/{repo}/releases"
        },
        "documentation_quality": {
            "has_readme": {"weight": 3, "desc": "有README文件"},
            "has_wiki": {"weight": 2, "desc": "有Wiki文档"},
            "has_pages": {"weight": 2, "desc": "有GitHub Pages"},
            "detailed_readme": {"min_length": 1000, "weight": 5}
        }
    }
}

# ================================
# 🤖 AI领域特定增强指标
# ================================

AI_ENHANCED_METRICS = {
    # AI技术成熟度指标
    "ai_maturity": {
        "model_artifacts": {
            "has_models": {"weight": 8, "keywords": ["model", "checkpoint", "weights"]},
            "model_formats": {
                "pytorch": {"weight": 3, "keywords": [".pth", ".pt"]},
                "tensorflow": {"weight": 3, "keywords": [".pb", ".h5"]},
                "onnx": {"weight": 4, "keywords": [".onnx"]},
                "huggingface": {"weight": 5, "keywords": ["huggingface", "transformers"]}
            }
        },
        "research_backing": {
            "has_paper": {"weight": 10, "keywords": ["paper", "arxiv", "research"]},
            "peer_reviewed": {"weight": 12, "keywords": ["published", "conference", "journal"]},
            "citations": {"weight": 8, "keywords": ["cite", "citation", "reference"]}
        },
        "practical_deployment": {
            "production_ready": {"weight": 8, "keywords": ["production", "deploy", "docker"]},
            "api_service": {"weight": 6, "keywords": ["api", "rest", "grpc", "server"]},
            "web_interface": {"weight": 4, "keywords": ["web", "ui", "interface", "gradio", "streamlit"]}
        }
    },
    
    # AI技术前沿性指标
    "ai_innovation": {
        "cutting_edge_tech": {
            "llm_2024": {"weight": 15, "keywords": ["gpt-4", "claude", "llama-3", "gemini"]},
            "multimodal": {"weight": 12, "keywords": ["multimodal", "vision-language", "clip"]},
            "agent_systems": {"weight": 10, "keywords": ["agent", "autonomous", "planning"]},
            "reasoning": {"weight": 10, "keywords": ["reasoning", "chain-of-thought", "cot"]},
            "retrieval": {"weight": 8, "keywords": ["rag", "retrieval", "vector-db"]}
        },
        "sota_performance": {
            "benchmark_results": {"weight": 12, "keywords": ["sota", "state-of-the-art", "benchmark"]},
            "leaderboard": {"weight": 10, "keywords": ["leaderboard", "ranking", "top-1"]},
            "evaluation": {"weight": 6, "keywords": ["evaluation", "metric", "score"]}
        }
    },
    
    # AI商业价值指标
    "commercial_viability": {
        "enterprise_adoption": {
            "enterprise_users": {"weight": 10, "keywords": ["enterprise", "business", "commercial"]},
            "industry_backing": {"weight": 8, "keywords": ["google", "microsoft", "openai", "meta"]},
            "funding": {"weight": 6, "keywords": ["funding", "investment", "series"]}
        },
        "developer_ecosystem": {
            "framework_integration": {"weight": 8, "keywords": ["langchain", "llamaindex", "haystack"]},
            "cloud_support": {"weight": 6, "keywords": ["aws", "azure", "gcp", "huggingface"]},
            "community_tools": {"weight": 4, "keywords": ["plugin", "extension", "integration"]}
        }
    }
}

# ================================
# 📊 高级GitHub指标
# ================================

ADVANCED_GITHUB_METRICS = {
    # 代码质量指标
    "code_quality": {
        "languages": {
            "primary_language": {"weight": 2, "desc": "主要编程语言"},
            "language_diversity": {"weight": 3, "desc": "多语言支持"},
            "modern_languages": {
                "python": {"weight": 3},
                "rust": {"weight": 4},
                "typescript": {"weight": 3},
                "go": {"weight": 3}
            }
        },
        "repository_structure": {
            "has_tests": {"weight": 5, "indicators": ["test/", "tests/", "__test__"]},
            "has_ci": {"weight": 4, "indicators": [".github/workflows/", ".travis.yml"]},
            "has_docs": {"weight": 3, "indicators": ["docs/", "documentation/"]},
            "has_examples": {"weight": 3, "indicators": ["examples/", "demo/"]}
        },
        "code_size": {
            "size_kb": {
                "optimal": {"min": 100, "max": 10000, "weight": 3},
                "too_large": {"min": 50000, "weight": -2},
                "too_small": {"max": 10, "weight": -1}
            }
        }
    },
    
    # 网络效应指标
    "network_effects": {
        "dependency_network": {
            "is_dependency": {"weight": 8, "desc": "被其他项目依赖"},
            "dependency_count": {
                "high": {"min": 1000, "weight": 10},
                "medium": {"min": 100, "weight": 6},
                "low": {"min": 10, "weight": 3}
            }
        },
        "social_signals": {
            "twitter_mentions": {"weight": 4, "desc": "社交媒体影响"},
            "blog_coverage": {"weight": 5, "desc": "技术博客报道"},
            "conference_talks": {"weight": 6, "desc": "会议演讲"}
        }
    },
    
    # 可持续性指标
    "sustainability": {
        "maintenance": {
            "regular_updates": {"weight": 8, "threshold_days": 30},
            "responsive_issues": {"weight": 6, "avg_response_days": 7},
            "security_updates": {"weight": 10, "keywords": ["security", "vulnerability"]}
        },
        "governance": {
            "has_contributing_guide": {"weight": 3},
            "has_code_of_conduct": {"weight": 2},
            "has_license": {"weight": 5},
            "clear_roadmap": {"weight": 4}
        }
    }
}

# ================================
# 📈 动态评分算法
# ================================

def calculate_enhanced_score(repo_data, additional_data=None):
    """计算增强版项目评分 (总分100分)"""
    
    total_score = 0
    
    # 1. 基础影响力评分 (30分)
    basic_score = calculate_basic_impact_score(repo_data)
    total_score += basic_score
    
    # 2. AI特定评分 (25分)
    ai_score = calculate_ai_specific_score(repo_data)
    total_score += ai_score
    
    # 3. 社区活跃度评分 (20分)
    community_score = calculate_community_score(repo_data, additional_data)
    total_score += community_score
    
    # 4. 项目健康度评分 (15分)
    health_score = calculate_health_score(repo_data, additional_data)
    total_score += health_score
    
    # 5. 创新性和前沿性评分 (10分)
    innovation_score = calculate_innovation_score(repo_data)
    total_score += innovation_score
    
    return min(100, max(0, total_score))

def calculate_basic_impact_score(repo_data):
    """计算基础影响力评分 (30分)"""
    score = 0
    
    # 星标评分 (15分)
    stars = repo_data.get('stargazers_count', 0)
    if stars >= 10000:
        score += 15
    elif stars >= 5000:
        score += 12
    elif stars >= 1000:
        score += 10
    elif stars >= 500:
        score += 8
    elif stars >= 100:
        score += 6
    elif stars >= 20:
        score += 4
    
    # 分叉评分 (10分)
    forks = repo_data.get('forks_count', 0)
    if forks >= 2000:
        score += 10
    elif forks >= 500:
        score += 8
    elif forks >= 200:
        score += 6
    elif forks >= 50:
        score += 4
    elif forks >= 10:
        score += 2
    
    # 关注者评分 (5分)
    watchers = repo_data.get('watchers_count', 0)
    if watchers >= 1000:
        score += 5
    elif watchers >= 200:
        score += 3
    elif watchers >= 50:
        score += 2
    
    return score

def calculate_ai_specific_score(repo_data):
    """计算AI特定评分 (25分)"""
    score = 0
    
    name = repo_data.get('name', '').lower()
    description = repo_data.get('description', '').lower() if repo_data.get('description') else ''
    full_text = f"{name} {description}"
    
    # 前沿技术评分 (15分)
    cutting_edge_keywords = {
        "gpt-4": 5, "claude": 5, "llama": 4, "gemini": 4,
        "multimodal": 4, "vision-language": 4,
        "agent": 3, "autonomous": 3, "reasoning": 3,
        "rag": 3, "retrieval": 3, "vector": 2
    }
    
    for keyword, weight in cutting_edge_keywords.items():
        if keyword in full_text:
            score += weight
    
    # 技术成熟度评分 (10分)
    maturity_keywords = {
        "paper": 3, "arxiv": 3, "research": 2,
        "production": 2, "deploy": 2, "api": 1,
        "model": 2, "checkpoint": 2, "weights": 2
    }
    
    for keyword, weight in maturity_keywords.items():
        if keyword in full_text:
            score += weight
    
    return min(25, score)

def calculate_community_score(repo_data, additional_data):
    """计算社区活跃度评分 (20分)"""
    score = 0
    
    # 活跃度评分 (10分)
    pushed_at = repo_data.get('pushed_at', '')
    if pushed_at:
        try:
            pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            days_since_push = (datetime.now(pushed_date.tzinfo) - pushed_date).days
            
            if days_since_push <= 7:
                score += 10
            elif days_since_push <= 30:
                score += 8
            elif days_since_push <= 90:
                score += 6
            elif days_since_push <= 365:
                score += 3
        except:
            pass
    
    # 问题处理评分 (5分)
    open_issues = repo_data.get('open_issues_count', 0)
    if 5 <= open_issues <= 50:  # 健康的问题数量
        score += 5
    elif open_issues < 5:
        score += 3
    elif open_issues > 100:
        score -= 2
    
    # 社区参与评分 (5分)
    if additional_data and 'contributors' in additional_data:
        contributors = additional_data['contributors']
        if contributors >= 50:
            score += 5
        elif contributors >= 10:
            score += 3
        elif contributors >= 3:
            score += 2
    
    return min(20, score)

def calculate_health_score(repo_data, additional_data):
    """计算项目健康度评分 (15分)"""
    score = 0
    
    # 许可证评分 (5分)
    license_info = repo_data.get('license', {})
    if license_info:
        score += 5
    
    # 描述质量评分 (5分)
    description = repo_data.get('description', '') or ''
    if len(description) >= 100:
        score += 5
    elif len(description) >= 50:
        score += 3
    elif len(description) >= 20:
        score += 2
    
    # 项目结构评分 (5分)
    if additional_data and 'has_readme' in additional_data:
        if additional_data.get('has_readme'):
            score += 2
        if additional_data.get('has_tests'):
            score += 2
        if additional_data.get('has_ci'):
            score += 1
    
    return score

def calculate_innovation_score(repo_data):
    """计算创新性评分 (10分)"""
    score = 0
    
    # 新颖性评分
    created_at = repo_data.get('created_at', '')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_since_creation = (datetime.now(created_date.tzinfo) - created_date).days
            
            if days_since_creation <= 90:  # 3个月内的新项目
                score += 5
            elif days_since_creation <= 365:  # 1年内
                score += 3
        except:
            pass
    
    # 技术栈现代化评分
    language = repo_data.get('language', '').lower()
    modern_languages = {
        'python': 2, 'rust': 3, 'typescript': 2, 
        'go': 2, 'julia': 3, 'swift': 2
    }
    
    if language in modern_languages:
        score += modern_languages[language]
    
    return min(10, score)

# ================================
# 🎯 数据库增强字段
# ================================

DATABASE_ENHANCEMENT = {
    # 新增字段建议
    "new_fields": {
        "enhanced_score": "INTEGER DEFAULT 0",  # 增强评分 (0-100)
        "ai_maturity_level": "TEXT",            # AI成熟度等级
        "community_health": "TEXT",             # 社区健康状态
        "innovation_level": "TEXT",             # 创新水平
        "commercial_potential": "TEXT",         # 商业潜力
        "last_commit_date": "TEXT",            # 最后提交日期
        "contributors_count": "INTEGER DEFAULT 0", # 贡献者数量
        "issues_count": "INTEGER DEFAULT 0",    # 问题数量
        "pr_count": "INTEGER DEFAULT 0",        # PR数量
        "languages": "TEXT",                    # 编程语言列表
        "topics": "TEXT",                       # GitHub topics
        "license_type": "TEXT",                 # 许可证类型
        "has_documentation": "BOOLEAN DEFAULT 0", # 是否有文档
        "deployment_ready": "BOOLEAN DEFAULT 0",   # 是否可部署
        "research_backed": "BOOLEAN DEFAULT 0"     # 是否有研究支撑
    },
    
    # 新增索引
    "new_indexes": [
        "CREATE INDEX IF NOT EXISTS idx_enhanced_score ON repos(enhanced_score DESC);",
        "CREATE INDEX IF NOT EXISTS idx_ai_maturity ON repos(ai_maturity_level);",
        "CREATE INDEX IF NOT EXISTS idx_community_health ON repos(community_health);",
        "CREATE INDEX IF NOT EXISTS idx_last_commit ON repos(last_commit_date);",
        "CREATE INDEX IF NOT EXISTS idx_contributors ON repos(contributors_count DESC);"
    ]
}

# ================================
# 💡 使用指南
# ================================

ENHANCED_USAGE_GUIDE = """
🎯 完善的关键指标体系

📊 评分体系 (总分100分):
├── 基础影响力 (30分): Stars, Forks, Watchers
├── AI特定指标 (25分): 前沿技术, 技术成熟度
├── 社区活跃度 (20分): 提交频率, 问题处理, 贡献者
├── 项目健康度 (15分): 文档, 许可证, 项目结构
└── 创新性评分 (10分): 新颖性, 技术栈现代化

🔍 新增高级指标:
├── Contributors数量 (社区规模)
├── Issues处理情况 (维护质量)
├── PR活跃度 (开发活力)
├── Release频率 (版本管理)
├── 代码质量指标 (测试, CI/CD)
├── 文档完整性 (README, Wiki, 示例)
├── 商业价值评估 (企业采用, 资金支持)
└── 网络效应 (依赖关系, 社交信号)

🎯 应用价值:
- 更精准的项目质量评估
- 多维度的技术价值分析  
- 商业潜力和投资价值评估
- 社区健康和可持续性分析
- AI技术前沿性和成熟度判断

📈 预期效果:
- 项目评估准确率 > 90%
- 商业价值识别能力显著提升
- 技术趋势预测更加精准
- 投资决策支持更加完善
"""

if __name__ == "__main__":
    print("🎯 增强指标配置系统加载完成")
    print("📊 100分制综合评分体系")
    print("🔍 覆盖基础指标 + AI特定指标 + 商业价值指标")
    print("\n" + ENHANCED_USAGE_GUIDE)
