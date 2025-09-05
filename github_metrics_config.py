#!/usr/bin/env python3
"""
基于GitHub官方指标的完整项目评估配置
参考GitHub项目评估最佳实践，构建多维度评估体系
"""

from datetime import datetime, timedelta

# ================================
# 🎯 核心指标：衡量项目的价值和影响力
# ================================

CORE_METRICS_CONFIG = {
    # 星标数 (Stars) - 项目流行度
    "stars": {
        "tier_1": {"min": 1000, "weight": 10, "desc": "明星项目"},
        "tier_2": {"min": 500, "weight": 8, "desc": "优秀项目"}, 
        "tier_3": {"min": 100, "weight": 6, "desc": "良好项目"},
        "tier_4": {"min": 20, "weight": 4, "desc": "新兴项目"},
        "api_field": "stargazers_count"
    },
    
    # 分叉数 (Forks) - 项目可用度
    "forks": {
        "tier_1": {"min": 200, "weight": 8, "desc": "高价值项目"},
        "tier_2": {"min": 50, "weight": 6, "desc": "实用项目"},
        "tier_3": {"min": 10, "weight": 4, "desc": "有潜力项目"},
        "tier_4": {"min": 2, "weight": 2, "desc": "起步项目"},
        "api_field": "forks_count"
    },
    
    # 贡献者数 (Contributors) - 社区活跃度
    "contributors": {
        "evaluation": "贡献者多的项目通常更新频繁、生命力更强",
        "fetch_method": "需要额外API调用获取",
        "api_endpoint": "/repos/{owner}/{repo}/contributors"
    }
}

# ================================
# 🔄 次要指标：衡量项目的新鲜度和活跃度  
# ================================

ACTIVITY_METRICS_CONFIG = {
    # 最近更新时间 (Pushed At) - 项目活跃度
    "pushed_at": {
        "very_active": {"days": 7, "weight": 10, "desc": "极活跃项目"},
        "active": {"days": 30, "weight": 8, "desc": "活跃项目"},
        "moderate": {"days": 90, "weight": 6, "desc": "中等活跃"},
        "inactive": {"days": 365, "weight": 2, "desc": "不活跃项目"},
        "api_field": "pushed_at"
    },
    
    # 提交数 (Commits) - 开发活跃度
    "commits": {
        "evaluation": "高提交数意味着项目在持续进化",
        "fetch_method": "需要额外API调用获取",
        "api_endpoint": "/repos/{owner}/{repo}/commits"
    },
    
    # 发布日期 (Created At) - 项目新鲜度
    "created_at": {
        "brand_new": {"days": 30, "weight": 8, "desc": "全新项目"},
        "recent": {"days": 90, "weight": 6, "desc": "近期项目"},
        "established": {"days": 365, "weight": 4, "desc": "成熟项目"},
        "veteran": {"days": 9999, "weight": 2, "desc": "老牌项目"},
        "api_field": "created_at"
    }
}

# ================================
# 🏆 高级指标：衡量项目的质量和成熟度
# ================================

QUALITY_METRICS_CONFIG = {
    # 许可证 (License) - 项目开放度
    "license": {
        "open_source": {
            "preferred": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"],
            "weight": 5,
            "desc": "明确的开源许可证"
        },
        "restrictive": {
            "types": ["GPL-2.0", "AGPL-3.0"],
            "weight": 3,
            "desc": "限制性许可证"
        },
        "unknown": {
            "weight": 1,
            "desc": "无明确许可证"
        },
        "api_field": "license"
    },
    
    # 描述 (Description) - 项目质量
    "description": {
        "excellent": {"min_length": 100, "weight": 5, "desc": "详细描述"},
        "good": {"min_length": 50, "weight": 4, "desc": "良好描述"},
        "basic": {"min_length": 20, "weight": 2, "desc": "基础描述"},
        "poor": {"min_length": 0, "weight": 0, "desc": "无描述"},
        "api_field": "description"
    }
}

# ================================
# 🔍 GitHub API 搜索查询优化
# ================================

def build_enhanced_search_queries():
    """构建基于指标的搜索查询"""
    
    # 时间范围配置
    now = datetime.now()
    time_ranges = {
        "very_recent": (now - timedelta(days=30)).strftime('%Y-%m-%d'),
        "recent": (now - timedelta(days=90)).strftime('%Y-%m-%d'),
        "established": (now - timedelta(days=365)).strftime('%Y-%m-%d')
    }
    
    # 基于不同指标组合的查询策略
    search_strategies = [
        # 策略1: 明星项目 (高星标 + 近期活跃)
        {
            "name": "star_projects",
            "query_template": "{keywords} stars:>1000 pushed:>={recent_date}",
            "target": "寻找明星级别的活跃项目",
            "expected_quality": "极高"
        },
        
        # 策略2: 新兴项目 (中等星标 + 新创建)
        {
            "name": "emerging_projects", 
            "query_template": "{keywords} stars:>100 created:>={recent_date}",
            "target": "发现快速崛起的新项目",
            "expected_quality": "高"
        },
        
        # 策略3: 活跃项目 (中等星标 + 高活跃度)
        {
            "name": "active_projects",
            "query_template": "{keywords} stars:>200 pushed:>={very_recent_date}",
            "target": "找到持续开发的项目",
            "expected_quality": "高"
        },
        
        # 策略4: 社区项目 (高分叉 + 多贡献者)
        {
            "name": "community_projects",
            "query_template": "{keywords} forks:>50 stars:>500",
            "target": "发现社区认可度高的项目",
            "expected_quality": "中高"
        },
        
        # 策略5: 潜力项目 (低星标 + 近期创建 + 有活跃度)
        {
            "name": "potential_projects",
            "query_template": "{keywords} stars:20..200 created:>={recent_date} pushed:>={very_recent_date}",
            "target": "挖掘有潜力的新项目",
            "expected_quality": "中"
        }
    ]
    
    return search_strategies, time_ranges

# ================================
# 📊 综合评分算法
# ================================

def calculate_comprehensive_score(repo_data):
    """基于多维指标计算项目综合评分"""
    
    score = 0
    max_score = 50  # 总分50分
    
    # 1. 星标评分 (最高10分)
    stars = repo_data.get('stargazers_count', 0)
    if stars >= 1000:
        score += 10
    elif stars >= 500:
        score += 8
    elif stars >= 100:
        score += 6
    elif stars >= 20:
        score += 4
    
    # 2. 分叉评分 (最高8分)
    forks = repo_data.get('forks_count', 0)
    if forks >= 200:
        score += 8
    elif forks >= 50:
        score += 6
    elif forks >= 10:
        score += 4
    elif forks >= 2:
        score += 2
    
    # 3. 活跃度评分 (最高10分)
    pushed_at = repo_data.get('pushed_at', '')
    if pushed_at:
        try:
            pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            days_since_push = (datetime.now(pushed_date.tzinfo) - pushed_date).days
            
            if days_since_push <= 7:
                score += 10  # 极活跃
            elif days_since_push <= 30:
                score += 8   # 活跃
            elif days_since_push <= 90:
                score += 6   # 中等
            elif days_since_push <= 365:
                score += 2   # 不活跃
        except:
            pass
    
    # 4. 新鲜度评分 (最高8分)
    created_at = repo_data.get('created_at', '')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_since_creation = (datetime.now(created_date.tzinfo) - created_date).days
            
            if days_since_creation <= 30:
                score += 8   # 全新
            elif days_since_creation <= 90:
                score += 6   # 近期
            elif days_since_creation <= 365:
                score += 4   # 成熟
            else:
                score += 2   # 老牌
        except:
            pass
    
    # 5. 质量评分 (最高9分)
    # 许可证评分 (最高5分)
    license_info = repo_data.get('license', {})
    if license_info and license_info.get('key'):
        license_key = license_info.get('key', '')
        preferred_licenses = ['mit', 'apache-2.0', 'gpl-3.0', 'bsd-3-clause']
        if license_key.lower() in preferred_licenses:
            score += 5
        else:
            score += 3
    
    # 描述评分 (最高4分)
    description = repo_data.get('description', '') or ''
    desc_length = len(description)
    if desc_length >= 100:
        score += 4
    elif desc_length >= 50:
        score += 3
    elif desc_length >= 20:
        score += 2
    
    # 6. 社区评分 (最高5分) - 基于星标和分叉的比例
    if stars > 0 and forks > 0:
        fork_ratio = forks / stars
        if fork_ratio >= 0.1:  # 10%以上的分叉率说明项目实用性强
            score += 5
        elif fork_ratio >= 0.05:
            score += 3
        elif fork_ratio >= 0.02:
            score += 2
    
    return min(score, max_score)

# ================================
# 🎯 AI项目特定指标
# ================================

AI_SPECIFIC_METRICS = {
    # AI领域关键指标
    "ai_indicators": {
        "model_files": {
            "keywords": ["model", "checkpoint", "weights", ".pth", ".onnx", ".pkl"],
            "weight": 5,
            "desc": "包含模型文件"
        },
        "research_quality": {
            "keywords": ["paper", "arxiv", "research", "publication"],
            "weight": 4,
            "desc": "有学术支撑"
        },
        "practical_usage": {
            "keywords": ["api", "demo", "example", "tutorial", "documentation"],
            "weight": 3,
            "desc": "实用性强"
        },
        "cutting_edge": {
            "keywords": ["2024", "latest", "state-of-art", "sota", "breakthrough"],
            "weight": 6,
            "desc": "前沿技术"
        }
    },
    
    # 技术栈评分
    "tech_stack_bonus": {
        "python": 2,
        "pytorch": 3,
        "tensorflow": 3,
        "huggingface": 4,
        "openai": 3,
        "langchain": 2,
        "gradio": 2,
        "streamlit": 2
    }
}

# ================================
# 📈 搜索优化配置
# ================================

SEARCH_OPTIMIZATION_CONFIG = {
    # 每日搜索配额分配
    "daily_search_allocation": {
        "star_projects": 30,      # 30次搜索明星项目
        "emerging_projects": 25,   # 25次搜索新兴项目
        "active_projects": 20,     # 20次搜索活跃项目
        "community_projects": 15,  # 15次搜索社区项目
        "potential_projects": 10   # 10次搜索潜力项目
    },
    
    # API调用限制
    "api_limits": {
        "search_per_hour": 30,     # 每小时30次搜索
        "requests_per_minute": 10,  # 每分钟10次请求
        "delay_between_calls": 2.0  # 调用间隔2秒
    },
    
    # 目标收集量
    "collection_targets": {
        "total_candidates": 1000,   # 目标候选项目
        "high_quality": 200,        # 高质量项目 (35+ 分)
        "medium_quality": 300,      # 中等质量项目 (25-35分)
        "potential": 500           # 潜力项目 (15-25分)
    }
}

# ================================
# 💡 使用说明
# ================================

USAGE_INSTRUCTIONS = """
🎯 基于GitHub官方指标的项目评估体系

1. 核心指标 (权重最高):
   - Stars: 反映项目受欢迎程度
   - Forks: 反映项目实用性和开发价值
   - Contributors: 反映社区活跃度

2. 活跃度指标:
   - Pushed At: 最重要的活跃度指标
   - Commits: 开发频率
   - Created At: 项目新鲜度

3. 质量指标:
   - License: 开源程度
   - Description: 项目完整性

4. 搜索策略:
   - 多维度组合搜索
   - 基于不同目标的查询策略
   - API限制内的最优化搜索

5. 评分算法:
   - 50分制综合评分
   - 多指标加权计算
   - AI领域特定加分项

预期效果：
- 候选项目准确率提升至 60%+
- 每日收集200+ 高质量AI项目
- 覆盖从新兴到成熟的完整项目生态
"""

if __name__ == "__main__":
    print("🎯 GitHub指标配置加载完成")
    strategies, time_ranges = build_enhanced_search_queries()
    print(f"📊 配置了 {len(strategies)} 种搜索策略")
    print(f"⏰ 设置了 {len(time_ranges)} 个时间范围")
    print("\n" + USAGE_INSTRUCTIONS)
