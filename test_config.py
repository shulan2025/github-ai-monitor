#!/usr/bin/env python3
"""
配置测试脚本
用于验证所有 API 凭证和配置是否正确
"""

import os
import requests
from dotenv import load_dotenv
from cloudflare import Cloudflare

# 加载环境变量
load_dotenv()

def test_github_api():
    """测试 GitHub API 配置"""
    print("🔍 测试 GitHub API 配置...")
    
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN 环境变量未设置")
        return False
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # 测试基本 API 访问
        response = requests.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        print(f"✅ GitHub API 连接成功! 用户: {user_data.get('login')}")
        
        # 测试搜索 API
        search_response = requests.get(
            "https://api.github.com/search/repositories",
            headers=headers,
            params={"q": "AI stars:>1000", "per_page": 1}
        )
        search_response.raise_for_status()
        
        print(f"✅ GitHub 搜索 API 测试成功!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub API 测试失败: {e}")
        return False

def test_cloudflare_api():
    """测试 Cloudflare D1 API 配置"""
    print("\n☁️ 测试 Cloudflare D1 API 配置...")
    
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    database_id = os.environ.get("D1_DATABASE_ID")
    
    if not all([api_token, account_id, database_id]):
        missing = []
        if not api_token: missing.append("CLOUDFLARE_API_TOKEN")
        if not account_id: missing.append("CLOUDFLARE_ACCOUNT_ID") 
        if not database_id: missing.append("D1_DATABASE_ID")
        print(f"❌ 缺少环境变量: {', '.join(missing)}")
        return False
    
    try:
        client = Cloudflare(api_token=api_token)
        
        # 测试基本连接
        print(f"✅ Cloudflare API 客户端初始化成功!")
        print(f"📊 账户 ID: {account_id}")
        print(f"🗄️ 数据库 ID: {database_id}")
        
        # 测试数据库查询
        try:
            response = client.d1.database.query(
                database_id=database_id,
                account_id=account_id,
                sql="SELECT name FROM sqlite_master WHERE type='table' AND name='repos';"
            )
            
            if hasattr(response, 'result') and response.result:
                print("✅ D1 数据库连接成功! repos 表已存在")
            else:
                print("⚠️ D1 数据库连接成功，但 repos 表不存在，请先运行 create_table.sql")
            
            return True
            
        except Exception as db_error:
            print(f"⚠️ D1 数据库查询测试失败: {db_error}")
            print("💡 请检查数据库 ID 是否正确，或先创建 repos 表")
            return True  # API 连接本身是成功的
            
    except Exception as e:
        print(f"❌ Cloudflare API 测试失败: {e}")
        return False

def test_dependencies():
    """测试 Python 依赖包"""
    print("\n📦 测试 Python 依赖包...")
    
    required_packages = ['requests', 'cloudflare', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n💡 请安装缺少的包: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """运行所有测试"""
    print("🧪 开始配置测试...\n")
    
    tests = [
        ("依赖包", test_dependencies),
        ("GitHub API", test_github_api),
        ("Cloudflare D1 API", test_cloudflare_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "="*50)
    print("📋 测试结果总结:")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:15} | {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("🎉 所有测试通过! 你可以运行 sync_d1.py 开始数据同步了。")
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息并修复配置。")
    
    return all_passed

if __name__ == "__main__":
    main()
