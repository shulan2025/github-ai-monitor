#!/usr/bin/env python3
"""
简单检查数据库去重效果
"""

import os
from cloudflare import Cloudflare
from dotenv import load_dotenv

load_dotenv()

CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID")

cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

def simple_check():
    """简单检查重复数据"""
    print("🔍 检查数据库重复情况")
    print("=" * 40)
    
    try:
        # 检查是否有重复ID
        sql = """
        SELECT id, COUNT(*) as count 
        FROM repos 
        GROUP BY id 
        HAVING COUNT(*) > 1
        """
        
        response = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=sql
        )
        
        print("✅ 查询执行成功")
        print(f"📊 查询结果: {response}")
        
        # 简单的总数查询
        count_sql = "SELECT COUNT(*) FROM repos"
        response2 = cloudflare_client.d1.database.query(
            database_id=D1_DATABASE_ID,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            sql=count_sql
        )
        
        print(f"📊 总数查询结果: {response2}")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    simple_check()
