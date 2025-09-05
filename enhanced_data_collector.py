#!/usr/bin/env python3
"""
增强版数据收集器 v2.0
实现完整的GitHub指标收集和智能评分算法
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from cloudflare import Cloudflare
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
CLOUDFLARE_API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
D1_DATABASE_ID = os.environ.get('D1_DATABASE_ID')

# GitHub API配置
GITHUB_HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Enhanced-AI-Repo-Monitor/2.0'
}

# Cloudflare客户端
cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

def fetch_comprehensive_repo_data(owner, repo_name):
    """获取仓库的完整数据"""
    
    try:
        print(f"📊 正在获取 {owner}/{repo_name} 的完整数据...")
        
        # 1. 基础仓库信息
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        repo_response = requests.get(repo_url, headers=GITHUB_HEADERS)
        
        if repo_response.status_code != 200:
            print(f"❌ 获取仓库信息失败: {repo_response.status_code}")
            return None
            
        repo_data = repo_response.json()
        
        # 2. 贡献者信息
        contributors = fetch_contributors_count(owner, repo_name)
        
        # 3. 提交信息  
        commits_info = fetch_commits_info(owner, repo_name)
        
        # 4. Pull Requests信息
        prs_info = fetch_prs_info(owner, repo_name)
        
        # 5. Issues信息
        issues_info = fetch_issues_info(owner, repo_name)
        
        # 6. 发布信息
        releases_info = fetch_releases_info(owner, repo_name)
        
        # 7. 语言分布
        languages_info = fetch_languages_info(owner, repo_name)
        
        # 8. 内容分析 (README, 文档等)
        content_analysis = analyze_repo_content(owner, repo_name)
        
        # 9. AI/ML特定分析
        ai_analysis = analyze_ai_features(repo_data, content_analysis)
        
        # 整合所有数据
        comprehensive_data = {
            'basic_info': repo_data,
            'contributors': contributors,
            'commits': commits_info,
            'pull_requests': prs_info,
            'issues': issues_info,
            'releases': releases_info,
            'languages': languages_info,
            'content': content_analysis,
            'ai_features': ai_analysis
        }
        
        return comprehensive_data
        
    except Exception as e:
        print(f"❌ 获取数据时出错: {e}")
        return None

def fetch_contributors_count(owner, repo_name):
    """获取贡献者数量"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
        response = requests.get(url, headers=GITHUB_HEADERS)
        
        if response.status_code == 200:
            contributors = response.json()
            return len(contributors)
    except Exception as e:
        print(f"⚠️ 获取贡献者失败: {e}")
    
    return 0

def fetch_commits_info(owner, repo_name):
    """获取提交信息"""
    try:
        # 获取总提交数 (通过最后一页)
        url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
        params = {'per_page': 1, 'page': 1}
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        
        commits_count = 0
        last_commit_date = None
        
        if response.status_code == 200:
            # 从Link header获取总页数
            link_header = response.headers.get('Link', '')
            if 'last' in link_header:
                import re
                match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if match:
                    commits_count = int(match.group(1))
            
            # 获取最新提交信息
            commits = response.json()
            if commits:
                last_commit_date = commits[0]['commit']['author']['date']
        
        return {
            'total_commits': commits_count,
            'last_commit_date': last_commit_date
        }
        
    except Exception as e:
        print(f"⚠️ 获取提交信息失败: {e}")
        return {'total_commits': 0, 'last_commit_date': None}

def fetch_prs_info(owner, repo_name):
    """获取Pull Requests信息"""
    try:
        # 获取PR统计
        url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
        params = {'state': 'all', 'per_page': 100}
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        
        if response.status_code == 200:
            prs = response.json()
            
            open_prs = [pr for pr in prs if pr['state'] == 'open']
            closed_prs = [pr for pr in prs if pr['state'] == 'closed']
            
            return {
                'total_prs': len(prs),
                'open_prs': len(open_prs),
                'closed_prs': len(closed_prs)
            }
    except Exception as e:
        print(f"⚠️ 获取PR信息失败: {e}")
    
    return {'total_prs': 0, 'open_prs': 0, 'closed_prs': 0}

def fetch_issues_info(owner, repo_name):
    """获取Issues信息"""
    try:
        # 获取Issues统计
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
        params = {'state': 'all', 'per_page': 100}
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        
        if response.status_code == 200:
            issues = response.json()
            
            # 过滤掉Pull Requests (GitHub API中Issues包含PRs)
            real_issues = [issue for issue in issues if 'pull_request' not in issue]
            open_issues = [issue for issue in real_issues if issue['state'] == 'open']
            
            return {
                'total_issues': len(real_issues),
                'open_issues': len(open_issues)
            }
    except Exception as e:
        print(f"⚠️ 获取Issues信息失败: {e}")
    
    return {'total_issues': 0, 'open_issues': 0}

def fetch_releases_info(owner, repo_name):
    """获取发布信息"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/releases"
        response = requests.get(url, headers=GITHUB_HEADERS)
        
        if response.status_code == 200:
            releases = response.json()
            return len(releases)
    except Exception as e:
        print(f"⚠️ 获取发布信息失败: {e}")
    
    return 0

def fetch_languages_info(owner, repo_name):
    """获取编程语言信息"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
        response = requests.get(url, headers=GITHUB_HEADERS)
        
        if response.status_code == 200:
            languages = response.json()
            
            if languages:
                # 找出主要语言 (使用字节数最多的)
                primary_language = max(languages.items(), key=lambda x: x[1])[0]
                
                # 构建技术栈字符串
                tech_stack = ', '.join(languages.keys())
                
                return {
                    'primary_language': primary_language,
                    'tech_stack': tech_stack,
                    'languages_count': len(languages)
                }
    except Exception as e:
        print(f"⚠️ 获取语言信息失败: {e}")
    
    return {
        'primary_language': 'Unknown',
        'tech_stack': '',
        'languages_count': 0
    }

def analyze_repo_content(owner, repo_name):
    """分析仓库内容特征"""
    try:
        analysis = {
            'has_readme': False,
            'has_wiki': False,
            'has_pages': False,
            'documentation_score': 0
        }
        
        # 检查README
        readme_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
        readme_response = requests.get(readme_url, headers=GITHUB_HEADERS)
        
        if readme_response.status_code == 200:
            analysis['has_readme'] = True
            readme_data = readme_response.json()
            # README质量评分 (基于大小)
            size = readme_data.get('size', 0)
            analysis['documentation_score'] = min(15, size // 500)  # 每500字节1分，最高15分
        
        # 检查仓库设置 (通过基础API判断)
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        repo_response = requests.get(repo_url, headers=GITHUB_HEADERS)
        
        if repo_response.status_code == 200:
            repo_data = repo_response.json()
            analysis['has_wiki'] = repo_data.get('has_wiki', False)
            analysis['has_pages'] = repo_data.get('has_pages', False)
        
        return analysis
        
    except Exception as e:
        print(f"⚠️ 内容分析失败: {e}")
        return {
            'has_readme': False,
            'has_wiki': False, 
            'has_pages': False,
            'documentation_score': 0
        }

def analyze_ai_features(repo_data, content_analysis):
    """分析AI/ML特定特征"""
    
    name = repo_data.get('name', '').lower()
    description = repo_data.get('description', '').lower() if repo_data.get('description') else ''
    topics = repo_data.get('topics', [])
    full_text = f"{name} {description} {' '.join(topics)}"
    
    ai_analysis = {
        'ai_framework': 'unknown',
        'model_type': 'unknown',
        'has_model_files': False,
        'has_paper': False,
        'cutting_edge_score': 0,
        'practical_score': 0
    }
    
    # AI框架识别
    frameworks = {
        'pytorch': ['pytorch', 'torch'],
        'tensorflow': ['tensorflow', 'tf'],
        'huggingface': ['huggingface', 'transformers'],
        'langchain': ['langchain'],
        'openai': ['openai', 'gpt'],
        'anthropic': ['claude', 'anthropic'],
        'scikit-learn': ['sklearn', 'scikit-learn'],
        'keras': ['keras'],
        'jax': ['jax', 'flax']
    }
    
    for framework, keywords in frameworks.items():
        if any(keyword in full_text for keyword in keywords):
            ai_analysis['ai_framework'] = framework
            break
    
    # 模型类型识别
    model_types = {
        'llm': ['llm', 'language model', 'gpt', 'bert', 'transformer', 'chatbot'],
        'cv': ['computer vision', 'image', 'detection', 'yolo', 'opencv', 'vision'],
        'nlp': ['nlp', 'natural language', 'text processing', 'sentiment'],
        'ml': ['machine learning', 'classification', 'regression', 'clustering'],
        'dl': ['deep learning', 'neural network', 'cnn', 'rnn', 'lstm'],
        'rag': ['rag', 'retrieval', 'vector database', 'embedding'],
        'agent': ['agent', 'autonomous', 'planning', 'reasoning'],
        'multimodal': ['multimodal', 'vision-language', 'clip'],
        'generative': ['generation', 'gan', 'vae', 'diffusion']
    }
    
    for model_type, keywords in model_types.items():
        if any(keyword in full_text for keyword in keywords):
            ai_analysis['model_type'] = model_type
            break
    
    # 检测模型文件
    model_keywords = ['model', 'checkpoint', 'weights', '.pth', '.h5', '.onnx', '.pkl']
    if any(keyword in full_text for keyword in model_keywords):
        ai_analysis['has_model_files'] = True
    
    # 检测研究论文
    paper_keywords = ['paper', 'arxiv', 'research', 'publication', 'cite']
    if any(keyword in full_text for keyword in paper_keywords):
        ai_analysis['has_paper'] = True
    
    # 前沿技术评分 (0-25分)
    cutting_edge_keywords = {
        'gpt-4': 5, 'claude': 5, 'llama': 4, 'gemini': 4,
        'multimodal': 4, 'vision-language': 4,
        'agent': 3, 'autonomous': 3, 'reasoning': 3,
        'rag': 3, 'retrieval': 3, 'vector': 2,
        '2024': 3, 'sota': 4, 'state-of-art': 4
    }
    
    for keyword, score in cutting_edge_keywords.items():
        if keyword in full_text:
            ai_analysis['cutting_edge_score'] += score
    
    ai_analysis['cutting_edge_score'] = min(25, ai_analysis['cutting_edge_score'])
    
    # 实用性评分 (0-20分)
    practical_keywords = {
        'api': 3, 'production': 4, 'deploy': 3, 'docker': 2,
        'web': 2, 'app': 2, 'service': 3, 'tool': 2,
        'library': 2, 'framework': 3, 'sdk': 2
    }
    
    for keyword, score in practical_keywords.items():
        if keyword in full_text:
            ai_analysis['practical_score'] += score
    
    ai_analysis['practical_score'] = min(20, ai_analysis['practical_score'])
    
    return ai_analysis

def calculate_comprehensive_scores(comprehensive_data):
    """计算综合评分"""
    
    repo_data = comprehensive_data['basic_info']
    contributors = comprehensive_data['contributors']
    commits = comprehensive_data['commits']
    prs = comprehensive_data['pull_requests']
    issues = comprehensive_data['issues']
    releases = comprehensive_data['releases']
    languages = comprehensive_data['languages']
    content = comprehensive_data['content']
    ai_features = comprehensive_data['ai_features']
    
    # 基础数据
    stars = repo_data.get('stargazers_count', 0)
    forks = repo_data.get('forks_count', 0)
    watchers = repo_data.get('watchers_count', 0)
    
    # 计算各项评分
    scores = {}
    
    # 1. 质量评分 (0-50分)
    quality_score = 0
    
    # 星标评分 (0-15分)
    if stars >= 10000:
        quality_score += 15
    elif stars >= 5000:
        quality_score += 12
    elif stars >= 1000:
        quality_score += 10
    elif stars >= 500:
        quality_score += 8
    elif stars >= 100:
        quality_score += 6
    elif stars >= 20:
        quality_score += 3
    
    # 分叉评分 (0-10分)
    if forks >= 2000:
        quality_score += 10
    elif forks >= 500:
        quality_score += 8
    elif forks >= 100:
        quality_score += 6
    elif forks >= 20:
        quality_score += 4
    elif forks >= 5:
        quality_score += 2
    
    # 社区评分 (0-10分)
    if contributors >= 50:
        quality_score += 5
    elif contributors >= 10:
        quality_score += 3
    elif contributors >= 3:
        quality_score += 2
    
    # 文档评分 (0-10分)
    quality_score += content['documentation_score'] * 2 / 3  # 转换为10分制
    if content['has_readme']:
        quality_score += 2
    if content['has_wiki']:
        quality_score += 1
    
    # 活跃度评分 (0-5分)
    if commits['last_commit_date']:
        try:
            last_commit = datetime.fromisoformat(commits['last_commit_date'].replace('Z', '+00:00'))
            days_ago = (datetime.now(last_commit.tzinfo) - last_commit).days
            
            if days_ago <= 7:
                quality_score += 5
            elif days_ago <= 30:
                quality_score += 4
            elif days_ago <= 90:
                quality_score += 3
            elif days_ago <= 365:
                quality_score += 1
        except:
            pass
    
    scores['quality_score'] = min(50, quality_score)
    
    # 2. 影响力评分 (0-30分)
    impact_score = 0
    
    # 基于关注者和分叉的影响力
    impact_score += min(15, stars // 1000)  # 每1000星标1分，最高15分
    impact_score += min(10, watchers // 100)  # 每100关注者1分，最高10分
    impact_score += min(5, forks // 200)  # 每200分叉1分，最高5分
    
    scores['impact_score'] = min(30, impact_score)
    
    # 3. 创新评分 (0-20分)
    innovation_score = ai_features['cutting_edge_score']  # 已经是0-25分，取20分上限
    scores['innovation_score'] = min(20, innovation_score)
    
    # 4. 活跃度评分 (0-10分)
    activity_score = 0
    
    # 基于最近推送时间
    pushed_at = repo_data.get('pushed_at')
    if pushed_at:
        try:
            pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            days_since_push = (datetime.now(pushed_date.tzinfo) - pushed_date).days
            
            if days_since_push <= 7:
                activity_score = 10
            elif days_since_push <= 30:
                activity_score = 8
            elif days_since_push <= 90:
                activity_score = 6
            elif days_since_push <= 180:
                activity_score = 4
            elif days_since_push <= 365:
                activity_score = 2
            
            scores['days_since_pushed'] = days_since_push
        except:
            scores['days_since_pushed'] = 999
    else:
        scores['days_since_pushed'] = 999
    
    scores['activity_score'] = activity_score
    
    # 5. 其他专项评分
    scores['enterprise_score'] = min(20, ai_features['practical_score'])
    scores['production_ready_score'] = min(10, ai_features['practical_score'] // 2)
    scores['api_score'] = 10 if 'api' in repo_data.get('description', '').lower() else 0
    scores['community_health_score'] = min(10, (contributors * 2 + (10 - min(10, issues['open_issues']))))
    
    # 计算比率
    scores['fork_ratio'] = round(forks / max(1, stars), 3)
    
    # 计算趋势评分 (简化版)
    trending_factors = [
        scores['activity_score'] / 10,  # 活跃度权重
        min(1, stars / 1000),  # 受欢迎程度权重  
        min(1, ai_features['cutting_edge_score'] / 25)  # 前沿性权重
    ]
    scores['trending_score'] = int(sum(trending_factors) * 10 / 3)
    
    return scores

def create_enhanced_repo_record(comprehensive_data):
    """创建增强版仓库记录"""
    
    repo_data = comprehensive_data['basic_info']
    contributors = comprehensive_data['contributors']
    commits = comprehensive_data['commits']
    prs = comprehensive_data['pull_requests']
    issues = comprehensive_data['issues']
    releases = comprehensive_data['releases']
    languages = comprehensive_data['languages']
    content = comprehensive_data['content']
    ai_features = comprehensive_data['ai_features']
    
    # 计算综合评分
    scores = calculate_comprehensive_scores(comprehensive_data)
    
    # 构建完整记录
    record = {
        # 基础信息 (保持兼容)
        'id': str(repo_data.get('id')),
        'name': repo_data.get('name'),
        'owner': repo_data.get('owner', {}).get('login'),
        'description': repo_data.get('description'),
        'url': repo_data.get('html_url'),
        'created_at': repo_data.get('created_at'),
        'updated_at': repo_data.get('updated_at'),
        'sync_time': datetime.now().isoformat(),
        
        # 基础GitHub指标
        'stars': repo_data.get('stargazers_count', 0),
        'forks': repo_data.get('forks_count', 0),
        'watchers': repo_data.get('watchers_count', 0),
        'open_issues': repo_data.get('open_issues_count', 0),
        'size_kb': repo_data.get('size', 0),
        'language': languages['primary_language'],
        'default_branch': repo_data.get('default_branch', 'main'),
        'is_fork': repo_data.get('fork', False),
        
        # 时间和活跃度
        'pushed_at': repo_data.get('pushed_at'),
        'last_commit_date': commits['last_commit_date'],
        'days_since_pushed': scores['days_since_pushed'],
        'activity_score': scores['activity_score'],
        
        # 社区和协作
        'contributors_count': contributors,
        'commits_count': commits['total_commits'],
        'pull_requests_count': prs['total_prs'],
        'issues_count': issues['total_issues'],
        'releases_count': releases,
        'fork_ratio': scores['fork_ratio'],
        
        # 质量和成熟度
        'license_type': repo_data.get('license', {}).get('key') if repo_data.get('license') else None,
        'has_readme': content['has_readme'],
        'has_wiki': content['has_wiki'],
        'has_pages': content['has_pages'],
        'has_issues': repo_data.get('has_issues', True),
        'has_projects': repo_data.get('has_projects', False),
        'has_discussions': repo_data.get('has_discussions', False),
        
        # AI/ML特定
        'ai_framework': ai_features['ai_framework'],
        'model_type': ai_features['model_type'],
        'has_model_files': ai_features['has_model_files'],
        'has_paper': ai_features['has_paper'],
        'cutting_edge_score': ai_features['cutting_edge_score'],
        'practical_score': ai_features['practical_score'],
        
        # 商业应用价值
        'enterprise_score': scores['enterprise_score'],
        'production_ready_score': scores['production_ready_score'],
        'api_score': scores['api_score'],
        'documentation_score': content['documentation_score'],
        'community_health_score': scores['community_health_score'],
        
        # 综合评分
        'quality_score': scores['quality_score'],
        'impact_score': scores['impact_score'],
        'innovation_score': scores['innovation_score'],
        
        # 标签和分类
        'topics': ','.join(repo_data.get('topics', [])),
        'tech_stack': languages['tech_stack'],
        
        # 趋势分析
        'trending_score': scores['trending_score'],
        
        # 兼容字段 (保持现有系统正常运行)
        'relevance_score': min(10, scores['quality_score'] // 5),  # 转换为10分制
        'category': classify_repo_category(ai_features, repo_data),
        'tags': generate_smart_tags(ai_features, languages, repo_data),
        'summary': generate_repo_summary(repo_data, ai_features),
        
        # 元数据
        'data_version': 'v2.0',
        'last_analyzed_at': datetime.now().isoformat(),
        'analysis_status': 'completed',
        'data_completeness_score': calculate_data_completeness(comprehensive_data)
    }
    
    return record

def classify_repo_category(ai_features, repo_data):
    """智能分类仓库类别"""
    
    model_type = ai_features['model_type']
    ai_framework = ai_features['ai_framework']
    
    if model_type == 'llm':
        return 'LLM服务与工具'
    elif model_type == 'cv':
        return '计算机视觉'
    elif model_type == 'rag':
        return 'RAG技术'
    elif model_type == 'agent':
        return 'AI代理系统'
    elif model_type == 'generative':
        return '生成式AI'
    elif ai_framework in ['pytorch', 'tensorflow']:
        return '机器学习框架'
    else:
        return '通用AI工具'

def generate_smart_tags(ai_features, languages, repo_data):
    """生成智能标签"""
    
    tags = []
    
    # AI框架标签
    if ai_features['ai_framework'] != 'unknown':
        tags.append(ai_features['ai_framework'].title())
    
    # 模型类型标签
    if ai_features['model_type'] != 'unknown':
        tags.append(ai_features['model_type'].upper())
    
    # 技术栈标签
    primary_lang = languages['primary_language']
    if primary_lang != 'Unknown':
        tags.append(primary_lang)
    
    # 特征标签
    if ai_features['has_model_files']:
        tags.append('Pre-trained Models')
    
    if ai_features['has_paper']:
        tags.append('Research')
    
    if ai_features['cutting_edge_score'] > 15:
        tags.append('Cutting-edge')
    
    if ai_features['practical_score'] > 10:
        tags.append('Production-ready')
    
    return ', '.join(tags[:6])  # 限制标签数量

def generate_repo_summary(repo_data, ai_features):
    """生成仓库摘要"""
    
    name = repo_data.get('name', '')
    description = repo_data.get('description', '')
    
    if description:
        # 截取描述的前50个字符作为摘要
        summary = description[:50] + '...' if len(description) > 50 else description
    else:
        # 基于分析结果生成摘要
        framework = ai_features['ai_framework']
        model_type = ai_features['model_type']
        
        if framework != 'unknown' and model_type != 'unknown':
            summary = f"{name} - {framework.title()}基础的{model_type.upper()}项目"
        elif framework != 'unknown':
            summary = f"{name} - 基于{framework.title()}的AI项目"
        else:
            summary = f"{name} - AI/ML相关项目"
    
    return summary

def calculate_data_completeness(comprehensive_data):
    """计算数据完整性评分"""
    
    total_fields = 20  # 关键字段总数
    completed_fields = 0
    
    repo_data = comprehensive_data['basic_info']
    
    # 检查关键字段完整性
    key_fields = [
        'name', 'owner', 'description', 'stargazers_count', 'forks_count',
        'watchers_count', 'language', 'created_at', 'updated_at', 'pushed_at'
    ]
    
    for field in key_fields:
        if field in repo_data and repo_data[field] is not None:
            completed_fields += 1
    
    # 检查扩展数据完整性
    if comprehensive_data['contributors'] > 0:
        completed_fields += 2
    
    if comprehensive_data['commits']['total_commits'] > 0:
        completed_fields += 2
    
    if comprehensive_data['content']['has_readme']:
        completed_fields += 2
    
    if comprehensive_data['ai_features']['ai_framework'] != 'unknown':
        completed_fields += 2
    
    if comprehensive_data['languages']['primary_language'] != 'Unknown':
        completed_fields += 2
    
    return min(100, int(completed_fields / total_fields * 100))

def save_enhanced_repo_to_database(record):
    """保存增强记录到数据库"""
    
    try:
        # 构建SQL语句 (包含所有新字段)
        sql = """
        INSERT INTO repos (
            id, name, owner, description, url, created_at, updated_at, sync_time,
            stars, forks, watchers, open_issues, size_kb, language, default_branch, is_fork,
            pushed_at, last_commit_date, days_since_pushed, activity_score,
            contributors_count, commits_count, pull_requests_count, issues_count, releases_count, fork_ratio,
            license_type, has_readme, has_wiki, has_pages, has_issues, has_projects, has_discussions,
            ai_framework, model_type, has_model_files, has_paper, cutting_edge_score, practical_score,
            enterprise_score, production_ready_score, api_score, documentation_score, community_health_score,
            quality_score, impact_score, innovation_score,
            topics, tech_stack, trending_score,
            relevance_score, category, tags, summary,
            data_version, last_analyzed_at, analysis_status, data_completeness_score
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(id) DO UPDATE SET
            stars=excluded.stars, forks=excluded.forks, watchers=excluded.watchers,
            pushed_at=excluded.pushed_at, last_commit_date=excluded.last_commit_date,
            days_since_pushed=excluded.days_since_pushed, activity_score=excluded.activity_score,
            contributors_count=excluded.contributors_count, commits_count=excluded.commits_count,
            pull_requests_count=excluded.pull_requests_count, issues_count=excluded.issues_count,
            quality_score=excluded.quality_score, impact_score=excluded.impact_score,
            innovation_score=excluded.innovation_score, trending_score=excluded.trending_score,
            cutting_edge_score=excluded.cutting_edge_score, practical_score=excluded.practical_score,
            data_version=excluded.data_version, last_analyzed_at=excluded.last_analyzed_at,
            analysis_status=excluded.analysis_status, sync_time=excluded.sync_time
        """
        
        # 构建参数列表
        params = [
            record['id'], record['name'], record['owner'], record['description'], 
            record['url'], record['created_at'], record['updated_at'], record['sync_time'],
            record['stars'], record['forks'], record['watchers'], record['open_issues'],
            record['size_kb'], record['language'], record['default_branch'], record['is_fork'],
            record['pushed_at'], record['last_commit_date'], record['days_since_pushed'], record['activity_score'],
            record['contributors_count'], record['commits_count'], record['pull_requests_count'], 
            record['issues_count'], record['releases_count'], record['fork_ratio'],
            record['license_type'], record['has_readme'], record['has_wiki'], record['has_pages'],
            record['has_issues'], record['has_projects'], record['has_discussions'],
            record['ai_framework'], record['model_type'], record['has_model_files'], record['has_paper'],
            record['cutting_edge_score'], record['practical_score'],
            record['enterprise_score'], record['production_ready_score'], record['api_score'],
            record['documentation_score'], record['community_health_score'],
            record['quality_score'], record['impact_score'], record['innovation_score'],
            record['topics'], record['tech_stack'], record['trending_score'],
            record['relevance_score'], record['category'], record['tags'], record['summary'],
            record['data_version'], record['last_analyzed_at'], record['analysis_status'], 
            record['data_completeness_score']
        ]
        
        # 执行数据库操作
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql,
            params=params
        )
        
        if response.success:
            print(f"✅ 成功保存 {record['owner']}/{record['name']} 的增强数据")
            
            # 显示关键指标
            print(f"   📊 质量评分: {record['quality_score']}/50")
            print(f"   🎯 影响力评分: {record['impact_score']}/30") 
            print(f"   💡 创新评分: {record['innovation_score']}/20")
            print(f"   ⚡ 活跃度评分: {record['activity_score']}/10")
            print(f"   🤖 AI框架: {record['ai_framework']}")
            print(f"   🏷️ 模型类型: {record['model_type']}")
            
            return True
        else:
            print(f"❌ 保存失败: {response}")
            return False
            
    except Exception as e:
        print(f"❌ 数据库操作错误: {e}")
        return False

def main_enhanced_collection():
    """主要的增强数据收集流程"""
    
    print("🚀 启动增强版GitHub AI仓库数据收集系统 v2.0")
    print("=" * 70)
    
    # 测试项目列表 (可扩展)
    test_repos = [
        ("huggingface", "transformers"),
        ("pytorch", "pytorch"),
        ("tensorflow", "tensorflow"),
        ("openai", "openai-python"),
        ("langchain-ai", "langchain")
    ]
    
    successful_collections = 0
    
    for owner, repo_name in test_repos:
        print(f"\n📊 正在处理 {owner}/{repo_name}...")
        print("-" * 50)
        
        # 获取完整数据
        comprehensive_data = fetch_comprehensive_repo_data(owner, repo_name)
        
        if comprehensive_data:
            # 创建增强记录
            record = create_enhanced_repo_record(comprehensive_data)
            
            # 保存到数据库
            if save_enhanced_repo_to_database(record):
                successful_collections += 1
        
        # API速率限制延迟
        print("⏱️ 等待2秒...")
        time.sleep(2)
    
    print(f"\n🎉 增强数据收集完成!")
    print("=" * 70)
    print(f"✅ 成功收集: {successful_collections}/{len(test_repos)} 个项目")
    print(f"💾 数据已保存到Cloudflare D1数据库")
    print(f"📊 包含59个新增字段的完整数据")

if __name__ == "__main__":
    main_enhanced_collection()
