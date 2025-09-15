#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证watchers_count修复结果
"""

from cloudflare import Cloudflare
from config_v2 import Config

def verify_watchers_fix():
    """验证watchers_count修复结果"""
    print("🔍 验证watchers_count修复结果...")
    
    # 初始化Cloudflare客户端
    cf = Cloudflare(api_token=Config.CLOUDFLARE_API_TOKEN)
    
    try:
        # 查询已修复的记录（watchers_count != stargazers_count）
        sql_fixed = """
        SELECT full_name, stargazers_count, watchers_count, 
               (watchers_count * 100.0 / stargazers_count) as watchers_ratio
        FROM github_ai_post_attr 
        WHERE watchers_count != stargazers_count 
        ORDER BY stargazers_count DESC 
        LIMIT 10
        """
        
        response = cf.d1.database.query(
            database_id=Config.D1_DATABASE_ID,
            account_id=Config.CLOUDFLARE_ACCOUNT_ID,
            sql=sql_fixed
        )
        
        if response.success:
            results = response.result[0].results
            if results:
                print("✅ 已修复的记录 (watchers_count != stargazers_count):")
                print("=" * 80)
                for i, record in enumerate(results, 1):
                    repo_name = record['full_name']
                    stars = record['stargazers_count']
                    watchers = record['watchers_count']
                    ratio = record['watchers_ratio']
                    print(f"{i:2d}. {repo_name}")
                    print(f"    Stars: {stars:,} | Watchers: {watchers:,} | 比例: {ratio:.2f}%")
                    print()
            else:
                print("❌ 没有找到已修复的记录")
        else:
            print(f"❌ 查询失败: {response.errors}")
        
        # 查询仍需修复的记录
        sql_need_fix = """
        SELECT COUNT(*) as count 
        FROM github_ai_post_attr 
        WHERE watchers_count = stargazers_count
        """
        
        response = cf.d1.database.query(
            database_id=Config.D1_DATABASE_ID,
            account_id=Config.CLOUDFLARE_ACCOUNT_ID,
            sql=sql_need_fix
        )
        
        if response.success:
            results = response.result[0].results
            if results:
                need_fix_count = results[0]['count']
                print(f"📊 仍需修复的记录数: {need_fix_count}")
        
        # 查询总记录数
        sql_total = "SELECT COUNT(*) as count FROM github_ai_post_attr"
        
        response = cf.d1.database.query(
            database_id=Config.D1_DATABASE_ID,
            account_id=Config.CLOUDFLARE_ACCOUNT_ID,
            sql=sql_total
        )
        
        if response.success:
            results = response.result[0].results
            if results:
                total_count = results[0]['count']
                fixed_count = total_count - need_fix_count
                progress = (fixed_count / total_count) * 100
                print(f"📈 修复进度: {fixed_count}/{total_count} ({progress:.1f}%)")
        
    except Exception as e:
        print(f"❌ 验证过程发生错误: {e}")

if __name__ == "__main__":
    verify_watchers_fix()
