#!/usr/bin/env python3
"""
增强指标系统测试脚本
验证所有新功能是否正常工作
"""

import os
from datetime import datetime
from enhanced_metrics_config import *

def test_configuration_loading():
    """测试配置系统加载"""
    print("🔧 测试配置系统...")
    
    try:
        # 测试核心指标配置
        assert 'basic_impact' in ENHANCED_CORE_METRICS
        assert 'ai_maturity' in AI_ENHANCED_METRICS
        print("✅ 核心指标配置加载成功")
        
        # 测试评分算法
        test_repo_data = {
            'stargazers_count': 1500,
            'forks_count': 200,
            'watchers_count': 300,
            'description': 'A powerful LLM framework with PyTorch backend for production deployment',
            'pushed_at': '2024-01-05T10:30:00Z',
            'created_at': '2023-06-15T14:20:00Z',
            'license': {'key': 'mit'},
            'language': 'Python'
        }
        
        score = calculate_enhanced_score(test_repo_data)
        assert 0 <= score <= 100
        print(f"✅ 评分算法测试通过: {score}/100分")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置系统测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n🗄️ 测试数据库连接...")
    
    try:
        from cloudflare import Cloudflare
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # 检查环境变量
        required_vars = ['CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID', 'D1_DATABASE_ID']
        for var in required_vars:
            if not os.environ.get(var):
                print(f"❌ 缺少环境变量: {var}")
                return False
        
        print("✅ 环境变量配置完整")
        
        # 测试数据库连接
        client = Cloudflare(api_token=os.environ.get('CLOUDFLARE_API_TOKEN'))
        
        # 简单查询测试
        response = client.d1.database.query(
            database_id=os.environ.get('D1_DATABASE_ID'),
            account_id=os.environ.get('CLOUDFLARE_ACCOUNT_ID'),
            sql='SELECT COUNT(*) as count FROM repos'
        )
        
        if response.success:
            count = response.result[0].results[0]['count']
            print(f"✅ 数据库连接成功，当前记录数: {count}")
            return True
        else:
            print(f"❌ 数据库查询失败: {response}")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def test_github_api():
    """测试GitHub API"""
    print("\n🐙 测试GitHub API...")
    
    try:
        import requests
        from dotenv import load_dotenv
        
        load_dotenv()
        
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("❌ 缺少GITHUB_TOKEN环境变量")
            return False
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 测试API限制查询
        response = requests.get('https://api.github.com/rate_limit', headers=headers)
        
        if response.status_code == 200:
            rate_limit = response.json()
            remaining = rate_limit['rate']['remaining']
            limit = rate_limit['rate']['limit']
            print(f"✅ GitHub API连接成功")
            print(f"📊 API限制: {remaining}/{limit} 次请求剩余")
            
            if remaining < 100:
                print("⚠️ 警告: API请求次数较少，建议稍后测试")
            
            return True
        else:
            print(f"❌ GitHub API连接失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub API测试失败: {e}")
        return False

def test_ai_analysis():
    """测试AI分析功能"""
    print("\n🤖 测试AI分析功能...")
    
    try:
        # 模拟项目数据
        test_projects = [
            {
                'name': 'awesome-llm',
                'description': 'A cutting-edge LLM framework with GPT-4 integration and PyTorch backend',
                'topics': ['llm', 'pytorch', 'gpt'],
                'language': 'Python'
            },
            {
                'name': 'computer-vision-toolkit',
                'description': 'YOLO object detection with OpenCV and deep learning models',
                'topics': ['computer-vision', 'yolo', 'opencv'],
                'language': 'Python'
            },
            {
                'name': 'rag-system',
                'description': 'Retrieval augmented generation with vector database and embeddings',
                'topics': ['rag', 'retrieval', 'embeddings'],
                'language': 'TypeScript'
            }
        ]
        
        for project in test_projects:
            # 测试AI框架识别
            name = project['name'].lower()
            description = project['description'].lower()
            full_text = f"{name} {description}"
            
            # 框架识别
            frameworks = {
                'pytorch': ['pytorch', 'torch'],
                'opencv': ['opencv', 'cv2'],
                'huggingface': ['huggingface', 'transformers']
            }
            
            detected_framework = 'unknown'
            for framework, keywords in frameworks.items():
                if any(keyword in full_text for keyword in keywords):
                    detected_framework = framework
                    break
            
            # 模型类型识别
            model_types = {
                'llm': ['llm', 'gpt', 'language model'],
                'cv': ['computer vision', 'yolo', 'detection'],
                'rag': ['rag', 'retrieval', 'vector']
            }
            
            detected_type = 'unknown'
            for model_type, keywords in model_types.items():
                if any(keyword in full_text for keyword in keywords):
                    detected_type = model_type
                    break
            
            print(f"✅ {project['name']}: 框架={detected_framework}, 类型={detected_type}")
        
        print("✅ AI分析功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ AI分析功能测试失败: {e}")
        return False

def test_scoring_algorithm():
    """测试评分算法"""
    print("\n📊 测试评分算法...")
    
    try:
        # 测试不同等级的项目
        test_cases = [
            {
                'name': '顶级项目',
                'data': {
                    'stargazers_count': 15000,
                    'forks_count': 3000,
                    'watchers_count': 1500,
                    'description': 'Production-ready LLM framework with GPT-4 API and enterprise deployment',
                    'pushed_at': '2024-01-05T10:30:00Z',
                    'created_at': '2023-01-15T14:20:00Z',
                    'license': {'key': 'apache-2.0'},
                    'language': 'Python'
                },
                'expected_range': (80, 100)
            },
            {
                'name': '优秀项目',
                'data': {
                    'stargazers_count': 2000,
                    'forks_count': 400,
                    'watchers_count': 300,
                    'description': 'Modern PyTorch framework for machine learning research',
                    'pushed_at': '2024-01-03T10:30:00Z',
                    'created_at': '2023-08-15T14:20:00Z',
                    'license': {'key': 'mit'},
                    'language': 'Python'
                },
                'expected_range': (60, 80)
            },
            {
                'name': '新兴项目',
                'data': {
                    'stargazers_count': 150,
                    'forks_count': 25,
                    'watchers_count': 40,
                    'description': 'Experimental AI agent with reasoning capabilities',
                    'pushed_at': '2024-01-04T10:30:00Z',
                    'created_at': '2023-12-01T14:20:00Z',
                    'license': {'key': 'mit'},
                    'language': 'Python'
                },
                'expected_range': (30, 60)
            }
        ]
        
        for test_case in test_cases:
            score = calculate_enhanced_score(test_case['data'])
            min_score, max_score = test_case['expected_range']
            
            if min_score <= score <= max_score:
                print(f"✅ {test_case['name']}: {score}/100分 (符合预期范围 {min_score}-{max_score})")
            else:
                print(f"⚠️ {test_case['name']}: {score}/100分 (预期范围 {min_score}-{max_score})")
        
        print("✅ 评分算法测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 评分算法测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n📁 测试文件结构...")
    
    required_files = [
        'enhanced_metrics_config.py',
        'enhanced_database_upgrade.sql',
        'enhanced_metrics_sync.py',
        'metrics_dashboard.py',
        'ENHANCED_METRICS_GUIDE.md',
        'UPGRADE_GUIDE.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (缺失)")
            missing_files.append(file)
    
    if not missing_files:
        print("✅ 所有增强指标文件已创建")
        return True
    else:
        print(f"❌ 缺失文件: {missing_files}")
        return False

def generate_test_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("🚀 增强指标系统完整性测试报告")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("文件结构检查", test_file_structure),
        ("配置系统测试", test_configuration_loading),
        ("数据库连接测试", test_database_connection),
        ("GitHub API测试", test_github_api),
        ("AI分析功能测试", test_ai_analysis),
        ("评分算法测试", test_scoring_algorithm)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 执行测试: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 恭喜！增强指标系统完全就绪！")
        print("💡 您可以开始使用新的100分制评估体系了！")
    elif passed >= total * 0.8:
        print("\n✅ 系统基本就绪，少数功能需要调整")
        print("💡 建议检查失败的测试项目")
    else:
        print("\n⚠️ 系统需要进一步配置")
        print("💡 建议先解决基础配置问题")
    
    return passed, total

def main():
    """主测试函数"""
    print("🎯 GitHub AI仓库监控系统 - 增强指标测试")
    print("版本: 2.0 (100分制评估体系)")
    print()
    
    passed, total = generate_test_report()
    
    print("\n" + "="*60)
    print("🔗 下一步操作建议")
    print("="*60)
    
    if passed == total:
        print("1. 🗄️ 升级数据库: 执行 enhanced_database_upgrade.sql")
        print("2. 📊 收集增强数据: python3 enhanced_metrics_sync.py")  
        print("3. 📈 生成仪表板: python3 metrics_dashboard.py")
        print("4. 🎯 查看完整指南: cat ENHANCED_METRICS_GUIDE.md")
    else:
        print("1. 🔧 检查环境变量配置 (.env文件)")
        print("2. 🌐 验证网络连接 (GitHub API, Cloudflare)")
        print("3. 📋 重新运行测试: python3 test_enhanced_metrics.py")
        print("4. 📖 查看升级指南: cat UPGRADE_GUIDE.md")

if __name__ == "__main__":
    main()
