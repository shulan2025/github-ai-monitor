#!/usr/bin/env python3
"""
快速测试增强版搜索策略
验证调整后的参数能否获得更多数据
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def quick_search_test():
    """快速搜索测试"""
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    
    if not GITHUB_TOKEN:
        print("❌ 未设置GITHUB_TOKEN")
        return
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = "https://api.github.com/search/repositories"
    
    # 测试不同的搜索策略
    test_cases = [
        {
            "name": "LLM项目-30天-100星",
            "query": "LLM OR transformer stars:>100 created:2025-08-06..2025-09-05 is:public archived:false",
            "expected": "中等数量"
        },
        {
            "name": "LLM项目-30天-50星", 
            "query": "LLM OR transformer stars:>50 created:2025-08-06..2025-09-05 is:public archived:false",
            "expected": "更多数量"
        },
        {
            "name": "LLM项目-30天-20星",
            "query": "LLM OR transformer stars:>20 created:2025-08-06..2025-09-05 is:public archived:false",
            "expected": "大量数据"
        },
        {
            "name": "机器学习-90天-20星",
            "query": "machine-learning OR deep-learning stars:>20 created:2025-06-08..2025-09-05 is:public archived:false",
            "expected": "大量数据"
        },
        {
            "name": "AI综合-90天-10星",
            "query": "(artificial-intelligence OR AI OR machine-learning) stars:>10 created:2025-06-08..2025-09-05 is:public archived:false",
            "expected": "海量数据"
        }
    ]
    
    print("🧪 快速搜索测试")
    print("=" * 60)
    
    total_found = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   查询: {test_case['query'][:50]}...")
        
        try:
            params = {
                "q": test_case["query"],
                "sort": "stars",
                "order": "desc",
                "per_page": 30  # 只取前30个测试
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            total_count = data.get("total_count", 0)
            repos = data.get("items", [])
            
            print(f"   结果: 找到 {total_count} 个项目 (显示前{len(repos)}个)")
            
            if repos:
                # 显示前3个项目
                for j, repo in enumerate(repos[:3]):
                    print(f"      {j+1}. {repo['name']} - ⭐{repo['stargazers_count']} - {repo['owner']['login']}")
                
                total_found += len(repos)
            
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
    
    print(f"\n📊 测试总结:")
    print(f"   测试用例: {len(test_cases)} 个")
    print(f"   获得数据: {total_found} 条")
    print(f"   平均每次: {total_found/len(test_cases):.1f} 条")
    
    # 预测全量收集效果
    if total_found > 0:
        # 假设我们执行60次搜索（多个关键词组合）
        estimated_total = total_found * 4  # 考虑不同时间窗口和排序
        print(f"   预计全量: {estimated_total} 条候选")
        print(f"   预计有效: {estimated_total * 0.25:.0f} 条 (假设25%有效率)")
        
        if estimated_total * 0.25 >= 200:
            print("   ✅ 可以达到200条目标!")
        else:
            print("   ⚠️ 需要进一步优化策略")

def test_ai_keywords():
    """测试AI关键词的有效性"""
    print("\n🔍 测试AI关键词搜索效果")
    print("-" * 40)
    
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    
    if not GITHUB_TOKEN:
        print("❌ 未设置GITHUB_TOKEN")
        return
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = "https://api.github.com/search/repositories"
    
    # 测试不同关键词的效果
    keywords = [
        "LLM", "transformer", "GPT", "machine-learning", 
        "deep-learning", "computer-vision", "diffusion",
        "pytorch", "tensorflow", "AI", "artificial-intelligence"
    ]
    
    for keyword in keywords:
        try:
            # 搜索最近90天，20+星标
            query = f"{keyword} stars:>20 created:2025-06-08..2025-09-05 is:public archived:false"
            
            params = {
                "q": query,
                "sort": "stars", 
                "order": "desc",
                "per_page": 5
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            total_count = data.get("total_count", 0)
            
            print(f"{keyword:20} : {total_count:4d} 个项目")
            
        except Exception as e:
            print(f"{keyword:20} : 搜索失败 - {e}")

if __name__ == "__main__":
    quick_search_test()
    test_ai_keywords()
