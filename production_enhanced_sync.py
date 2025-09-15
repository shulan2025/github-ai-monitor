#!/usr/bin/env python3
"""
生产级增强版GitHub AI仓库收集脚本
基于测试结果优化，目标每天200条有效数据
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from cloudflare import Cloudflare
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# === 配置部分 ===
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID")

if not all([GITHUB_TOKEN, CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, D1_DATABASE_ID]):
    raise ValueError("环境变量未设置。请确保所有必要的环境变量都已正确配置。")

# 初始化客户端
cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

# GitHub API设置
github_url = "https://api.github.com/search/repositories"
github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# === 基于测试结果的优化搜索策略 ===

def get_production_search_queries():
    """生产级搜索查询配置"""
    
    # 基于测试结果，这些关键词有很好的效果
    high_yield_keywords = [
        "LLM",                    # 520个项目
        "AI",                     # 1276个项目  
        "artificial-intelligence", # 49个项目
        "diffusion",              # 103个项目
        "GPT",                    # 71个项目
        "pytorch",                # 57个项目
        "machine-learning",       # 56个项目
        "deep-learning",          # 52个项目
        "transformer",            # 36个项目
        "computer-vision",        # 24个项目
    ]
    
    # 技术组合关键词
    tech_combinations = [
        "RAG OR retrieval-augmented",
        "stable-diffusion OR text-to-image",
        "chatbot OR chat OR conversation",
        "neural-network OR CNN OR RNN",
        "object-detection OR YOLO",
        "natural-language-processing OR NLP",
        "reinforcement-learning OR RL",
        "generative-ai OR generation",
        "multimodal OR vision-language",
        "fine-tuning OR PEFT OR LoRA"
    ]
    
    # 热门框架和工具
    framework_keywords = [
        "huggingface OR transformers",
        "langchain OR llama",
        "tensorflow OR keras",
        "scikit-learn OR sklearn",
        "opencv OR cv2",
        "jupyter OR notebook",
        "gradio OR streamlit",
        "docker OR deployment"
    ]
    
    return high_yield_keywords + tech_combinations + framework_keywords

def get_production_time_windows():
    """生产级时间窗口配置"""
    windows = []
    
    # 30天窗口，不同星标要求
    end = datetime.now()
    
    # 高质量项目 (30天, 100+星)
    start = end - timedelta(days=30)
    windows.append({
        "name": "high_quality_30d",
        "range": f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "min_stars": 100,
        "priority": 1
    })
    
    # 中质量项目 (30天, 50+星)
    windows.append({
        "name": "medium_quality_30d", 
        "range": f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "min_stars": 50,
        "priority": 2
    })
    
    # 广泛覆盖 (30天, 20+星)
    windows.append({
        "name": "broad_coverage_30d",
        "range": f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "min_stars": 20,
        "priority": 3
    })
    
    # 90天窗口，发现更多项目
    start_90 = end - timedelta(days=90)
    windows.append({
        "name": "discovery_90d",
        "range": f"{start_90.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "min_stars": 20,
        "priority": 4
    })
    
    return windows

def execute_github_search(keyword, time_window, sort_method="stars"):
    """执行GitHub搜索"""
    
    query = f"{keyword} stars:>{time_window['min_stars']} created:{time_window['range']} is:public archived:false"
    
    params = {
        "q": query,
        "sort": sort_method,
        "order": "desc", 
        "per_page": 100
    }
    
    try:
        print(f"🔍 搜索: {keyword[:20]:20} | 窗口: {time_window['name']:15} | 最小星标: {time_window['min_stars']:3d}")
        
        response = requests.get(github_url, headers=github_headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        repos = data.get("items", [])
        total_count = data.get("total_count", 0)
        
        print(f"   📊 找到 {total_count} 个项目，获取前 {len(repos)} 个")
        
        return repos
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 搜索失败: {e}")
        return []

def calculate_ai_relevance_score(repo):
    """计算AI相关性评分 (优化版)"""
    name = repo.get("name", "").lower()
    description = repo.get("description", "").lower() if repo.get("description") else ""
    full_text = f"{name} {description}"
    
    score = 0
    
    # 高价值AI关键词 (3分每个)
    high_value = ["llm", "gpt", "transformer", "diffusion", "neural", "deep-learning"]
    score += sum(3 for keyword in high_value if keyword in full_text)
    
    # 中价值关键词 (2分每个)
    medium_value = ["machine-learning", "ai", "computer-vision", "nlp", "pytorch", "tensorflow"]
    score += sum(2 for keyword in medium_value if keyword in full_text)
    
    # 技术工具 (1分每个)
    tools = ["python", "api", "model", "training", "inference", "framework"]
    score += sum(1 for keyword in tools if keyword in full_text)
    
    # 质量加分
    stars = repo.get("stargazers_count", 0)
    if stars >= 1000:
        score += 3
    elif stars >= 500:
        score += 2
    elif stars >= 100:
        score += 1
    
    # 活跃度加分
    updated_at = repo.get("updated_at", "")
    if updated_at:
        try:
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_ago = (datetime.now().replace(tzinfo=updated.tzinfo) - updated).days
            if days_ago <= 30:
                score += 2
            elif days_ago <= 90:
                score += 1
        except:
            pass
    
    # 负面关键词扣分
    negative = ["tutorial", "example", "demo", "course", "learning", "study", "homework"]
    score -= sum(1 for keyword in negative if keyword in full_text)
    
    return min(10, max(0, score))

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
                
            description = repo.get("description", "")
            if len(description) < 10:  # 至少10字符描述
                continue
            
            # AI相关性评分
            relevance_score = calculate_ai_relevance_score(repo)
            
            if relevance_score < 2:  # 至少2分才保留
                continue
            
            # 分类
            category = categorize_project(repo.get("name", ""), description)
            
            # 提取标签
            tags = extract_tags(repo.get("name", ""), description)
            
            # 生成摘要
            summary = f"{repo.get('name', '')} - {description.split('.')[0]}"[:100]
            
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
                "category": category,
                "tags": tags,
                "summary": summary,
                "relevance_score": relevance_score
            }
            
            processed.append(processed_repo)
            
        except Exception as e:
            print(f"❌ 处理项目时出错: {e}")
            continue
    
    return processed

def categorize_project(name, description):
    """项目分类"""
    text = f"{name} {description}".lower()
    
    if any(k in text for k in ["llm", "large language", "gpt", "chatgpt", "language model"]):
        if any(k in text for k in ["api", "server", "serving", "inference"]):
            return "LLM服务与工具"
        elif any(k in text for k in ["chat", "assistant", "bot", "conversation"]):
            return "LLM应用"
        else:
            return "LLM研究"
    elif any(k in text for k in ["rag", "retrieval", "vector", "embedding"]):
        return "RAG技术"
    elif any(k in text for k in ["diffusion", "stable-diffusion", "text-to-image", "generation"]):
        return "生成式AI"
    elif any(k in text for k in ["computer vision", "object detection", "yolo", "opencv"]):
        return "计算机视觉"
    elif any(k in text for k in ["data science", "pandas", "visualization", "analytics"]):
        return "数据科学"
    elif any(k in text for k in ["machine learning", "deep learning", "neural network"]):
        return "机器学习"
    else:
        return "其他AI技术"

def extract_tags(name, description):
    """提取技术标签"""
    text = f"{name} {description}".lower()
    tags = []
    
    tag_mapping = {
        "LLM": ["llm", "language model"],
        "PyTorch": ["pytorch"],
        "TensorFlow": ["tensorflow"],
        "Transformer": ["transformer"],
        "API": ["api"],
        "Python": ["python"],
        "Chat": ["chat", "conversation"],
        "Research": ["research", "paper"],
        "Computer Vision": ["computer vision", "cv"],
        "Data Science": ["data science", "analytics"]
    }
    
    for tag, keywords in tag_mapping.items():
        if any(keyword in text for keyword in keywords):
            tags.append(tag)
    
    return ", ".join(tags[:5])  # 最多5个标签

def save_to_database(repos_data):
    """保存数据到Cloudflare D1"""
    if not repos_data:
        print("❌ 没有数据需要保存")
        return
    
    print(f"💾 开始保存 {len(repos_data)} 条数据到数据库...")
    
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
    
    # 批量处理
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
            
            if success_count % 10 == 0:
                print(f"📊 已保存 {success_count}/{len(repos_data)} 条数据")
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            continue
    
    print(f"🎉 成功保存 {success_count} 条记录到数据库！")
    return success_count

def main_production_collection():
    """生产级主数据收集函数"""
    start_time = datetime.now()
    print("🚀 生产级GitHub AI仓库收集开始")
    print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    search_queries = get_production_search_queries()
    time_windows = get_production_time_windows()
    
    print(f"📊 搜索关键词: {len(search_queries)} 个")
    print(f"⏰ 时间窗口: {len(time_windows)} 个")
    print(f"🔄 计划搜索次数: {len(search_queries) * len(time_windows)} 次")
    
    all_repos = []
    unique_repos = {}
    search_count = 0
    
    # 执行搜索
    for keyword in search_queries:
        for time_window in time_windows:
            
            repos = execute_github_search(keyword, time_window)
            
            # 去重处理
            for repo in repos:
                repo_id = str(repo.get("id"))
                if repo_id not in unique_repos:
                    unique_repos[repo_id] = repo
            
            search_count += 1
            
            # 进度显示
            if search_count % 10 == 0:
                print(f"📈 已完成 {search_count} 次搜索，收集到 {len(unique_repos)} 个唯一项目")
            
            # API限制控制
            time.sleep(1.0)  # 每次搜索间隔1秒
            
            # 达到足够数据量时可以早停
            if len(unique_repos) >= 1000:
                print(f"✅ 已收集足够数据 ({len(unique_repos)}个)，停止搜索")
                break
        
        if len(unique_repos) >= 1000:
            break
    
    all_repos = list(unique_repos.values())
    
    print(f"\n🎉 搜索完成！")
    print(f"📊 总搜索次数: {search_count}")
    print(f"📦 候选项目总数: {len(all_repos)}")
    
    # 处理和过滤数据
    print(f"\n🔍 开始处理和过滤数据...")
    filtered_repos = filter_and_process_repos(all_repos)
    
    print(f"✅ 过滤后有效项目: {len(filtered_repos)}")
    
    if filtered_repos:
        # 按评分排序
        filtered_repos.sort(key=lambda x: (x["relevance_score"], x["stars"]), reverse=True)
        
        # 保存到数据库
        saved_count = save_to_database(filtered_repos)
        
        # 统计结果
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 生产级数据收集完成！")
        print(f"⏰ 总耗时: {duration}")
        print(f"📊 候选项目: {len(all_repos)} 个")
        print(f"✅ 有效项目: {len(filtered_repos)} 个") 
        print(f"💾 保存成功: {saved_count} 个")
        print(f"📈 有效率: {(len(filtered_repos)/len(all_repos)*100):.1f}%")
        
        # 分类统计
        categories = {}
        scores = {"高分(8-10)": 0, "中分(6-7)": 0, "低分(2-5)": 0}
        
        for repo in filtered_repos:
            # 分类统计
            cat = repo["category"]
            categories[cat] = categories.get(cat, 0) + 1
            
            # 评分统计
            score = repo["relevance_score"]
            if score >= 8:
                scores["高分(8-10)"] += 1
            elif score >= 6:
                scores["中分(6-7)"] += 1
            else:
                scores["低分(2-5)"] += 1
        
        print(f"\n📋 分类统计:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count} 个")
        
        print(f"\n🎯 质量分布:")
        for level, count in scores.items():
            print(f"   {level}: {count} 个")
        
        # 成功判断
        if len(filtered_repos) >= 200:
            print(f"\n🎊 成功达成目标！收集到 {len(filtered_repos)} 条有效数据！")
        else:
            print(f"\n⚠️ 未完全达成目标，收集到 {len(filtered_repos)} 条有效数据")
            print("   建议：可以降低过滤阈值或增加搜索关键词")
    
    else:
        print("❌ 没有符合条件的项目数据")

if __name__ == "__main__":
    main_production_collection()
