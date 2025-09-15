#!/usr/bin/env python3
"""
更新活跃度数据脚本
专门收集和更新 pushed_at, watchers, activity_score 等关键字段
"""

import os
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
    'User-Agent': 'Activity-Data-Updater/1.0'
}

# Cloudflare客户端
cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

def fetch_repo_activity_data(owner, repo_name):
    """获取仓库的活跃度数据"""
    
    try:
        print(f"📊 正在获取 {owner}/{repo_name} 的活跃度数据...")
        
        # 获取仓库基础信息 (包含 pushed_at 和 watchers_count)
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        response = requests.get(repo_url, headers=GITHUB_HEADERS)
        
        if response.status_code != 200:
            print(f"❌ 获取失败: {response.status_code}")
            return None
            
        repo_data = response.json()
        
        # 提取关键数据
        activity_data = {
            'pushed_at': repo_data.get('pushed_at'),
            'watchers': repo_data.get('watchers_count', 0),
            'stars': repo_data.get('stargazers_count', 0),
            'forks': repo_data.get('forks_count', 0)
        }
        
        return activity_data
        
    except Exception as e:
        print(f"❌ 获取活跃度数据失败: {e}")
        return None

def calculate_activity_score(pushed_at):
    """基于推送时间计算活跃度评分"""
    
    if not pushed_at:
        return 0, 999
    
    try:
        # 解析推送时间
        pushed_date = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
        current_time = datetime.now(pushed_date.tzinfo)
        
        # 计算距离现在的天数
        days_since_pushed = (current_time - pushed_date).days
        
        # 计算活跃度评分 (0-10分)
        if days_since_pushed <= 7:
            activity_score = 10  # 极活跃
        elif days_since_pushed <= 30:
            activity_score = 8   # 活跃
        elif days_since_pushed <= 90:
            activity_score = 6   # 中等活跃
        elif days_since_pushed <= 180:
            activity_score = 4   # 一般
        elif days_since_pushed <= 365:
            activity_score = 2   # 不活跃
        else:
            activity_score = 0   # 停止维护
        
        return activity_score, days_since_pushed
        
    except Exception as e:
        print(f"⚠️ 计算活跃度评分失败: {e}")
        return 0, 999

def update_repo_activity_in_database(repo_id, activity_data):
    """更新数据库中的活跃度数据"""
    
    try:
        # 计算活跃度评分
        activity_score, days_since_pushed = calculate_activity_score(activity_data['pushed_at'])
        
        # 构建更新SQL
        sql = """
        UPDATE repos SET
            pushed_at = ?,
            watchers = ?,
            activity_score = ?,
            days_since_pushed = ?
        WHERE id = ?
        """
        
        params = [
            activity_data['pushed_at'],
            activity_data['watchers'],
            activity_score,
            days_since_pushed,
            repo_id
        ]
        
        # 执行更新
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql,
            params=params
        )
        
        if response.success:
            print(f"✅ 更新成功")
            print(f"   📅 最后推送: {activity_data['pushed_at']}")
            print(f"   👀 关注者: {activity_data['watchers']}")
            print(f"   ⚡ 活跃度评分: {activity_score}/10")
            print(f"   📊 距今天数: {days_since_pushed} 天")
            return True
        else:
            print(f"❌ 更新失败: {response}")
            return False
            
    except Exception as e:
        print(f"❌ 数据库更新错误: {e}")
        return False

def get_all_repos_from_database():
    """从数据库获取所有仓库信息"""
    
    try:
        sql = "SELECT id, name, owner FROM repos ORDER BY stars DESC"
        
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql
        )
        
        if response.success and response.result:
            repos = response.result[0].results
            print(f"📊 从数据库获取到 {len(repos)} 个仓库")
            return repos
        else:
            print("❌ 获取仓库列表失败")
            return []
            
    except Exception as e:
        print(f"❌ 数据库查询错误: {e}")
        return []

def batch_update_activity_data(limit=10):
    """批量更新活跃度数据"""
    
    print("🚀 开始批量更新活跃度数据")
    print("=" * 50)
    
    # 获取仓库列表
    repos = get_all_repos_from_database()
    
    if not repos:
        print("❌ 没有找到仓库数据")
        return
    
    # 限制更新数量 (避免API限制)
    repos_to_update = repos[:limit]
    
    successful_updates = 0
    
    for i, repo in enumerate(repos_to_update, 1):
        print(f"\n📊 [{i}/{len(repos_to_update)}] 更新 {repo['owner']}/{repo['name']}")
        print("-" * 40)
        
        # 获取活跃度数据
        activity_data = fetch_repo_activity_data(repo['owner'], repo['name'])
        
        if activity_data:
            # 更新数据库
            if update_repo_activity_in_database(repo['id'], activity_data):
                successful_updates += 1
        
        # API限制延迟 (每分钟最多30次请求)
        import time
        time.sleep(2)  # 2秒延迟
    
    print(f"\n🎉 批量更新完成!")
    print("=" * 50)
    print(f"✅ 成功更新: {successful_updates}/{len(repos_to_update)} 个仓库")

def test_activity_scoring():
    """测试活跃度评分算法"""
    
    print("🧪 测试活跃度评分算法")
    print("=" * 40)
    
    # 测试用例
    test_cases = [
        ("2024-01-05T10:00:00Z", "今天推送"),
        ("2024-01-01T10:00:00Z", "4天前推送"),
        ("2023-12-01T10:00:00Z", "1个月前推送"),
        ("2023-10-01T10:00:00Z", "3个月前推送"),
        ("2023-06-01T10:00:00Z", "6个月前推送"),
        ("2022-01-01T10:00:00Z", "2年前推送"),
    ]
    
    for pushed_at, description in test_cases:
        score, days = calculate_activity_score(pushed_at)
        print(f"📅 {description}: {score}/10分 ({days}天前)")
    
    print("\n✅ 活跃度评分算法测试完成")

def show_activity_statistics():
    """显示活跃度统计"""
    
    try:
        print("\n📊 数据库活跃度统计")
        print("=" * 40)
        
        # 查询活跃度分布
        sql = """
        SELECT 
            CASE 
                WHEN activity_score >= 8 THEN '高活跃 (8-10分)'
                WHEN activity_score >= 6 THEN '中等活跃 (6-7分)'
                WHEN activity_score >= 2 THEN '低活跃 (2-5分)'
                ELSE '停止维护 (0-1分)'
            END as activity_level,
            COUNT(*) as count,
            ROUND(AVG(stars), 0) as avg_stars,
            ROUND(AVG(watchers), 0) as avg_watchers
        FROM repos 
        WHERE activity_score IS NOT NULL
        GROUP BY activity_level
        ORDER BY MIN(activity_score) DESC
        """
        
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql
        )
        
        if response.success and response.result:
            results = response.result[0].results
            
            for row in results:
                print(f"🎯 {row['activity_level']}: {row['count']}个项目")
                print(f"   平均星标: {row['avg_stars']}, 平均关注: {row['avg_watchers']}")
        
        # 显示最活跃的项目
        print(f"\n🔥 最活跃的AI项目 (Top 10)")
        print("-" * 40)
        
        sql_top = """
        SELECT name, owner, activity_score, days_since_pushed, stars, watchers
        FROM repos 
        WHERE activity_score IS NOT NULL
        ORDER BY activity_score DESC, stars DESC
        LIMIT 10
        """
        
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql_top
        )
        
        if response.success and response.result:
            results = response.result[0].results
            
            for i, repo in enumerate(results, 1):
                print(f"{i:2d}. {repo['owner']}/{repo['name']}")
                print(f"    ⚡{repo['activity_score']}/10分 | ⭐{repo['stars']} | 👀{repo['watchers']} | 📅{repo['days_since_pushed']}天前")
        
    except Exception as e:
        print(f"❌ 统计查询失败: {e}")

def main():
    """主函数"""
    
    print("🎯 GitHub AI仓库活跃度数据更新器")
    print("🎯 专门更新 pushed_at, watchers, activity_score 字段")
    print()
    
    while True:
        print("\n请选择操作:")
        print("1. 📊 批量更新活跃度数据 (前10个)")
        print("2. 📊 批量更新活跃度数据 (前50个)")
        print("3. 🧪 测试活跃度评分算法")
        print("4. 📈 查看活跃度统计")
        print("5. 🚪 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            batch_update_activity_data(limit=10)
        elif choice == "2":
            batch_update_activity_data(limit=50)
        elif choice == "3":
            test_activity_scoring()
        elif choice == "4":
            show_activity_statistics()
        elif choice == "5":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
