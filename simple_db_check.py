#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单数据库检查脚本
"""

from cloudflare import Cloudflare
from config_v2 import Config

def check_database():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")
    
    # 初始化Cloudflare客户端
    cf = Cloudflare(api_token=Config.CLOUDFLARE_API_TOKEN)
    
    try:
        # 查询总记录数
        response = cf.d1.database.query(
            database_id=Config.D1_DATABASE_ID,
            account_id=Config.CLOUDFLARE_ACCOUNT_ID,
            sql="SELECT COUNT(*) as total FROM github_ai_post_attr"
        )
        
        if response.success:
            results = response.result[0].results
            if results and len(results) > 0:
                total_count = results[0]['total']
                print(f"✅ 数据库连接正常")
                print(f"📊 总记录数: {total_count}")
                
                # 查询最近的记录
                recent_response = cf.d1.database.query(
                    database_id=Config.D1_DATABASE_ID,
                    account_id=Config.CLOUDFLARE_ACCOUNT_ID,
                    sql="SELECT full_name, stargazers_count, created_at FROM github_ai_post_attr ORDER BY collection_time DESC LIMIT 5"
                )
                
                if recent_response.success:
                    recent_results = recent_response.result[0].results
                    if recent_results:
                        print(f"📋 最近5条记录:")
                        for i, record in enumerate(recent_results, 1):
                            print(f"   {i}. {record['full_name']} - {record['stargazers_count']}⭐ - {record['created_at']}")
                    else:
                        print("📋 暂无记录")
                else:
                    print(f"❌ 查询最近记录失败: {recent_response.errors}")
            else:
                print("❌ 无法获取记录数")
        else:
            print(f"❌ 数据库查询失败: {response.errors}")
            
    except Exception as e:
        print(f"❌ 检查过程发生错误: {e}")

if __name__ == "__main__":
    check_database()
