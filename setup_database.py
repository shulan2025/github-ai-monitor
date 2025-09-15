#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
功能: 创建 Cloudflare D1 数据库表
"""

import os
import sys
from cloudflare import Cloudflare
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_database_table():
    """创建数据库表"""
    print("🚀 开始初始化数据库...")
    
    # 检查必要的环境变量
    required_vars = [
        'CLOUDFLARE_ACCOUNT_ID',
        'CLOUDFLARE_API_TOKEN', 
        'D1_DATABASE_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请检查 .env 文件配置")
        return False
    
    try:
        # 初始化 Cloudflare 客户端
        cf = Cloudflare(api_token=os.getenv('CLOUDFLARE_API_TOKEN'))
        
        # 读取 SQL 文件
        sql_file = 'create_table.sql'
        if not os.path.exists(sql_file):
            print(f"❌ SQL 文件不存在: {sql_file}")
            return False
            
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📝 执行 SQL 创建表...")
        
        # 执行 SQL
        response = cf.d1.database.query(
            database_id=os.getenv('D1_DATABASE_ID'),
            account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
            sql=sql_content
        )
        
        if response.success:
            print("✅ 数据库表创建成功!")
            print("📊 表名: github_ai_post_attr")
            print("📋 字段数量: 25")
            return True
        else:
            print(f"❌ 数据库表创建失败: {response.errors}")
            return False
            
    except Exception as e:
        print(f"❌ 初始化过程发生错误: {e}")
        return False

def verify_table_structure():
    """验证表结构"""
    print("\n🔍 验证表结构...")
    
    try:
        cf = Cloudflare(api_token=os.getenv('CLOUDFLARE_API_TOKEN'))
        
        # 查询表结构
        sql = "PRAGMA table_info(github_ai_post_attr);"
        response = cf.d1.database.query(
            database_id=os.getenv('D1_DATABASE_ID'),
            account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
            sql=sql
        )
        
        if response.success:
            results = response.result[0].results
            print(f"✅ 表结构验证成功，共 {len(results)} 个字段")
            
            # 显示字段信息
            print("\n📋 表字段列表:")
            for i, field in enumerate(results, 1):
                print(f"  {i:2d}. {field['name']:<20} {field['type']:<10} {'NOT NULL' if field['notnull'] else 'NULL'}")
            
            return True
        else:
            print(f"❌ 表结构验证失败: {response.errors}")
            return False
            
    except Exception as e:
        print(f"❌ 验证过程发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🗄️  GitHub AI Monitor 数据库初始化")
    print("=" * 60)
    
    # 创建表
    if not create_database_table():
        sys.exit(1)
    
    # 验证表结构
    if not verify_table_structure():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 数据库初始化完成!")
    print("=" * 60)
    print("📝 下一步:")
    print("  1. 运行 python3 test_config.py 测试配置")
    print("  2. 运行 python3 optimized_fast_collector.py 开始采集")
    print("  3. 运行 python3 simple_db_check.py 检查数据")

if __name__ == "__main__":
    main()
