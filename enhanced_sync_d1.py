#!/usr/bin/env python3
"""
增强版GitHub AI仓库数据收集脚本
目标：每天收集200+条有效AI项目数据
策略：多轮次、多维度、多时间窗口搜索
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from cloudflare import Cloudflare
from dotenv import load_dotenv
from enhanced_search_config import (
    ENHANCED_SEARCH_CONFIG, TECH_KEYWORD_GROUPS, TRENDING_KEYWORDS,
    LANGUAGE_COMBINATIONS, SORT_STRATEGIES, ENHANCED_FILTER_CONFIG,
    HIGH_VALUE_KEYWORDS, EXECUTION_STRATEGY, generate_search_queries,
    get_time_windows
)

# 从原配置导入必要的函数
from search_config import AI_RELEVANCE_THRESHOLD

# 加载环境变量
load_dotenv()

# --- 配置部分 ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID")

if not all([GITHUB_TOKEN, CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, D1_DATABASE_ID]):
    raise ValueError("环境变量未设置。请确保所有必要的环境变量都已正确配置。")

# --- 初始化客户端 ---
cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

# GitHub API设置
github_url = "https://api.github.com/search/repositories"
github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ================================
# 🔍 增强搜索函数
# ================================

def calculate_ai_relevance_enhanced(repo):
    """增强版AI相关性评分算法"""
    name = repo.get("name", "").lower()
    description = repo.get("description", "").lower() if repo.get("description") else ""
    full_text = f"{name} {description}"
    
    score = 0
    
    # 高价值关键词评分 (每个3分)
    high_value_matches = sum(1 for keyword in HIGH_VALUE_KEYWORDS 
                           if keyword.lower() in full_text)
    score += high_value_matches * 3
    
    # 技术栈匹配评分 (每组2分)
    for group_keywords in TECH_KEYWORD_GROUPS.values():
        if any(keyword.lower() in full_text for keyword in group_keywords):
            score += 2
    
    # 热门技术评分 (每个1分)
    trending_matches = sum(1 for keyword in TRENDING_KEYWORDS 
                         if keyword.lower() in full_text)
    score += trending_matches
    
    # 项目质量指标
    stars = repo.get("stargazers_count", 0)
    if stars >= 1000:
        score += 2
    elif stars >= 500:
        score += 1
        
    # 最近活跃度
    updated_at = repo.get("updated_at", "")
    if updated_at:
        try:
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_ago = (datetime.now().replace(tzinfo=updated.tzinfo) - updated).days
            if days_ago <= 30:
                score += 1
        except:
            pass
    
    # 负面关键词扣分
    negative_keywords = ["tutorial", "example", "demo", "course", "learning", "study"]
    negative_matches = sum(1 for keyword in negative_keywords 
                         if keyword in full_text)
    score -= negative_matches
    
    return min(10, max(0, score))

def filter_ai_repos_enhanced(repos):
    """增强版AI仓库过滤"""
    filtered = []
    
    for repo in repos:
        # 基础过滤
        if repo.get("fork", False) and ENHANCED_FILTER_CONFIG.get("exclude_forks", True):
            continue
            
        if repo.get("archived", False) and ENHANCED_FILTER_CONFIG.get("exclude_archived", True):
            continue
            
        description = repo.get("description", "")
        if len(description) < ENHANCED_FILTER_CONFIG.get("min_description_length", 20):
            continue
        
        # AI相关性评分
        score = calculate_ai_relevance_enhanced(repo)
        
        if score >= ENHANCED_FILTER_CONFIG.get("ai_relevance_threshold", 1):
            repo['relevance_score'] = score
            filtered.append(repo)
    
    return filtered

# ================================
# 🎯 多策略搜索执行
# ================================

def execute_search_query(query_config, time_window, sort_config):
    """执行单次搜索查询"""
    
    # 构建查询字符串
    search_terms = query_config["terms"]
    
    # 使用时间窗口自带的星标要求
    star_threshold = time_window.get("min_stars", 20)
    
    # 添加基础过滤条件
    filters = [
        f"stars:>{star_threshold}",
        f"created:{time_window['range']}",
        "is:public",
        "archived:false"
    ]
    
    # 如果是语言特定搜索，语言过滤已在terms中
    if not query_config["name"].startswith("lang_"):
        filters.append("language:Python OR language:JavaScript OR language:TypeScript OR language:Rust OR language:Go")
    
    query_string = f"({search_terms}) {' '.join(filters)}"
    
    params = {
        "q": query_string,
        "sort": sort_config["sort"],
        "order": sort_config["order"],
        "per_page": ENHANCED_SEARCH_CONFIG["per_page"]
    }
    
    try:
        print(f"🔍 搜索: {query_config['name']} | 时间窗口: {time_window['name']} | 排序: {sort_config['sort']}")
        print(f"   查询: {query_string[:100]}...")
        
        response = requests.get(github_url, headers=github_headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        repos = data.get("items", [])
        
        print(f"   找到 {len(repos)} 个候选项目")
        
        return repos
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 搜索失败: {e}")
        return []

def enhanced_data_collection():
    """增强版数据收集主函数"""
    print("🚀 开始增强版数据收集...")
    print(f"🎯 目标：收集 {EXECUTION_STRATEGY['target_valid']} 条有效AI项目")
    
    all_repos = []
    search_count = 0
    
    # 生成搜索查询
    search_queries = generate_search_queries()
    time_windows = get_time_windows()
    
    print(f"📊 生成了 {len(search_queries)} 个搜索查询")
    print(f"⏰ 配置了 {len(time_windows)} 个时间窗口")
    print(f"🔄 计划执行 {len(search_queries) * len(time_windows)} 次搜索")
    
    # 多轮搜索
    for query_config in search_queries[:EXECUTION_STRATEGY["primary_searches"]]:
        for time_window in time_windows[:4]:  # 使用前4个时间窗口
            for sort_config in SORT_STRATEGIES:
                
                # 执行搜索（星标要求在时间窗口中定义）
                repos = execute_search_query(query_config, time_window, sort_config)
                all_repos.extend(repos)
                
                search_count += 1
                
                # 进度显示
                if search_count % 10 == 0:
                    print(f"📈 已完成 {search_count} 次搜索，收集到 {len(all_repos)} 个候选项目")
                
                # API限制控制
                time.sleep(EXECUTION_STRATEGY["request_delay"])
                
                # 如果已经收集足够多的候选项目，可以提前结束
                if len(all_repos) >= EXECUTION_STRATEGY["target_candidates"]:
                    print(f"✅ 已达到候选项目目标 ({len(all_repos)}个)，停止搜索")
                    break
            
            if len(all_repos) >= EXECUTION_STRATEGY["target_candidates"]:
                break
        
        if len(all_repos) >= EXECUTION_STRATEGY["target_candidates"]:
            break
        
        # 每组查询后短暂休息
        time.sleep(EXECUTION_STRATEGY["batch_delay"])
    
    print(f"\n🎉 搜索完成！")
    print(f"📊 总搜索次数: {search_count}")
    print(f"📦 候选项目总数: {len(all_repos)}")
    
    return all_repos

# ================================
# 🔄 数据处理与存储
# ================================

def categorize_ai_project_enhanced(name, description):
    """增强版AI项目分类"""
    name_lower = name.lower() if name else ""
    desc_lower = description.lower() if description else ""
    full_text = f"{name_lower} {desc_lower}"
    
    # 更精确的分类逻辑
    if any(keyword in full_text for keyword in ["gpt", "llm", "large language model", "language model", "chatgpt", "claude", "llama"]):
        if any(keyword in full_text for keyword in ["api", "server", "inference", "serving", "engine"]):
            return "LLM服务与工具"
        elif any(keyword in full_text for keyword in ["chat", "assistant", "bot", "conversation"]):
            return "LLM应用"
        else:
            return "LLM研究"
    
    elif any(keyword in full_text for keyword in ["rag", "retrieval", "vector", "embedding", "semantic search"]):
        return "RAG技术"
    
    elif any(keyword in full_text for keyword in ["diffusion", "stable-diffusion", "text-to-image", "generation", "dall-e", "midjourney"]):
        return "生成式AI"
    
    elif any(keyword in full_text for keyword in ["computer vision", "cv", "yolo", "object detection", "image recognition", "opencv", "segmentation"]):
        return "计算机视觉"
    
    elif any(keyword in full_text for keyword in ["data science", "pandas", "numpy", "jupyter", "analytics", "visualization"]):
        return "数据科学"
    
    elif any(keyword in full_text for keyword in ["machine learning", "ml", "deep learning", "neural network", "tensorflow", "pytorch"]):
        return "机器学习"
    
    elif any(keyword in full_text for keyword in ["agent", "autonomous", "multi-agent", "workflow", "automation"]):
        return "智能体与自动化"
    
    elif any(keyword in full_text for keyword in ["speech", "audio", "voice", "whisper", "tts", "asr"]):
        return "语音AI"
    
    elif any(keyword in full_text for keyword in ["robotics", "robot", "embodied", "simulation"]):
        return "机器人与仿真"
    
    else:
        return "其他AI技术"

def process_and_save_repos_enhanced(repos):
    """增强版数据处理和保存"""
    print(f"\n🔍 开始处理 {len(repos)} 个候选项目...")
    
    # 去重处理
    unique_repos = {}
    for repo in repos:
        repo_id = str(repo.get("id"))
        if repo_id not in unique_repos:
            unique_repos[repo_id] = repo
    
    repos = list(unique_repos.values())
    print(f"🔄 去重后剩余 {len(repos)} 个项目")
    
    # AI相关性过滤
    filtered_repos = filter_ai_repos_enhanced(repos)
    print(f"🎯 AI过滤后剩余 {len(filtered_repos)} 个项目")
    
    if not filtered_repos:
        print("❌ 没有符合条件的项目")
        return
    
    # 数据处理和增强
    processed_repos = []
    for repo in filtered_repos:
        try:
            # 基础信息
            processed_repo = {
                "id": str(repo.get("id")),
                "name": repo.get("name"),
                "owner": repo.get("owner", {}).get("login"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("pushed_at"),
                "relevance_score": repo.get("relevance_score", 0)
            }
            
            # 智能分析
            processed_repo["category"] = categorize_ai_project_enhanced(
                processed_repo["name"], 
                processed_repo["description"]
            )
            
            # 简化的标签提取
            tags = []
            desc_lower = (processed_repo["description"] or "").lower()
            name_lower = (processed_repo["name"] or "").lower()
            full_text = f"{name_lower} {desc_lower}"
            
            # 技术标签
            if "llm" in full_text or "language model" in full_text:
                tags.append("LLM")
            if "transformer" in full_text:
                tags.append("Transformer") 
            if "pytorch" in full_text:
                tags.append("PyTorch")
            if "tensorflow" in full_text:
                tags.append("TensorFlow")
            if "api" in full_text:
                tags.append("API")
            if "cli" in full_text:
                tags.append("CLI")
                
            processed_repo["tags"] = ", ".join(tags[:5])  # 最多5个标签
            
            # 生成摘要
            processed_repo["summary"] = f"{processed_repo['name']} - {(processed_repo['description'] or '').split('.')[0]}"[:100]
            
            processed_repos.append(processed_repo)
            
        except Exception as e:
            print(f"❌ 处理项目时出错: {e}")
            continue
    
    print(f"✅ 成功处理 {len(processed_repos)} 个项目")
    
    # 保存到数据库
    save_to_database_enhanced(processed_repos)
    
    return processed_repos

def save_to_database_enhanced(repos_data):
    """增强版数据库保存"""
    if not repos_data:
        print("❌ 没有数据需要保存")
        return
    
    print(f"💾 开始保存 {len(repos_data)} 条数据到数据库...")
    
    # 准备SQL语句
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
    
    # 批量处理
    batch_size = 10
    success_count = 0
    
    for i in range(0, len(repos_data), batch_size):
        batch = repos_data[i:i+batch_size]
        commands = []
        
        for repo in batch:
            commands.append({
                "sql": sql,
                "params": [
                    repo["id"], repo["name"], repo["owner"],
                    repo["stars"], repo["forks"], repo["description"],
                    repo["url"], repo["created_at"], repo["updated_at"],
                    repo["category"], repo["tags"], repo["summary"],
                    repo["relevance_score"]
                ]
            })
        
        try:
            # 执行批量插入
            response = cloudflare_client.d1.database.query(
                database_id=D1_DATABASE_ID,
                account_id=CLOUDFLARE_ACCOUNT_ID,
                sql=sql,
                params=commands[0]["params"] if commands else []
            )
            
            success_count += len(batch)
            print(f"📊 已保存 {success_count}/{len(repos_data)} 条数据")
            
        except Exception as e:
            print(f"❌ 保存批次失败: {e}")
            
            # 尝试逐条保存
            for cmd in commands:
                try:
                    cloudflare_client.d1.database.query(
                        database_id=D1_DATABASE_ID,
                        account_id=CLOUDFLARE_ACCOUNT_ID,
                        sql=cmd["sql"],
                        params=cmd["params"]
                    )
                    success_count += 1
                except Exception as e2:
                    print(f"❌ 保存单条记录失败: {e2}")
    
    print(f"🎉 成功保存 {success_count} 条记录到数据库！")

# ================================
# 🚀 主程序
# ================================

def main_enhanced():
    """增强版主程序"""
    start_time = datetime.now()
    print(f"🚀 增强版GitHub AI仓库收集开始")
    print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 目标: {EXECUTION_STRATEGY['target_valid']} 条有效数据")
    print("=" * 60)
    
    try:
        # 执行数据收集
        all_repos = enhanced_data_collection()
        
        # 处理和保存数据
        processed_repos = process_and_save_repos_enhanced(all_repos)
        
        # 统计结果
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 增强版数据收集完成！")
        print(f"⏰ 总耗时: {duration}")
        print(f"📊 候选项目: {len(all_repos)} 个")
        print(f"✅ 有效项目: {len(processed_repos) if processed_repos else 0} 个")
        print(f"📈 有效率: {(len(processed_repos)/len(all_repos)*100):.1f}%" if all_repos and processed_repos else "N/A")
        
        if processed_repos:
            # 分类统计
            categories = {}
            for repo in processed_repos:
                cat = repo["category"]
                categories[cat] = categories.get(cat, 0) + 1
            
            print("\n📋 分类统计:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   {cat}: {count} 个")
        
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_enhanced()
