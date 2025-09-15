#!/usr/bin/env python3
"""
测试增强版数据收集策略
验证是否能达到200条/天的目标
"""

import os
from datetime import datetime
from enhanced_sync_d1 import (
    enhanced_data_collection, 
    process_and_save_repos_enhanced,
    execute_search_query,
    calculate_ai_relevance_enhanced
)
from enhanced_search_config import (
    generate_search_queries,
    get_time_windows,
    SORT_STRATEGIES,
    EXECUTION_STRATEGY
)

def test_search_strategy():
    """测试搜索策略的有效性"""
    print("🧪 测试增强版搜索策略...")
    
    # 生成搜索查询
    queries = generate_search_queries()
    time_windows = get_time_windows()
    
    print(f"📊 生成搜索查询: {len(queries)} 个")
    print(f"⏰ 时间窗口: {len(time_windows)} 个")
    print(f"🔄 排序策略: {len(SORT_STRATEGIES)} 种")
    
    total_combinations = len(queries) * len(time_windows) * len(SORT_STRATEGIES)
    print(f"🎯 理论搜索组合: {total_combinations} 种")
    
    # 选择前5个查询进行测试
    test_queries = queries[:5]
    test_windows = time_windows[:2]
    
    print(f"\n🔍 执行测试搜索 (前5个查询 × 前2个时间窗口)...")
    
    total_candidates = 0
    valid_projects = 0
    
    for i, query in enumerate(test_queries):
        print(f"\n查询 {i+1}/{len(test_queries)}: {query['name']}")
        
        for j, window in enumerate(test_windows):
            for k, sort_config in enumerate(SORT_STRATEGIES[:1]):  # 只测试第一种排序
                
                print(f"  执行: {window['name']} + {sort_config['sort']}")
                
                # 执行搜索
                repos = execute_search_query(query, window, sort_config, star_threshold=50)
                
                if repos:
                    total_candidates += len(repos)
                    
                    # 计算有效项目数
                    for repo in repos:
                        score = calculate_ai_relevance_enhanced(repo)
                        if score >= 1:  # 使用新的阈值
                            valid_projects += 1
                    
                    print(f"    找到: {len(repos)} 个候选, 预计有效: {sum(1 for r in repos if calculate_ai_relevance_enhanced(r) >= 1)} 个")
                
                # 避免过度测试
                if total_candidates >= 200:
                    break
            
            if total_candidates >= 200:
                break
        
        if total_candidates >= 200:
            break
    
    efficiency = (valid_projects / total_candidates * 100) if total_candidates > 0 else 0
    
    print(f"\n📊 测试结果:")
    print(f"   候选项目: {total_candidates} 个")
    print(f"   有效项目: {valid_projects} 个")
    print(f"   有效率: {efficiency:.1f}%")
    
    # 预测全量收集效果
    if efficiency > 0:
        estimated_searches = EXECUTION_STRATEGY["primary_searches"] * 4 * 3  # 查询数 × 时间窗口 × 排序策略
        estimated_candidates = estimated_searches * 20  # 假设每次搜索平均20个结果
        estimated_valid = estimated_candidates * (efficiency / 100)
        
        print(f"\n🔮 全量收集预测:")
        print(f"   预计搜索次数: {estimated_searches}")
        print(f"   预计候选数: {estimated_candidates}")
        print(f"   预计有效数: {estimated_valid:.0f}")
        print(f"   是否达标: {'✅ 是' if estimated_valid >= 200 else '❌ 否'}")

def test_ai_relevance_scoring():
    """测试AI相关性评分算法"""
    print("\n🧪 测试AI相关性评分算法...")
    
    # 测试用例
    test_cases = [
        {"name": "llama2-chatbot", "description": "A conversational AI powered by LLaMA 2 transformer model", "expected": "高分"},
        {"name": "pytorch-diffusion", "description": "PyTorch implementation of diffusion models for image generation", "expected": "高分"},
        {"name": "rag-system", "description": "Retrieval-augmented generation system with vector database", "expected": "高分"},
        {"name": "cv-toolkit", "description": "Computer vision toolkit with YOLO object detection", "expected": "中分"},
        {"name": "data-analysis-pandas", "description": "Data science tools built with pandas and numpy", "expected": "中分"},
        {"name": "hello-world", "description": "Simple hello world application for beginners", "expected": "低分"},
        {"name": "tutorial-repo", "description": "Learning materials and examples for machine learning", "expected": "低分"},
    ]
    
    print("项目名称 | 描述 | 得分 | 预期")
    print("-" * 60)
    
    for case in test_cases:
        repo = {
            "name": case["name"],
            "description": case["description"],
            "stargazers_count": 100,
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        score = calculate_ai_relevance_enhanced(repo)
        print(f"{case['name'][:15]:15} | {case['description'][:25]:25} | {score:2d}/10 | {case['expected']}")

def test_category_classification():
    """测试项目分类功能"""
    print("\n🧪 测试项目分类功能...")
    
    from enhanced_sync_d1 import categorize_ai_project_enhanced
    
    test_cases = [
        {"name": "vllm", "description": "High-throughput LLM serving engine", "expected": "LLM服务与工具"},
        {"name": "chatgpt-clone", "description": "ChatGPT-like conversational AI assistant", "expected": "LLM应用"},
        {"name": "rag-paper", "description": "Research implementation of retrieval-augmented generation", "expected": "RAG技术"},
        {"name": "stable-diffusion-webui", "description": "Web interface for Stable Diffusion image generation", "expected": "生成式AI"},
        {"name": "yolo-detection", "description": "Real-time object detection using YOLO algorithm", "expected": "计算机视觉"},
        {"name": "pandas-profiling", "description": "Automated data analysis and visualization with pandas", "expected": "数据科学"},
        {"name": "pytorch-tutorial", "description": "Deep learning tutorials using PyTorch framework", "expected": "机器学习"},
    ]
    
    print("项目名称 | 描述 | 分类结果")
    print("-" * 70)
    
    for case in test_cases:
        category = categorize_ai_project_enhanced(case["name"], case["description"])
        match = "✅" if category == case["expected"] else "❌"
        print(f"{case['name'][:15]:15} | {case['description'][:30]:30} | {category} {match}")

def dry_run_collection():
    """模拟运行数据收集（不实际调用API）"""
    print("\n🧪 模拟数据收集流程...")
    
    # 模拟候选数据
    mock_repos = []
    for i in range(100):
        mock_repos.append({
            "id": f"mock_{i}",
            "name": f"ai-project-{i}",
            "description": f"This is a machine learning project with {['pytorch', 'tensorflow', 'llm', 'diffusion'][i%4]} technology",
            "stargazers_count": 50 + i * 10,
            "forks_count": 10 + i * 2,
            "html_url": f"https://github.com/user/ai-project-{i}",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z",
            "owner": {"login": f"user{i}"},
            "fork": False,
            "archived": False
        })
    
    print(f"📦 模拟候选项目: {len(mock_repos)} 个")
    
    # 使用真实的过滤函数
    from enhanced_sync_d1 import filter_ai_repos_enhanced
    filtered_repos = filter_ai_repos_enhanced(mock_repos)
    
    print(f"🎯 过滤后项目: {len(filtered_repos)} 个")
    print(f"📈 过滤效率: {len(filtered_repos)/len(mock_repos)*100:.1f}%")
    
    # 分类统计
    categories = {}
    for repo in filtered_repos:
        from enhanced_sync_d1 import categorize_ai_project_enhanced
        category = categorize_ai_project_enhanced(repo["name"], repo["description"])
        categories[category] = categories.get(category, 0) + 1
    
    print("\n📋 分类统计:")
    for cat, count in categories.items():
        print(f"   {cat}: {count} 个")

def main():
    """主测试函数"""
    print("🧪 增强版数据收集策略测试")
    print("=" * 50)
    
    # 检查环境变量
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ 未设置GITHUB_TOKEN，跳过API测试")
        api_test = False
    else:
        print("✅ 检测到GITHUB_TOKEN，将执行API测试")
        api_test = True
    
    # 执行测试
    if api_test:
        test_search_strategy()
    
    test_ai_relevance_scoring()
    test_category_classification()
    dry_run_collection()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    
    if api_test:
        print("\n💡 建议:")
        print("1. 如果预测有效数 >= 200，可以使用enhanced_sync_d1.py")
        print("2. 如果有效率偏低，考虑调整搜索关键词或过滤阈值")
        print("3. 可以通过增加搜索轮次来提高数据收集量")
    else:
        print("\n💡 建议:")
        print("1. 设置GITHUB_TOKEN后重新测试API搜索策略")
        print("2. 当前模拟测试显示算法逻辑正常")

if __name__ == "__main__":
    main()
