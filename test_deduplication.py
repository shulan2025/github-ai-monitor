#!/usr/bin/env python3
"""
测试数据库去重机制
验证每天更新是否会产生重复数据
"""

import os
import requests
from datetime import datetime
from cloudflare import Cloudflare
from dotenv import load_dotenv

load_dotenv()

# 配置
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID")

cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

def test_duplicate_handling():
    """测试重复数据处理机制"""
    
    print("🧪 测试数据库去重机制")
    print("=" * 50)
    
    # 1. 查看当前数据库状态
    print("1. 📊 检查当前数据库状态...")
    
    try:
        # 查询总记录数
        count_sql = "SELECT COUNT(*) as total FROM repos"
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=count_sql
        )
        
        if response.success and response.result:
            total_count = response.result[0]["results"][0]["total"]
            print(f"   当前数据库总记录数: {total_count}")
        
        # 查询今天的记录数
        today_sql = "SELECT COUNT(*) as today_count FROM repos WHERE DATE(sync_time) = DATE('now')"
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=today_sql
        )
        
        if response.success and response.result:
            today_count = response.result[0]["results"][0]["today_count"]
            print(f"   今天同步的记录数: {today_count}")
            
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
        return
    
    # 2. 测试重复ID处理
    print("\n2. 🔄 测试重复ID处理机制...")
    
    # 模拟插入一个重复的记录
    test_repo_id = "123456789"  # 使用一个测试ID
    
    # 第一次插入
    insert_sql = """
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
    
    test_params_1 = [
        test_repo_id, "test-repo", "testowner", 100, 20,
        "First version of test repo", "https://github.com/testowner/test-repo",
        "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z",
        "测试项目", "Test", "test-repo - 第一版测试", 25
    ]
    
    try:
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=insert_sql,
            params=test_params_1
        )
        print("   ✅ 第一次插入测试记录成功")
        
        # 查询记录数
        count_after_first = check_record_count(test_repo_id)
        print(f"   📊 插入后记录数: {count_after_first}")
        
    except Exception as e:
        print(f"   ❌ 第一次插入失败: {e}")
        return
    
    # 第二次插入 (模拟更新)
    test_params_2 = [
        test_repo_id, "test-repo", "testowner", 150, 30,  # 更新了stars和forks
        "Updated version of test repo", "https://github.com/testowner/test-repo",
        "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z",  # 更新了updated_at
        "测试项目-更新版", "Test, Updated", "test-repo - 更新版测试", 30  # 更新了其他字段
    ]
    
    try:
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=insert_sql,
            params=test_params_2
        )
        print("   ✅ 第二次插入(更新)测试记录成功")
        
        # 查询记录数
        count_after_second = check_record_count(test_repo_id)
        print(f"   📊 更新后记录数: {count_after_second}")
        
        if count_after_first == count_after_second:
            print("   ✅ 去重机制正常工作 - 没有产生重复记录")
        else:
            print("   ❌ 去重机制失效 - 产生了重复记录")
            
    except Exception as e:
        print(f"   ❌ 第二次插入失败: {e}")
        return
    
    # 3. 验证数据是否正确更新
    print("\n3. 🔍 验证数据更新效果...")
    
    try:
        verify_sql = "SELECT * FROM repos WHERE id = ?"
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=verify_sql,
            params=[test_repo_id]
        )
        
        if response.success and response.result:
            record = response.result[0]["results"][0]
            print(f"   📊 最终记录状态:")
            print(f"      ID: {record.get('id')}")
            print(f"      Stars: {record.get('stars')} (应该是150)")
            print(f"      Forks: {record.get('forks')} (应该是30)")
            print(f"      Category: {record.get('category')} (应该是更新版)")
            print(f"      Summary: {record.get('summary')}")
            
            # 验证是否正确更新
            if (record.get('stars') == 150 and 
                record.get('forks') == 30 and 
                "更新版" in str(record.get('category', ''))):
                print("   ✅ 数据更新机制正常工作")
            else:
                print("   ⚠️ 数据更新可能有问题")
                
    except Exception as e:
        print(f"   ❌ 验证查询失败: {e}")
    
    # 4. 清理测试数据
    print("\n4. 🧹 清理测试数据...")
    
    try:
        delete_sql = "DELETE FROM repos WHERE id = ?"
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=delete_sql,
            params=[test_repo_id]
        )
        print("   ✅ 测试数据清理完成")
        
    except Exception as e:
        print(f"   ❌ 清理失败: {e}")

def check_record_count(repo_id):
    """检查特定ID的记录数"""
    try:
        count_sql = "SELECT COUNT(*) as count FROM repos WHERE id = ?"
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=count_sql,
            params=[repo_id]
        )
        
        if response.success and response.result:
            return response.result[0]["results"][0]["count"]
        return 0
        
    except Exception as e:
        print(f"   ❌ 记录数查询失败: {e}")
        return 0

def analyze_deduplication_strategy():
    """分析去重策略"""
    
    print("\n" + "=" * 50)
    print("📋 去重机制分析")
    print("=" * 50)
    
    print("""
🎯 当前去重策略:

1. 🔑 主键机制:
   - 使用 GitHub 仓库 ID 作为主键
   - 每个仓库有唯一的数字ID，绝对不会重复
   
2. 🔄 冲突处理:
   - 使用 'ON CONFLICT(id) DO UPDATE SET' 语句
   - 当发现相同ID时，更新而不是插入新记录
   
3. 📊 更新字段:
   - stars: 更新最新星标数
   - updated_at: 更新最新推送时间
   - category: 更新最新分类结果
   - tags: 更新最新技术标签
   - summary: 更新最新摘要
   - relevance_score: 更新最新相关性评分
   - sync_time: 自动更新为当前时间

4. ✅ 保证唯一性:
   - 每个GitHub项目只会有一条记录
   - 每次运行只会更新现有记录，不会产生重复
   
5. 📈 数据价值:
   - 保持历史连续性
   - 追踪项目发展趋势
   - 实时反映项目最新状态
""")

def show_daily_update_simulation():
    """模拟每日更新效果"""
    
    print("\n" + "=" * 50)
    print("📅 每日更新模拟")
    print("=" * 50)
    
    print("""
🌅 第一天运行:
├── 收集到 862 个项目
├── 全部为新记录，直接插入
└── 数据库总记录: 862 条

🌅 第二天运行:
├── 再次收集到 500 个项目
├── 其中 300 个是重复项目(已存在)
├── 200 个是新发现的项目
├── 重复项目: 更新 stars、category 等字段
├── 新项目: 插入新记录
└── 数据库总记录: 862 + 200 = 1062 条

🌅 第三天运行:
├── 收集到 600 个项目
├── 其中 400 个是重复项目
├── 200 个是新项目  
├── 重复项目: 继续更新最新信息
├── 新项目: 插入新记录
└── 数据库总记录: 1062 + 200 = 1262 条

📊 总结:
✅ 不会产生重复记录
✅ 现有项目持续更新最新信息
✅ 新发现项目正常添加
✅ 数据库大小稳定增长
✅ 保持数据的时效性和准确性
""")

if __name__ == "__main__":
    test_duplicate_handling()
    analyze_deduplication_strategy()
    show_daily_update_simulation()
