#!/usr/bin/env python3
"""
基于时间去重的GitHub AI项目收集脚本
30天内不重复，30天后满足条件可重新收录
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from cloudflare import Cloudflare
from dotenv import load_dotenv
from time_based_dedup_config import (
    TIME_DEDUP_CONFIG, get_time_dedup_sql, should_reentry_repo,
    get_time_dedup_stats_sql
)
from github_metrics_config import (
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
# 📅 时间去重核心函数
# ================================

def check_existing_record(repo_id):
    """检查30天内是否已存在记录"""
    
    sql_queries = get_time_dedup_sql()
    
    try:
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql_queries["check_existing"],
            params=[repo_id]
        )
        
        if response.success and hasattr(response, 'result') and response.result:
            results = response.result[0].results
            if results:
                return results[0]
        
        return None
        
    except Exception as e:
        print(f"❌ 检查现有记录失败: {e}")
        return None

def process_repo_with_time_dedup(repo):
    """基于时间去重处理单个项目"""
    
    repo_id = str(repo.get("id"))
    
    # 检查30天内是否已存在
    existing_record = check_existing_record(repo_id)
    
    # 判断处理策略
    should_process, reason, action = should_reentry_repo(existing_record, repo)
    
    result = {
        "repo_id": repo_id,
        "name": repo.get("name"),
        "action": action,
        "reason": reason,
        "should_process": should_process
    }
    
    if not should_process:
        return result
    
    # 计算项目数据
    enhanced_data = enhance_repo_data(repo)
    
    if action == "insert" or action == "reinsert":
        success = insert_new_record(enhanced_data)
        result["success"] = success
        result["operation"] = "插入新记录"
        
    elif action == "update":
        success = update_existing_record(repo_id, enhanced_data)
        result["success"] = success
        result["operation"] = "更新现有记录"
    
    return result

def enhance_repo_data(repo):
    """增强项目数据"""
    
    # 计算评分
    score = calculate_comprehensive_score(repo)
    
    # 分类
    category = classify_project(repo)
    
    # 标签
    tags = extract_tags(repo)
    
    # 摘要
    summary = generate_summary(repo)
    
    return {
        "id": str(repo.get("id")),
        "name": repo.get("name"),
        "owner": repo.get("owner", {}).get("login"),
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "description": repo.get("description", ""),
        "url": repo.get("html_url"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("pushed_at"),
        "category": category,
        "tags": tags,
        "summary": summary,
        "relevance_score": score
    }

def classify_project(repo):
    """项目分类"""
    name = repo.get("name", "").lower()
    description = repo.get("description", "").lower() if repo.get("description") else ""
    text = f"{name} {description}"
    
    if any(k in text for k in ["llm", "large language", "gpt", "language model"]):
        if any(k in text for k in ["api", "server", "serving"]):
            return "LLM服务与工具"
        elif any(k in text for k in ["chat", "assistant", "bot"]):
            return "LLM应用"
        else:
            return "LLM研究"
    elif any(k in text for k in ["rag", "retrieval", "vector"]):
        return "RAG技术"
    elif any(k in text for k in ["diffusion", "stable-diffusion", "generation"]):
        return "生成式AI"
    elif any(k in text for k in ["computer vision", "object detection", "yolo"]):
        return "计算机视觉"
    elif any(k in text for k in ["data science", "analytics", "visualization"]):
        return "数据科学"
    else:
        return "通用AI"

def extract_tags(repo):
    """提取技术标签"""
    text = f"{repo.get('name', '')} {repo.get('description', '')}".lower()
    tags = []
    
    tag_keywords = {
        "LLM": ["llm", "language model"],
        "PyTorch": ["pytorch"],
        "TensorFlow": ["tensorflow"],
        "API": ["api"],
        "Research": ["research", "paper"]
    }
    
    for tag, keywords in tag_keywords.items():
        if any(keyword in text for keyword in keywords):
            tags.append(tag)
    
    return ", ".join(tags[:5])

def generate_summary(repo):
    """生成项目摘要"""
    name = repo.get("name", "")
    description = repo.get("description", "")
    stars = repo.get("stargazers_count", 0)
    
    if description:
        desc_snippet = description.split('.')[0][:50]
        return f"{name} - {desc_snippet} (⭐{stars})"
    else:
        return f"{name} - AI项目 (⭐{stars})"

def insert_new_record(enhanced_data):
    """插入新记录"""
    
    sql_queries = get_time_dedup_sql()
    
    try:
        params = [
            enhanced_data["id"], enhanced_data["name"], enhanced_data["owner"],
            enhanced_data["stars"], enhanced_data["forks"], enhanced_data["description"],
            enhanced_data["url"], enhanced_data["created_at"], enhanced_data["updated_at"],
            enhanced_data["category"], enhanced_data["tags"], enhanced_data["summary"],
            enhanced_data["relevance_score"]
        ]
        
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql_queries["insert_new"],
            params=params
        )
        
        return response.success
        
    except Exception as e:
        print(f"❌ 插入记录失败: {e}")
        return False

def update_existing_record(repo_id, enhanced_data):
    """更新现有记录"""
    
    sql_queries = get_time_dedup_sql()
    
    try:
        params = [
            enhanced_data["stars"], enhanced_data["updated_at"],
            enhanced_data["category"], enhanced_data["tags"],
            enhanced_data["summary"], enhanced_data["relevance_score"],
            repo_id
        ]
        
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql_queries["update_existing"],
            params=params
        )
        
        return response.success
        
    except Exception as e:
        print(f"❌ 更新记录失败: {e}")
        return False

# ================================
# 🔍 搜索和收集
# ================================

def execute_time_based_search():
    """执行基于时间去重的搜索"""
    
    print("🚀 开始基于时间去重的数据收集")
    print(f"📅 去重窗口: {TIME_DEDUP_CONFIG['dedup_window_days']} 天")
    print("=" * 60)
    
    # 获取搜索策略
    search_strategies, time_ranges = build_enhanced_search_queries()
    
    # AI关键词
    ai_keywords = [
        "LLM", "transformer", "artificial-intelligence",
        "machine-learning", "deep-learning", "computer-vision",
        "diffusion", "RAG", "pytorch", "tensorflow"
    ]
    
    all_repos = []
    search_count = 0
    
    # 执行搜索
    for strategy in search_strategies[:2]:  # 使用前2种策略
        for keyword in ai_keywords[:5]:  # 使用前5个关键词
            
            # 构建查询
            if strategy["name"] == "star_projects":
                query = f"{keyword} stars:>1000 pushed:>=2025-06-07 is:public archived:false"
            else:
                query = f"{keyword} stars:>100 created:>=2025-06-07 is:public archived:false"
            
            try:
                print(f"🔍 搜索: {keyword} ({strategy['name']})")
                
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 50  # 减少每次查询数量，专注质量
                }
                
                response = requests.get(
                    "https://api.github.com/search/repositories",
                    headers=github_headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                repos = data.get("items", [])
                
                print(f"   📊 找到 {len(repos)} 个项目")
                all_repos.extend(repos)
                
                search_count += 1
                time.sleep(2)  # API限制
                
                if len(all_repos) >= 200:  # 控制候选数量
                    break
                    
            except Exception as e:
                print(f"   ❌ 搜索失败: {e}")
                continue
        
        if len(all_repos) >= 200:
            break
    
    print(f"\n📦 搜索完成，收集到 {len(all_repos)} 个候选项目")
    return all_repos

def process_repos_with_time_dedup(repos):
    """使用时间去重处理所有项目"""
    
    print(f"\n🔄 开始处理 {len(repos)} 个项目 (30天去重)")
    print("=" * 60)
    
    results = {
        "inserted": 0,
        "updated": 0, 
        "skipped": 0,
        "reinserted": 0,
        "errors": 0
    }
    
    processed_repos = []
    
    for i, repo in enumerate(repos):
        try:
            # 基础过滤
            if repo.get("fork", False) or repo.get("archived", False):
                continue
                
            if not repo.get("description") or len(repo.get("description", "")) < 20:
                continue
            
            # 时间去重处理
            result = process_repo_with_time_dedup(repo)
            
            if result["should_process"]:
                processed_repos.append(result)
                
                if result["action"] == "insert":
                    results["inserted"] += 1
                    print(f"✅ 插入: {result['name']} - {result['reason']}")
                elif result["action"] == "update":
                    results["updated"] += 1
                    print(f"🔄 更新: {result['name']} - {result['reason']}")
                elif result["action"] == "reinsert":
                    results["reinserted"] += 1
                    print(f"🔄 重新收录: {result['name']} - {result['reason']}")
            else:
                results["skipped"] += 1
                if i % 10 == 0:  # 每10个显示一次跳过信息
                    print(f"⏭️ 跳过: {result['name']} - {result['reason']}")
                    
        except Exception as e:
            results["errors"] += 1
            print(f"❌ 处理出错: {e}")
            continue
    
    return results, processed_repos

# ================================
# 📊 统计和报告
# ================================

def show_time_dedup_stats():
    """显示时间去重统计"""
    
    print("\n📊 时间去重统计")
    print("=" * 40)
    
    try:
        stats_queries = get_time_dedup_stats_sql()
        
        # 30天内记录数
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=stats_queries["recent_records"]
        )
        
        if response.success and hasattr(response, 'result') and response.result:
            count = response.result[0].results[0]["count"]
            print(f"📅 30天内记录数: {count}")
        
    except Exception as e:
        print(f"❌ 统计查询失败: {e}")

# ================================
# 🚀 主程序
# ================================

def main_time_based_collection():
    """基于时间去重的主收集程序"""
    
    start_time = datetime.now()
    print("🚀 基于时间去重的GitHub AI项目收集")
    print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 去重策略: 30天内不重复，满足条件可重新收录")
    
    # 显示当前统计
    show_time_dedup_stats()
    
    # 执行搜索
    all_repos = execute_time_based_search()
    
    if not all_repos:
        print("❌ 没有找到候选项目")
        return
    
    # 去重处理
    unique_repos = {str(repo.get("id")): repo for repo in all_repos}.values()
    print(f"🔄 去重后候选项目: {len(list(unique_repos))} 个")
    
    # 时间去重处理
    results, processed_repos = process_repos_with_time_dedup(list(unique_repos))
    
    # 结果统计
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🎉 时间去重收集完成！")
    print(f"⏰ 总耗时: {duration}")
    print(f"📊 处理结果:")
    print(f"   ✅ 新插入: {results['inserted']} 个")
    print(f"   🔄 更新: {results['updated']} 个")
    print(f"   🔄 重新收录: {results['reinserted']} 个")
    print(f"   ⏭️ 跳过: {results['skipped']} 个")
    print(f"   ❌ 错误: {results['errors']} 个")
    
    total_processed = results['inserted'] + results['updated'] + results['reinserted']
    print(f"📈 有效处理: {total_processed} 个项目")
    
    if total_processed > 0:
        print(f"\n🎯 时间去重效果:")
        print(f"   - 避免了 {results['skipped']} 个30天内重复")
        print(f"   - 新发现了 {results['inserted']} 个项目")
        print(f"   - 更新了 {results['updated']} 个活跃项目")
        print(f"   - 重新收录了 {results['reinserted']} 个发展项目")
    
    # 显示最新统计
    show_time_dedup_stats()

if __name__ == "__main__":
    main_time_based_collection()
