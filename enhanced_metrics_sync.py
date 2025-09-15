#!/usr/bin/env python3
"""
增强指标数据收集系统
集成GitHub完整API + AI特定分析 + 商业价值评估
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from cloudflare import Cloudflare
from dotenv import load_dotenv
from enhanced_metrics_config import *

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
    'User-Agent': 'AI-Repo-Monitor/1.0'
}

# Cloudflare客户端
cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

def fetch_enhanced_repo_data(owner, repo_name):
    """获取GitHub仓库的完整增强数据"""
    
    try:
        print(f"📊 正在获取 {owner}/{repo_name} 的增强数据...")
        
        # 基础仓库信息
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        repo_response = requests.get(repo_url, headers=GITHUB_HEADERS)
        
        if repo_response.status_code != 200:
            print(f"❌ 获取仓库信息失败: {repo_response.status_code}")
            return None
            
        repo_data = repo_response.json()
        
        # 获取贡献者信息
        contributors_data = fetch_contributors_data(owner, repo_name)
        
        # 获取提交信息
        commits_data = fetch_commits_data(owner, repo_name)
        
        # 获取发布信息
        releases_data = fetch_releases_data(owner, repo_name)
        
        # 获取问题和PR信息
        issues_data = fetch_issues_data(owner, repo_name)
        pulls_data = fetch_pulls_data(owner, repo_name)
        
        # 获取语言信息
        languages_data = fetch_languages_data(owner, repo_name)
        
        # 获取内容分析 (README, 文档等)
        content_analysis = analyze_repo_content(owner, repo_name)
        
        # 整合所有数据
        enhanced_data = {
            'basic_info': repo_data,
            'contributors': contributors_data,
            'commits': commits_data,
            'releases': releases_data,
            'issues': issues_data,
            'pulls': pulls_data,
            'languages': languages_data,
            'content_analysis': content_analysis
        }
        
        return enhanced_data
        
    except Exception as e:
        print(f"❌ 获取增强数据时出错: {e}")
        return None

def fetch_contributors_data(owner, repo_name):
    """获取贡献者数据"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
        response = requests.get(url, headers=GITHUB_HEADERS)
        
        if response.status_code == 200:
            contributors = response.json()
            return {
                'count': len(contributors),
                'top_contributors': contributors[:10] if contributors else []
            }
    except Exception as e:
        print(f"⚠️ 获取贡献者数据失败: {e}")
    
    return {'count': 0, 'top_contributors': []}

def fetch_commits_data(owner, repo_name):
    """获取提交数据"""
    try:
        # 获取最近30天的提交
        since_date = (datetime.now() - timedelta(days=30)).isoformat()
        url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
        params = {'since': since_date, 'per_page': 100}
        
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        
        if response.status_code == 200:
            commits = response.json()
            
            # 计算提交频率
            commit_dates = []
            for commit in commits:
                if commit.get('commit', {}).get('author', {}).get('date'):
                    commit_dates.append(commit['commit']['author']['date'])
            
            return {
                'recent_commits_count': len(commits),
                'commit_dates': commit_dates,
                'frequency_score': min(10, len(commits) // 3)  # 简单的频率评分
            }
    except Exception as e:
        print(f"⚠️ 获取提交数据失败: {e}")
    
    return {'recent_commits_count': 0, 'commit_dates': [], 'frequency_score': 0}

def fetch_releases_data(owner, repo_name):
    """获取发布数据"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/releases"
        response = requests.get(url, headers=GITHUB_HEADERS)
        
        if response.status_code == 200:
            releases = response.json()
            
            # 分析发布频率
            recent_releases = []
            for release in releases:
                if release.get('published_at'):
                    pub_date = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00'))
                    if (datetime.now(pub_date.tzinfo) - pub_date).days <= 365:
                        recent_releases.append(release)
            
            return {
                'total_releases': len(releases),
                'recent_releases': len(recent_releases),
                'latest_release': releases[0] if releases else None
            }
    except Exception as e:
        print(f"⚠️ 获取发布数据失败: {e}")
    
    return {'total_releases': 0, 'recent_releases': 0, 'latest_release': None}

def fetch_issues_data(owner, repo_name):
    """获取问题数据"""
    try:
        # 获取开放问题
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
        params = {'state': 'open', 'per_page': 100}
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        
        open_issues = []
        if response.status_code == 200:
            open_issues = response.json()
        
        # 获取已关闭问题 (最近30天)
        params = {'state': 'closed', 'per_page': 100}
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        
        closed_issues = []
        if response.status_code == 200:
            closed_issues = response.json()
        
        return {
            'open_count': len(open_issues),
            'closed_count': len(closed_issues),
            'response_quality': calculate_issue_response_quality(open_issues + closed_issues)
        }
    except Exception as e:
        print(f"⚠️ 获取问题数据失败: {e}")
    
    return {'open_count': 0, 'closed_count': 0, 'response_quality': 0}

def fetch_pulls_data(owner, repo_name):
    """获取Pull Request数据"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
        params = {'state': 'all', 'per_page': 100}
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        
        if response.status_code == 200:
            pulls = response.json()
            
            open_prs = [pr for pr in pulls if pr['state'] == 'open']
            merged_prs = [pr for pr in pulls if pr.get('merged_at')]
            
            return {
                'total_prs': len(pulls),
                'open_prs': len(open_prs),
                'merged_prs': len(merged_prs),
                'merge_rate': len(merged_prs) / len(pulls) if pulls else 0
            }
    except Exception as e:
        print(f"⚠️ 获取PR数据失败: {e}")
    
    return {'total_prs': 0, 'open_prs': 0, 'merged_prs': 0, 'merge_rate': 0}

def fetch_languages_data(owner, repo_name):
    """获取编程语言数据"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
        response = requests.get(url, headers=GITHUB_HEADERS)
        
        if response.status_code == 200:
            languages = response.json()
            
            total_bytes = sum(languages.values())
            language_percentages = {}
            
            for lang, bytes_count in languages.items():
                percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                language_percentages[lang] = round(percentage, 2)
            
            primary_language = max(language_percentages.items(), key=lambda x: x[1])[0] if language_percentages else 'Unknown'
            
            return {
                'languages': language_percentages,
                'primary_language': primary_language,
                'language_count': len(languages)
            }
    except Exception as e:
        print(f"⚠️ 获取语言数据失败: {e}")
    
    return {'languages': {}, 'primary_language': 'Unknown', 'language_count': 0}

def analyze_repo_content(owner, repo_name):
    """分析仓库内容质量"""
    try:
        analysis = {
            'has_readme': False,
            'has_tests': False,
            'has_ci_cd': False,
            'has_documentation': False,
            'has_examples': False,
            'has_license': False,
            'readme_quality_score': 0
        }
        
        # 检查README
        readme_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
        readme_response = requests.get(readme_url, headers=GITHUB_HEADERS)
        
        if readme_response.status_code == 200:
            analysis['has_readme'] = True
            readme_data = readme_response.json()
            # 简单的README质量评分
            content_size = readme_data.get('size', 0)
            analysis['readme_quality_score'] = min(10, content_size // 1000)
        
        # 检查仓库内容结构
        contents_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
        contents_response = requests.get(contents_url, headers=GITHUB_HEADERS)
        
        if contents_response.status_code == 200:
            contents = contents_response.json()
            
            for item in contents:
                name = item.get('name', '').lower()
                item_type = item.get('type', '')
                
                # 检查测试目录
                if 'test' in name and item_type == 'dir':
                    analysis['has_tests'] = True
                
                # 检查文档目录
                if name in ['docs', 'doc', 'documentation'] and item_type == 'dir':
                    analysis['has_documentation'] = True
                
                # 检查示例目录
                if name in ['examples', 'example', 'demo'] and item_type == 'dir':
                    analysis['has_examples'] = True
                
                # 检查CI/CD配置
                if name in ['.github', '.travis.yml', '.gitlab-ci.yml', 'jenkinsfile']:
                    analysis['has_ci_cd'] = True
                
                # 检查许可证文件
                if 'license' in name:
                    analysis['has_license'] = True
        
        return analysis
        
    except Exception as e:
        print(f"⚠️ 内容分析失败: {e}")
        return {
            'has_readme': False, 'has_tests': False, 'has_ci_cd': False,
            'has_documentation': False, 'has_examples': False, 'has_license': False,
            'readme_quality_score': 0
        }

def calculate_issue_response_quality(issues):
    """计算问题响应质量评分"""
    if not issues:
        return 5  # 默认中等评分
    
    total_response_time = 0
    responded_issues = 0
    
    for issue in issues:
        if issue.get('comments', 0) > 0:
            responded_issues += 1
            # 简化计算：假设有评论就是有响应
    
    response_rate = responded_issues / len(issues) if issues else 0
    return int(response_rate * 10)  # 转换为0-10分

def analyze_ai_specific_indicators(enhanced_data):
    """分析AI特定指标"""
    repo_data = enhanced_data['basic_info']
    content_analysis = enhanced_data['content_analysis']
    
    ai_analysis = {
        'has_model_files': False,
        'has_research_paper': False,
        'has_deployment_config': False,
        'ai_framework': 'unknown',
        'model_type': 'unknown',
        'cutting_edge_score': 0,
        'research_quality_score': 0,
        'practical_deployment_score': 0
    }
    
    name = repo_data.get('name', '').lower()
    description = repo_data.get('description', '').lower() if repo_data.get('description') else ''
    full_text = f"{name} {description}"
    
    # 检测AI框架
    frameworks = {
        'pytorch': ['pytorch', 'torch'],
        'tensorflow': ['tensorflow', 'tf'],
        'huggingface': ['huggingface', 'transformers'],
        'langchain': ['langchain'],
        'openai': ['openai', 'gpt'],
        'anthropic': ['claude', 'anthropic']
    }
    
    for framework, keywords in frameworks.items():
        if any(keyword in full_text for keyword in keywords):
            ai_analysis['ai_framework'] = framework
            break
    
    # 检测模型类型
    model_types = {
        'llm': ['llm', 'language model', 'gpt', 'bert', 'transformer'],
        'cv': ['computer vision', 'image', 'detection', 'yolo', 'opencv'],
        'nlp': ['nlp', 'natural language', 'text processing'],
        'multimodal': ['multimodal', 'vision-language', 'clip'],
        'rag': ['rag', 'retrieval', 'vector database'],
        'agent': ['agent', 'autonomous', 'planning']
    }
    
    for model_type, keywords in model_types.items():
        if any(keyword in full_text for keyword in keywords):
            ai_analysis['model_type'] = model_type
            break
    
    # 计算前沿性评分
    cutting_edge_keywords = [
        'gpt-4', 'claude', 'llama', 'gemini', 'multimodal', 
        'agent', 'reasoning', 'sota', '2024'
    ]
    
    ai_analysis['cutting_edge_score'] = sum(
        3 for keyword in cutting_edge_keywords 
        if keyword in full_text
    )
    
    # 计算研究质量评分
    research_keywords = ['paper', 'arxiv', 'research', 'publication', 'cite']
    ai_analysis['research_quality_score'] = sum(
        2 for keyword in research_keywords 
        if keyword in full_text
    )
    
    # 计算实用部署评分
    deployment_keywords = ['api', 'docker', 'deploy', 'production', 'demo']
    ai_analysis['practical_deployment_score'] = sum(
        2 for keyword in deployment_keywords 
        if keyword in full_text
    )
    
    # 检查是否有模型文件
    if any(keyword in full_text for keyword in ['model', 'checkpoint', 'weights']):
        ai_analysis['has_model_files'] = True
    
    # 检查是否有研究论文
    if any(keyword in full_text for keyword in ['paper', 'arxiv', 'research']):
        ai_analysis['has_research_paper'] = True
    
    # 检查是否可部署
    if any(keyword in full_text for keyword in ['api', 'docker', 'deploy']):
        ai_analysis['has_deployment_config'] = True
    
    return ai_analysis

def calculate_commercial_potential(enhanced_data):
    """计算商业潜力评分"""
    repo_data = enhanced_data['basic_info']
    
    score = 0
    
    # 基于星标和分叉的商业价值
    stars = repo_data.get('stargazers_count', 0)
    forks = repo_data.get('forks_count', 0)
    
    if stars > 10000:
        score += 15
    elif stars > 5000:
        score += 12
    elif stars > 1000:
        score += 8
    
    if forks > 1000:
        score += 10
    elif forks > 200:
        score += 6
    
    # 基于描述的商业指标
    description = repo_data.get('description', '').lower() if repo_data.get('description') else ''
    
    commercial_keywords = {
        'enterprise': 5, 'business': 3, 'commercial': 4,
        'production': 4, 'api': 3, 'service': 3,
        'platform': 4, 'saas': 5, 'cloud': 3
    }
    
    for keyword, weight in commercial_keywords.items():
        if keyword in description:
            score += weight
    
    # 行业支持评估
    industry_indicators = {
        'google': 8, 'microsoft': 8, 'openai': 10, 'meta': 8,
        'amazon': 6, 'nvidia': 8, 'anthropic': 9, 'huggingface': 7
    }
    
    full_text = f"{repo_data.get('full_name', '')} {description}".lower()
    
    for company, weight in industry_indicators.items():
        if company in full_text:
            score += weight
            break
    
    return min(20, score)

def create_enhanced_repo_record(enhanced_data):
    """创建增强版仓库记录"""
    repo_data = enhanced_data['basic_info']
    contributors = enhanced_data['contributors']
    commits = enhanced_data['commits']
    releases = enhanced_data['releases']
    issues = enhanced_data['issues']
    pulls = enhanced_data['pulls']
    languages = enhanced_data['languages']
    content_analysis = enhanced_data['content_analysis']
    
    # AI特定分析
    ai_analysis = analyze_ai_specific_indicators(enhanced_data)
    
    # 商业价值分析
    commercial_score = calculate_commercial_potential(enhanced_data)
    
    # 计算综合评分
    enhanced_score = calculate_enhanced_score(repo_data, {
        'contributors': contributors['count'],
        'has_readme': content_analysis['has_readme'],
        'has_tests': content_analysis['has_tests'],
        'has_ci': content_analysis['has_ci_cd']
    })
    
    # 确定成熟度等级
    if enhanced_score >= 80:
        maturity_level = 'production'
    elif enhanced_score >= 60:
        maturity_level = 'mature'
    elif enhanced_score >= 40:
        maturity_level = 'developing'
    else:
        maturity_level = 'experimental'
    
    # 确定社区健康状态
    community_score = (contributors['count'] * 2 + 
                      commits['frequency_score'] * 3 + 
                      issues['response_quality']) / 6
    
    if community_score >= 8:
        community_health = 'excellent'
    elif community_score >= 6:
        community_health = 'good'
    elif community_score >= 4:
        community_health = 'fair'
    else:
        community_health = 'poor'
    
    # 确定创新水平
    innovation_score = ai_analysis['cutting_edge_score'] + ai_analysis['research_quality_score']
    
    if innovation_score >= 15:
        innovation_level = 'cutting-edge'
    elif innovation_score >= 10:
        innovation_level = 'high'
    elif innovation_score >= 5:
        innovation_level = 'medium'
    else:
        innovation_level = 'low'
    
    # 确定商业潜力等级
    if commercial_score >= 15:
        commercial_potential = 'very-high'
    elif commercial_score >= 10:
        commercial_potential = 'high'
    elif commercial_score >= 5:
        commercial_potential = 'medium'
    else:
        commercial_potential = 'low'
    
    # 构建完整记录
    record = {
        # 基础信息
        'id': str(repo_data.get('id')),
        'name': repo_data.get('name'),
        'owner': repo_data.get('owner', {}).get('login'),
        'description': repo_data.get('description'),
        'url': repo_data.get('html_url'),
        'created_at': repo_data.get('created_at'),
        'updated_at': repo_data.get('updated_at'),
        
        # 基础指标
        'stars': repo_data.get('stargazers_count', 0),
        'forks': repo_data.get('forks_count', 0),
        'watchers_count': repo_data.get('watchers_count', 0),
        'open_issues_count': repo_data.get('open_issues_count', 0),
        
        # 增强评分
        'enhanced_score': enhanced_score,
        'ai_maturity_level': maturity_level,
        'community_health': community_health,
        'innovation_level': innovation_level,
        'commercial_potential': commercial_potential,
        
        # GitHub高级指标
        'contributors_count': contributors['count'],
        'issues_count': issues['open_count'] + issues['closed_count'],
        'pull_requests_count': pulls['total_prs'],
        'last_commit_date': repo_data.get('pushed_at'),
        'last_release_date': releases['latest_release']['published_at'] if releases['latest_release'] else None,
        'commit_frequency_score': commits['frequency_score'],
        
        # AI特定指标
        'has_model_files': ai_analysis['has_model_files'],
        'has_research_paper': ai_analysis['has_research_paper'],
        'has_deployment_config': ai_analysis['has_deployment_config'],
        'ai_framework': ai_analysis['ai_framework'],
        'model_type': ai_analysis['model_type'],
        'cutting_edge_score': ai_analysis['cutting_edge_score'],
        'research_quality_score': ai_analysis['research_quality_score'],
        'practical_deployment_score': ai_analysis['practical_deployment_score'],
        
        # 项目质量指标
        'primary_language': languages['primary_language'],
        'languages_count': languages['language_count'],
        'repo_size_kb': repo_data.get('size', 0),
        'has_tests': content_analysis['has_tests'],
        'has_ci_cd': content_analysis['has_ci_cd'],
        'has_documentation': content_analysis['has_documentation'],
        'license_type': repo_data.get('license', {}).get('key') if repo_data.get('license') else None,
        
        # 商业价值指标
        'enterprise_adoption_score': commercial_score,
        'dependency_count': 0,  # 需要额外API调用获取
        
        # 元数据
        'github_topics': ','.join(repo_data.get('topics', [])),
        'technology_stack': ','.join(languages['languages'].keys()),
        'fork_to_star_ratio': (repo_data.get('forks_count', 0) / repo_data.get('stargazers_count', 1)),
        
        # 质量评分
        'code_quality_score': min(20, content_analysis['readme_quality_score'] + 
                                (5 if content_analysis['has_tests'] else 0) +
                                (5 if content_analysis['has_ci_cd'] else 0)),
        'maintenance_score': min(20, commits['frequency_score'] * 2),
        
        # 时间戳
        'sync_time': datetime.now().isoformat()
    }
    
    return record

def save_enhanced_record_to_database(record):
    """保存增强记录到数据库"""
    try:
        sql = """
        INSERT INTO repos (
            id, name, owner, description, url, created_at, updated_at,
            stars, forks, watchers_count, open_issues_count,
            enhanced_score, ai_maturity_level, community_health, innovation_level, commercial_potential,
            contributors_count, issues_count, pull_requests_count, last_commit_date, last_release_date,
            commit_frequency_score, has_model_files, has_research_paper, has_deployment_config,
            ai_framework, model_type, cutting_edge_score, research_quality_score, practical_deployment_score,
            primary_language, languages_count, repo_size_kb, has_tests, has_ci_cd, has_documentation,
            license_type, enterprise_adoption_score, dependency_count, github_topics, technology_stack,
            fork_to_star_ratio, code_quality_score, maintenance_score, sync_time
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(id) DO UPDATE SET
            stars=excluded.stars, forks=excluded.forks, watchers_count=excluded.watchers_count,
            enhanced_score=excluded.enhanced_score, ai_maturity_level=excluded.ai_maturity_level,
            community_health=excluded.community_health, innovation_level=excluded.innovation_level,
            commercial_potential=excluded.commercial_potential, contributors_count=excluded.contributors_count,
            issues_count=excluded.issues_count, pull_requests_count=excluded.pull_requests_count,
            last_commit_date=excluded.last_commit_date, commit_frequency_score=excluded.commit_frequency_score,
            cutting_edge_score=excluded.cutting_edge_score, research_quality_score=excluded.research_quality_score,
            practical_deployment_score=excluded.practical_deployment_score, code_quality_score=excluded.code_quality_score,
            maintenance_score=excluded.maintenance_score, sync_time=excluded.sync_time
        """
        
        params = [
            record['id'], record['name'], record['owner'], record['description'], record['url'],
            record['created_at'], record['updated_at'], record['stars'], record['forks'],
            record['watchers_count'], record['open_issues_count'], record['enhanced_score'],
            record['ai_maturity_level'], record['community_health'], record['innovation_level'],
            record['commercial_potential'], record['contributors_count'], record['issues_count'],
            record['pull_requests_count'], record['last_commit_date'], record['last_release_date'],
            record['commit_frequency_score'], record['has_model_files'], record['has_research_paper'],
            record['has_deployment_config'], record['ai_framework'], record['model_type'],
            record['cutting_edge_score'], record['research_quality_score'], record['practical_deployment_score'],
            record['primary_language'], record['languages_count'], record['repo_size_kb'],
            record['has_tests'], record['has_ci_cd'], record['has_documentation'], record['license_type'],
            record['enterprise_adoption_score'], record['dependency_count'], record['github_topics'],
            record['technology_stack'], record['fork_to_star_ratio'], record['code_quality_score'],
            record['maintenance_score'], record['sync_time']
        ]
        
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql,
            params=params
        )
        
        if response.success:
            print(f"✅ 成功保存 {record['owner']}/{record['name']} 的增强数据")
            return True
        else:
            print(f"❌ 保存失败: {response}")
            return False
            
    except Exception as e:
        print(f"❌ 数据库操作错误: {e}")
        return False

def main_enhanced_collection():
    """主要的增强数据收集流程"""
    print("🚀 启动GitHub AI仓库增强指标收集系统")
    print("=" * 60)
    
    # 示例：收集几个知名AI项目的增强数据
    test_repos = [
        ("huggingface", "transformers"),
        ("openai", "gpt-3"),
        ("microsoft", "DeepSpeed"),
        ("google-research", "bert"),
        ("facebookresearch", "llama")
    ]
    
    successful_collections = 0
    
    for owner, repo_name in test_repos:
        print(f"\n📊 正在处理 {owner}/{repo_name}...")
        
        # 获取增强数据
        enhanced_data = fetch_enhanced_repo_data(owner, repo_name)
        
        if enhanced_data:
            # 创建记录
            record = create_enhanced_repo_record(enhanced_data)
            
            # 保存到数据库
            if save_enhanced_record_to_database(record):
                successful_collections += 1
                
                # 显示收集结果
                print(f"📈 增强评分: {record['enhanced_score']}/100")
                print(f"🤖 AI成熟度: {record['ai_maturity_level']}")
                print(f"👥 社区健康: {record['community_health']}")
                print(f"💡 创新水平: {record['innovation_level']}")
                print(f"💼 商业潜力: {record['commercial_potential']}")
                
        # API速率限制延迟
        time.sleep(2)
    
    print(f"\n🎉 增强数据收集完成!")
    print(f"✅ 成功收集: {successful_collections}/{len(test_repos)} 个项目")
    print(f"💾 数据已保存到Cloudflare D1数据库")

if __name__ == "__main__":
    main_enhanced_collection()
