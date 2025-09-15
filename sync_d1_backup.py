import os
import requests
import json
from datetime import datetime, timedelta
from cloudflare import Cloudflare
from dotenv import load_dotenv
from search_config import (
    SEARCH_CONFIG, LLM_TERMS, RAG_TERMS, DIFFUSION_TERMS, 
    ML_TERMS, CV_TERMS, DS_TERMS, ENABLE_DOMAINS, 
    PREFERRED_LANGUAGES, AI_RELEVANCE_THRESHOLD
)

# 加载环境变量
load_dotenv()

# --- 配置部分 ---
# 请确保你的环境变量已正确设置
# GITHUB_TOKEN: GitHub 个人访问令牌
# CLOUDFLARE_API_TOKEN: Cloudflare API 令牌
# CLOUDFLARE_ACCOUNT_ID: Cloudflare 账户 ID
# D1_DATABASE_ID: Cloudflare D1 数据库 ID
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID")

if not all([GITHUB_TOKEN, CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, D1_DATABASE_ID]):
    raise ValueError("环境变量未设置。请确保所有必要的环境变量都已正确配置。")

# --- 初始化 API 客户端 ---
cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

# --- GitHub API 设置 ---
url = "https://api.github.com/search/repositories"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 动态生成查询日期范围（最近7天）
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
date_range = f"{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"

# 构建搜索查询
def build_search_query():
    """构建前沿AI技术的搜索查询"""
    all_terms = []
    
    # 根据配置添加AI领域的关键词（精简版，避免查询过长）
    if ENABLE_DOMAINS.get("LLM", True):
        all_terms.append("LLM")
    if ENABLE_DOMAINS.get("RAG", True):
        all_terms.append("RAG")
    if ENABLE_DOMAINS.get("Diffusion", True):
        all_terms.append("diffusion-model")
    if ENABLE_DOMAINS.get("MachineLearning", True):
        all_terms.append("machine-learning")
    if ENABLE_DOMAINS.get("ComputerVision", True):
        all_terms.append("computer-vision")
    if ENABLE_DOMAINS.get("DataScience", True):
        all_terms.append("data-science")
    
    # 动态生成查询日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=SEARCH_CONFIG["days_back"])
    date_range = f"{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
    
    # 构建查询字符串
    keywords = " OR ".join(all_terms)
    query = f"({keywords}) created:{date_range} stars:>{SEARCH_CONFIG['min_stars']}"
    
    return query

# 搜索参数
params = {
    "q": build_search_query(),
    "sort": "stars", 
    "order": "desc",
    "per_page": SEARCH_CONFIG["per_page"]
}

# --- 函数：智能分类AI项目 ---
def categorize_ai_project(name, description):
    """根据项目名称和描述智能分类AI项目"""
    name_lower = name.lower()
    desc_lower = description.lower() if description else ""
    full_text = f"{name_lower} {desc_lower}"
    
    # AI项目分类规则
    if any(keyword in full_text for keyword in ["llm", "large language model", "gpt", "chat", "conversation", "inference"]):
        if any(keyword in full_text for keyword in ["server", "api", "cli", "tool", "framework", "engine"]):
            return "LLM服务与工具"
        elif any(keyword in full_text for keyword in ["chat", "app", "client", "ui", "interface"]):
            return "LLM应用"
        else:
            return "LLM研究"
    
    elif any(keyword in full_text for keyword in ["rag", "retrieval", "vector", "embedding", "semantic search", "knowledge"]):
        return "RAG技术"
    
    elif any(keyword in full_text for keyword in ["diffusion", "stable-diffusion", "text-to-image", "generation", "dall-e"]):
        return "生成式AI"
    
    elif any(keyword in full_text for keyword in ["computer vision", "object detection", "image recognition", "opencv", "yolo", "image classification", "segmentation", "face recognition", "ocr"]):
        return "计算机视觉"
    
    elif any(keyword in full_text for keyword in ["data science", "data analysis", "data visualization", "pandas", "numpy", "matplotlib", "jupyter", "statistical", "analytics"]):
        return "数据科学"
    
    elif any(keyword in full_text for keyword in ["machine learning", "scikit-learn", "tensorflow", "pytorch", "keras", "gradient boosting", "random forest", "svm", "neural network"]):
        if any(keyword in full_text for keyword in ["llm", "language model", "gpt", "transformer"]):
            return "LLM研究"  # 如果同时包含ML和LLM关键词，归类为LLM
        else:
            return "机器学习"
    
    elif any(keyword in full_text for keyword in ["dataset", "benchmark", "toolkit", "framework", "library", "collection"]):
        return "AI资源与工具"
    
    elif any(keyword in full_text for keyword in ["mobile", "ios", "android", "flutter", "swift"]):
        return "移动端AI"
    
    elif any(keyword in full_text for keyword in ["reinforcement", "agent", "autonomous"]):
        return "智能体与强化学习"
    
    else:
        return "其他AI技术"

def generate_summary(name, description):
    """生成项目简要介绍"""
    if not description:
        return f"{name} - AI相关项目"
    
    # 简化描述，提取关键信息
    desc = description.strip()
    if len(desc) > 100:
        # 截取前100个字符并在合适位置截断
        truncated = desc[:100]
        last_space = truncated.rfind(' ')
        if last_space > 50:
            desc = truncated[:last_space] + "..."
        else:
            desc = truncated + "..."
    
    return f"{name} - {desc}"

def extract_tags(name, description, category):
    """提取项目标签"""
    name_lower = name.lower()
    desc_lower = description.lower() if description else ""
    full_text = f"{name_lower} {desc_lower}"
    
    tags = []
    
    # 技术标签
    tech_keywords = {
        "LLM": ["llm", "large language model"],
        "Transformer": ["transformer"],
        "RAG": ["rag", "retrieval"],
        "Diffusion": ["diffusion"],
        "PyTorch": ["pytorch"],
        "TensorFlow": ["tensorflow"],
        "Scikit-Learn": ["scikit-learn", "sklearn"],
        "Keras": ["keras"],
        "OpenAI": ["openai", "gpt"],
        "Hugging Face": ["huggingface", "hf"],
        "Vector DB": ["vector", "embedding"],
        "Chat": ["chat", "conversation"],
        "API": ["api", "server"],
        "Mobile": ["mobile", "ios", "android"],
        "CLI": ["cli", "command"],
        "Research": ["paper", "research"],
        "Benchmark": ["benchmark", "evaluation"],
        "Computer Vision": ["computer vision", "cv", "opencv"],
        "YOLO": ["yolo"],
        "Object Detection": ["object detection", "detection"],
        "Data Science": ["data science", "ds"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Jupyter": ["jupyter"],
        "Visualization": ["visualization", "matplotlib"],
        "Deep Learning": ["deep learning", "dl"],
        "Neural Network": ["neural network", "nn"],
        "Machine Learning": ["machine learning", "ml"]
    }
    
    for tag, keywords in tech_keywords.items():
        if any(keyword in full_text for keyword in keywords):
            tags.append(tag)
    
    return ", ".join(tags[:5])  # 最多5个标签

# --- 函数：过滤真正的 AI/ML 相关仓库 ---
def filter_ai_repos(repos_data):
    """过滤出真正与 AI/ML 相关的仓库 - 升级版"""
    
    # 高权重 AI 关键词 (必须匹配)
    high_priority_keywords = [
        'artificial intelligence', 'machine learning', 'deep learning', 'neural network',
        'computer vision', 'natural language processing', 'reinforcement learning',
        'llm', 'large language model', 'gpt', 'transformer', 'bert', 'llama',
        'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'huggingface',
        'object detection', 'image recognition', 'text classification', 
        'sentiment analysis', 'fine-tuning', 'rag', 'yolo', 'opencv'
    ]
    
    # 中等权重关键词
    medium_priority_keywords = [
        'ai', 'ml', 'dl', 'nlp', 'cv', 'data science', 'algorithm',
        'classification', 'regression', 'clustering', 'segmentation',
        'chatbot', 'recommendation', 'anomaly detection', 'feature extraction'
    ]
    
    # 排除关键词 (这些通常不是AI项目)
    exclude_keywords = [
        'ui framework', 'web framework', 'frontend', 'backend', 'api',
        'compose', 'react', 'vue', 'angular', 'css', 'html', 'javascript',
        'website', 'web design', 'mobile app', 'game engine', 'database',
        'blockchain', 'cryptocurrency', 'devops', 'docker', 'kubernetes'
    ]
    
    # 编程语言相关 (单独出现时不算AI项目)
    language_only_keywords = [
        'python tutorial', 'javascript guide', 'java examples', 'c++ basics',
        'programming exercises', 'coding practice', 'algorithm practice'
    ]
    
    filtered_repos = []
    
    for repo in repos_data:
        name = repo.get('name', '').lower()
        description = repo.get('description', '').lower() if repo.get('description') else ''
        full_text = f"{name} {description}"
        
        # 评分系统
        score = 0
        
        # 高权重关键词匹配 (+3分)
        high_matches = sum(1 for keyword in high_priority_keywords if keyword in full_text)
        score += high_matches * 3
        
        # 中等权重关键词匹配 (+1分)
        medium_matches = sum(1 for keyword in medium_priority_keywords if keyword in full_text)
        score += medium_matches * 1
        
        # 排除关键词匹配 (-5分)
        exclude_matches = sum(1 for keyword in exclude_keywords if keyword in full_text)
        score -= exclude_matches * 5
        
        # 纯语言教程关键词 (-3分)
        language_matches = sum(1 for keyword in language_only_keywords if keyword in full_text)
        score -= language_matches * 3
        
        # 决策逻辑：使用配置中的阈值
        if score >= AI_RELEVANCE_THRESHOLD:
            # 添加智能分类和摘要
            repo['ai_relevance_score'] = score
            repo['category'] = categorize_ai_project(name, description)
            repo['tags'] = extract_tags(name, description, repo['category'])
            repo['summary'] = generate_summary(repo.get('name'), description)
            
            filtered_repos.append(repo)
            print(f"✅ 保留AI仓库 (分数:{score}) [{repo['category']}]: {repo['summary']}")
        else:
            print(f"⚠️ 过滤掉不相关仓库 (分数:{score}): {repo.get('name')} - {description[:50]}...")
    
    # 按相关性分数排序
    filtered_repos.sort(key=lambda x: x.get('ai_relevance_score', 0), reverse=True)
    
    return filtered_repos

# --- 函数：将数据插入到 D1 数据库 ---
def insert_to_d1(repos_data):
    if not repos_data:
        print("没有数据可插入。")
        return

    # 准备 SQL 语句，包含新的字段
    sql = """
    INSERT INTO repos (id, name, owner, stars, forks, description, url, created_at, updated_at, category, tags, summary, relevance_score) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
    ON CONFLICT(id) DO UPDATE SET 
      stars=excluded.stars,
      forks=excluded.forks,
      description=excluded.description,
      updated_at=excluded.updated_at,
      category=excluded.category,
      tags=excluded.tags,
      summary=excluded.summary,
      relevance_score=excluded.relevance_score;
    """
    
    # 准备要执行的命令列表
    commands = []
    for repo in repos_data:
        commands.append({
            "sql": sql,
            "params": [
                str(repo.get("id")),
                repo.get("name"),
                repo.get("owner", {}).get("login"),
                repo.get("stargazers_count"),
                repo.get("forks_count"),
                repo.get("description"),
                repo.get("html_url"),
                repo.get("created_at"),
                repo.get("pushed_at"),
                repo.get("category", "其他AI技术"),
                repo.get("tags", ""),
                repo.get("summary", ""),
                repo.get("ai_relevance_score", 0)
            ]
        })

    try:
        # 通过 Cloudflare API 执行批量插入
        success_count = 0
        for cmd in commands:
            try:
                response = cloudflare_client.d1.database.query(
                    database_id=D1_DATABASE_ID,
                    account_id=CLOUDFLARE_ACCOUNT_ID,
                    sql=cmd["sql"],
                    params=cmd["params"]
                )
                success_count += 1
            except Exception as single_error:
                print(f"单条数据插入失败: {single_error}")
        
        print(f"成功将 {success_count}/{len(repos_data)} 条数据插入/更新到 D1 数据库。")
        
    except Exception as e:
        print(f"与 Cloudflare D1 通信时发生错误: {e}")
        # 尝试逐条插入以提高成功率
        print("尝试逐条插入数据...")
        success_count = 0
        for i, repo in enumerate(repos_data):
            try:
                single_response = cloudflare_client.d1.database.query(
                    database_id=D1_DATABASE_ID,
                    account_id=CLOUDFLARE_ACCOUNT_ID,
                    sql=sql,
                    params=[
                        str(repo.get("id")),
                        repo.get("name"),
                        repo.get("owner", {}).get("login"),
                        repo.get("stargazers_count"),
                        repo.get("forks_count"),
                        repo.get("description"),
                        repo.get("html_url"),
                        repo.get("created_at"),
                        repo.get("pushed_at"),
                        repo.get("category", "其他AI技术"),
                        repo.get("tags", ""),
                        repo.get("summary", ""),
                        repo.get("ai_relevance_score", 0)
                    ]
                )
                success_count += 1
            except Exception as single_error:
                print(f"第 {i+1} 条数据插入失败: {single_error}")
        
        print(f"逐条插入完成，成功 {success_count}/{len(repos_data)} 条。")

# --- 主程序 ---
def main():
    try:
        print(f"正在查询 GitHub 仓库... 查询条件: {params['q']}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        repos = data.get("items", [])

        if not repos:
            print("未找到符合条件的新仓库，任务结束。")
            return
        
        print(f"找到 {len(repos)} 个符合条件的仓库:")
        for i, repo in enumerate(repos[:5], 1):  # 显示前5个仓库信息
            print(f"{i}. {repo['name']} - ⭐{repo['stargazers_count']} - {repo['owner']['login']}")
        
        if len(repos) > 5:
            print(f"... 还有 {len(repos) - 5} 个仓库")
        
        # 过滤出真正的 AI/ML 相关仓库
        print(f"\n🔍 正在过滤 AI/ML 相关仓库...")
        filtered_repos = filter_ai_repos(repos)
        
        if filtered_repos:
            print(f"\n✅ 过滤后剩余 {len(filtered_repos)} 个真正的 AI/ML 仓库")
            insert_to_d1(filtered_repos)
        else:
            print("\n⚠️ 过滤后没有找到真正的 AI/ML 相关仓库")

    except requests.exceptions.RequestException as e:
        print(f"请求 GitHub API 时出错: {e}")
    except Exception as e:
        print(f"脚本执行时发生错误: {e}")

if __name__ == "__main__":
    main()
