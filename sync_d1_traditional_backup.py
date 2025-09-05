#!/usr/bin/env python3
"""
基于GitHub官方指标的智能AI项目收集脚本
使用多维度评估体系，目标每天200+条高质量数据
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from cloudflare import Cloudflare
from dotenv import load_dotenv
from github_metrics_config import (
    CORE_METRICS_CONFIG, ACTIVITY_METRICS_CONFIG, QUALITY_METRICS_CONFIG,
    AI_SPECIFIC_METRICS, SEARCH_OPTIMIZATION_CONFIG,
    build_enhanced_search_queries, calculate_comprehensive_score
)

# 加载环境变量
load_dotenv()

# === 配置 ===
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN") 
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID")

if not all([GITHUB_TOKEN, CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, D1_DATABASE_ID]):
    raise ValueError("环境变量未设置。请确保所有必要的环境变量都已正确配置。")

# 初始化客户端
cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ================================
# 🔍 基于指标的搜索执行
# ================================

def execute_metrics_based_search(strategy, keywords, time_ranges):
    """基于指标执行搜索"""
    
    # 构建查询
    if strategy["name"] == "star_projects":
        query = strategy["query_template"].format(
            keywords=keywords,
            recent_date=time_ranges["recent"]
        )
    elif strategy["name"] == "emerging_projects":
        query = strategy["query_template"].format(
            keywords=keywords, 
            recent_date=time_ranges["recent"]
        )
    elif strategy["name"] == "active_projects":
        query = strategy["query_template"].format(
            keywords=keywords,
            very_recent_date=time_ranges["very_recent"]
        )
    elif strategy["name"] == "potential_projects":
        query = strategy["query_template"].format(
            keywords=keywords,
            recent_date=time_ranges["recent"],
            very_recent_date=time_ranges["very_recent"]
        )
    else:
        query = strategy["query_template"].format(keywords=keywords)
    
    # 添加基础过滤条件
    query += " is:public archived:false"
    
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 100
    }
    
    try:
        print(f"🔍 {strategy['name']}: {keywords[:30]}")
        print(f"   查询: {query[:80]}...")
        
        response = requests.get(
            "https://api.github.com/search/repositories",
            headers=github_headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        repos = data.get("items", [])
        total_count = data.get("total_count", 0)
        
        print(f"   📊 找到 {total_count} 个项目，获取前 {len(repos)} 个")
        
        return repos
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 搜索失败: {e}")
        return []

def enhance_repo_with_metrics(repo):
    """用指标数据增强仓库信息"""
    
    # 计算综合评分
    comprehensive_score = calculate_comprehensive_score(repo)
    
    # AI特定评分
    ai_score = calculate_ai_specific_score(repo)
    
    # 最终评分
    final_score = min(50, comprehensive_score + ai_score)
    
    # 项目分类
    category = classify_by_metrics(repo)
    
    # 质量等级
    quality_level = determine_quality_level(final_score)
    
    # 活跃度状态
    activity_status = determine_activity_status(repo)
    
    # 社区影响力
    community_impact = calculate_community_impact(repo)
    
    enhanced_repo = repo.copy()
    enhanced_repo.update({
        "comprehensive_score": comprehensive_score,
        "ai_specific_score": ai_score,
        "final_score": final_score,
        "category": category,
        "quality_level": quality_level,
        "activity_status": activity_status,
        "community_impact": community_impact,
        "metrics_timestamp": datetime.now().isoformat()
    })
    
    return enhanced_repo

def calculate_ai_specific_score(repo):
    """计算AI领域特定评分"""
    name = repo.get("name", "").lower()
    description = repo.get("description", "").lower() if repo.get("description") else ""
    full_text = f"{name} {description}"
    
    ai_score = 0
    
    # AI指标评分
    for indicator, config in AI_SPECIFIC_METRICS["ai_indicators"].items():
        matches = sum(1 for keyword in config["keywords"] if keyword in full_text)
        if matches > 0:
            ai_score += config["weight"]
    
    # 技术栈加分
    for tech, bonus in AI_SPECIFIC_METRICS["tech_stack_bonus"].items():
        if tech in full_text:
            ai_score += bonus
    
    return min(15, ai_score)  # AI特定评分最高15分

def classify_by_metrics(repo):
    """基于指标数据进行项目分类"""
    name = repo.get("name", "").lower()
    description = repo.get("description", "").lower() if repo.get("description") else ""
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    
    full_text = f"{name} {description}"
    
    # 基于星标和分叉数判断项目类型
    if stars >= 1000:
        project_tier = "明星项目"
    elif stars >= 500:
        project_tier = "优秀项目"
    elif stars >= 100:
        project_tier = "良好项目"
    else:
        project_tier = "新兴项目"
    
    # 基于内容判断技术分类
    if any(keyword in full_text for keyword in ["llm", "gpt", "language model", "transformer"]):
        if any(keyword in full_text for keyword in ["api", "server", "serving"]):
            tech_category = "LLM服务"
        elif any(keyword in full_text for keyword in ["chat", "assistant", "bot"]):
            tech_category = "LLM应用"
        else:
            tech_category = "LLM研究"
    elif any(keyword in full_text for keyword in ["diffusion", "stable-diffusion", "image generation"]):
        tech_category = "生成式AI"
    elif any(keyword in full_text for keyword in ["computer vision", "object detection", "yolo"]):
        tech_category = "计算机视觉"
    elif any(keyword in full_text for keyword in ["rag", "retrieval", "vector", "embedding"]):
        tech_category = "RAG技术"
    elif any(keyword in full_text for keyword in ["data science", "analytics", "visualization"]):
        tech_category = "数据科学"
    else:
        tech_category = "通用AI"
    
    return f"{tech_category} - {project_tier}"

def determine_quality_level(score):
    """根据评分确定质量等级"""
    if score >= 40:
        return "顶级项目 (40+ 分)"
    elif score >= 30:
        return "优秀项目 (30-39 分)"
    elif score >= 20:
        return "良好项目 (20-29 分)"
    elif score >= 10:
        return "潜力项目 (10-19 分)"
    else:
        return "基础项目 (< 10 分)"

def determine_activity_status(repo):
    """确定项目活跃状态"""
    pushed_at = repo.get("pushed_at", "")
    
    if not pushed_at:
        return "未知状态"
    
    try:
        pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
        days_ago = (datetime.now(pushed_date.tzinfo) - pushed_date).days
        
        if days_ago <= 7:
            return "极活跃 (7天内更新)"
        elif days_ago <= 30:
            return "活跃 (30天内更新)"
        elif days_ago <= 90:
            return "中等活跃 (90天内更新)"
        elif days_ago <= 365:
            return "不够活跃 (一年内更新)"
        else:
            return "不活跃 (超过一年)"
    except:
        return "状态解析失败"

def calculate_community_impact(repo):
    """计算社区影响力"""
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    
    if stars == 0:
        return "无影响力"
    
    fork_ratio = forks / stars if stars > 0 else 0
    
    if stars >= 1000 and fork_ratio >= 0.1:
        return "高影响力"
    elif stars >= 500 and fork_ratio >= 0.05:
        return "中等影响力"  
    elif stars >= 100:
        return "一定影响力"
    else:
        return "初步影响力"

# ================================
# 🎯 数据处理和保存
# ================================

def filter_and_process_repos(repos):
    """过滤和处理仓库数据"""
    processed = []
    
    for repo in repos:
        try:
            # 基础过滤
            if repo.get("fork", False):
                continue
            
            if repo.get("archived", False):
                continue
            
            # 描述长度过滤
            description = repo.get("description", "") or ""
            if len(description) < 15:
                continue
            
            # 使用指标增强
            enhanced_repo = enhance_repo_with_metrics(repo)
            
            # 质量过滤：只保留10分以上的项目
            if enhanced_repo["final_score"] < 10:
                continue
            
            # 构建保存数据
            processed_repo = {
                "id": str(repo.get("id")),
                "name": repo.get("name"),
                "owner": repo.get("owner", {}).get("login"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "description": description,
                "url": repo.get("html_url"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("pushed_at"),
                "category": enhanced_repo["category"],
                "tags": extract_metrics_tags(enhanced_repo),
                "summary": generate_metrics_summary(enhanced_repo),
                "relevance_score": enhanced_repo["final_score"]
            }
            
            processed.append(processed_repo)
            
        except Exception as e:
            print(f"❌ 处理项目出错: {e}")
            continue
    
    return processed

def extract_metrics_tags(enhanced_repo):
    """基于指标提取标签"""
    tags = []
    
    # 质量标签
    if enhanced_repo["final_score"] >= 40:
        tags.append("顶级项目")
    elif enhanced_repo["final_score"] >= 30:
        tags.append("优秀项目")
    
    # 活跃度标签
    if "极活跃" in enhanced_repo["activity_status"]:
        tags.append("高活跃")
    elif "活跃" in enhanced_repo["activity_status"]:
        tags.append("活跃")
    
    # 影响力标签
    if enhanced_repo["community_impact"] == "高影响力":
        tags.append("高影响力")
    
    # 技术标签
    category = enhanced_repo["category"]
    if "LLM" in category:
        tags.append("LLM")
    if "生成式AI" in category:
        tags.append("生成式AI")
    if "计算机视觉" in category:
        tags.append("计算机视觉")
    
    return ", ".join(tags[:5])

def generate_metrics_summary(enhanced_repo):
    """生成基于指标的摘要"""
    repo = enhanced_repo
    name = repo.get("name", "")
    score = repo["final_score"]
    quality = repo["quality_level"].split()[0]
    activity = repo["activity_status"].split()[0]
    
    summary = f"{name} - {quality}·{activity}·{score}分"
    
    # 添加描述片段
    description = repo.get("description", "")
    if description:
        desc_snippet = description.split('.')[0][:50]
        summary += f" | {desc_snippet}"
    
    return summary[:150]

def save_to_database_with_metrics(repos_data):
    """保存指标增强的数据到数据库"""
    if not repos_data:
        print("❌ 没有数据需要保存")
        return
    
    print(f"💾 开始保存 {len(repos_data)} 条基于指标的数据...")
    
    sql = """
    INSERT INTO repos (id, name, owner, stars, forks, description, url, created_at, updated_at, category, tags, summary, relevance_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        stars=excluded.stars,
        updated_at=excluded.updated_at,
        category=excluded.category,
        tags=excluded.tags,
        summary=excluded.summary,
        relevance_score=excluded.relevance_score,
        sync_time=CURRENT_TIMESTAMP;
    """
    
    success_count = 0
    
    for repo in repos_data:
        try:
            params = [
                repo["id"], repo["name"], repo["owner"],
                repo["stars"], repo["forks"], repo["description"],
                repo["url"], repo["created_at"], repo["updated_at"],
                repo["category"], repo["tags"], repo["summary"],
                repo["relevance_score"]
            ]
            
            response = cloudflare_client.d1.database.query(
                database_id=D1_DATABASE_ID,
                account_id=CLOUDFLARE_ACCOUNT_ID,
                sql=sql,
                params=params
            )
            
            success_count += 1
            
            if success_count % 20 == 0:
                print(f"📊 已保存 {success_count}/{len(repos_data)} 条数据")
                
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            continue
    
    print(f"🎉 成功保存 {success_count} 条基于指标的记录！")
    return success_count

# ================================
# 🚀 主程序
# ================================

def main_metrics_based_collection():
    """基于指标的主数据收集程序"""
    start_time = datetime.now()
    print("🚀 基于GitHub指标的AI项目收集开始")
    print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取搜索策略和关键词
    search_strategies, time_ranges = build_enhanced_search_queries()
    
    # AI关键词
    ai_keywords = [
        "LLM", "transformer", "GPT", "artificial-intelligence",
        "machine-learning", "deep-learning", "computer-vision",
        "diffusion", "RAG", "pytorch", "tensorflow", "huggingface"
    ]
    
    print(f"📊 搜索策略: {len(search_strategies)} 种")
    print(f"🔑 关键词: {len(ai_keywords)} 个")
    print(f"🎯 目标: {SEARCH_OPTIMIZATION_CONFIG['collection_targets']['high_quality']} 条高质量数据")
    
    all_repos = []
    unique_repos = {}
    search_count = 0
    
    # 按配额分配搜索
    allocation = SEARCH_OPTIMIZATION_CONFIG["daily_search_allocation"]
    
    for strategy in search_strategies:
        strategy_quota = allocation.get(strategy["name"], 10)
        strategy_keywords = ai_keywords[:strategy_quota]
        
        print(f"\n🎯 执行策略: {strategy['name']} (配额: {strategy_quota})")
        
        for keyword in strategy_keywords:
            repos = execute_metrics_based_search(strategy, keyword, time_ranges)
            
            # 去重处理
            for repo in repos:
                repo_id = str(repo.get("id"))
                if repo_id not in unique_repos:
                    unique_repos[repo_id] = repo
            
            search_count += 1
            
            # 进度显示
            if search_count % 5 == 0:
                print(f"📈 已搜索 {search_count} 次，收集 {len(unique_repos)} 个唯一项目")
            
            # API限制控制
            time.sleep(SEARCH_OPTIMIZATION_CONFIG["api_limits"]["delay_between_calls"])
            
            # 达到目标后可早停
            if len(unique_repos) >= 800:
                print(f"✅ 已收集足够候选数据 ({len(unique_repos)}个)")
                break
        
        if len(unique_repos) >= 800:
            break
    
    all_repos = list(unique_repos.values())
    
    print(f"\n🎉 搜索阶段完成！")
    print(f"📊 总搜索次数: {search_count}")
    print(f"📦 候选项目: {len(all_repos)} 个")
    
    # 处理和过滤
    print(f"\n🔍 开始基于指标处理数据...")
    filtered_repos = filter_and_process_repos(all_repos)
    
    print(f"✅ 指标过滤后: {len(filtered_repos)} 个项目")
    
    if filtered_repos:
        # 按评分排序
        filtered_repos.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # 保存数据
        saved_count = save_to_database_with_metrics(filtered_repos)
        
        # 统计分析
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 基于指标的数据收集完成！")
        print(f"⏰ 总耗时: {duration}")
        print(f"📊 候选项目: {len(all_repos)}")
        print(f"✅ 有效项目: {len(filtered_repos)}")
        print(f"💾 保存成功: {saved_count}")
        print(f"📈 有效率: {(len(filtered_repos)/len(all_repos)*100):.1f}%")
        
        # 质量分析
        score_ranges = {"40+分": 0, "30-39分": 0, "20-29分": 0, "10-19分": 0}
        category_stats = {}
        
        for repo in filtered_repos:
            score = repo["relevance_score"]
            if score >= 40:
                score_ranges["40+分"] += 1
            elif score >= 30:
                score_ranges["30-39分"] += 1
            elif score >= 20:
                score_ranges["20-29分"] += 1
            else:
                score_ranges["10-19分"] += 1
            
            category = repo["category"].split(" - ")[0]
            category_stats[category] = category_stats.get(category, 0) + 1
        
        print(f"\n🎯 质量分布:")
        for range_name, count in score_ranges.items():
            print(f"   {range_name}: {count} 个")
        
        print(f"\n📋 技术分布:")
        for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {category}: {count} 个")
        
        # 成功判断
        high_quality_count = score_ranges["40+分"] + score_ranges["30-39分"]
        if len(filtered_repos) >= 200:
            print(f"\n🎊 成功达成目标！收集到 {len(filtered_repos)} 条数据，其中 {high_quality_count} 条为高质量项目！")
        else:
            print(f"\n📈 收集到 {len(filtered_repos)} 条数据，其中 {high_quality_count} 条为高质量项目")
    
    else:
        print("❌ 没有符合指标要求的项目")

if __name__ == "__main__":
    main_metrics_based_collection()
