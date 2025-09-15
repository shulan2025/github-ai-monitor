#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watchers Count 彻底修复方案 v2.0
解决GitHub API中watchers_count字段解析错误的根本问题

问题分析:
1. GitHub搜索API返回的watchers_count实际上是stargazers_count
2. 真正的watchers_count需要通过单独的API调用获取
3. 需要在新采集和修复历史数据两个层面都解决

解决方案:
1. 修改数据处理器，正确获取watchers_count
2. 创建批量修复脚本，修复所有历史数据
3. 添加验证机制，确保数据正确性
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from cloudflare import Cloudflare
from config_v2 import Config
from high_frequency_collector import RepositoryData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WatchersCountFixerV2:
    """Watchers Count 彻底修复器 v2.0"""
    
    def __init__(self):
        self.config = Config()
        self.cf = Cloudflare(api_token=self.config.CLOUDFLARE_API_TOKEN)
        self.session = None
        self.logger = logging.getLogger('watchers_fixer_v2')
        
    async def initialize_session(self):
        """初始化HTTP会话"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"token {self.config.GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "GitHub-AI-Monitor/2.0"
                }
            )
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
    
    async def get_real_watchers_count(self, repo_full_name: str) -> Optional[int]:
        """获取真正的watchers_count (subscribers_count)"""
        try:
            url = f"https://api.github.com/repos/{repo_full_name}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # 真正的watchers_count是subscribers_count
                    return data.get("subscribers_count", 0)
                elif response.status == 404:
                    self.logger.warning(f"仓库不存在: {repo_full_name}")
                    return None
                elif response.status == 403:
                    self.logger.warning(f"API限制: {repo_full_name}")
                    return None
                else:
                    self.logger.warning(f"获取watchers_count失败: {repo_full_name}, 状态码: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"获取watchers_count异常: {repo_full_name} | {e}")
            return None
    
    async def fix_watchers_count_batch(self, batch_size: int = 50, max_concurrent: int = 10):
        """批量修复watchers_count字段"""
        await self.initialize_session()
        
        try:
            # 获取需要修复的记录
            sql = """
            SELECT id, full_name, stargazers_count, watchers_count
            FROM github_ai_post_attr
            WHERE watchers_count = stargazers_count OR watchers_count = 0
            ORDER BY stargazers_count DESC
            LIMIT ?
            """
            
            response = self.cf.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=sql,
                params=[batch_size]
            )
            
            if not response.success:
                self.logger.error(f"查询失败: {response.errors}")
                return
            
            records = response.result[0].results
            if not records:
                self.logger.info("没有需要修复的记录")
                return
            
            self.logger.info(f"开始修复 {len(records)} 条记录的watchers_count字段")
            
            # 使用信号量控制并发
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def fix_single_record(record):
                async with semaphore:
                    repo_id = record['id']
                    full_name = record['full_name']
                    stargazers_count = record['stargazers_count']
                    current_watchers = record['watchers_count']
                    
                    # 获取真正的watchers_count
                    real_watchers = await self.get_real_watchers_count(full_name)
                    
                    if real_watchers is not None:
                        # 更新数据库
                        update_sql = """
                        UPDATE github_ai_post_attr
                        SET watchers_count = ?
                        WHERE id = ?
                        """
                        
                        update_response = self.cf.d1.database.query(
                            database_id=self.config.D1_DATABASE_ID,
                            account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                            sql=update_sql,
                            params=[real_watchers, repo_id]
                        )
                        
                        if update_response.success:
                            self.logger.info(f"✅ 修复成功: {full_name} | Stars: {stargazers_count} | Watchers: {current_watchers} -> {real_watchers}")
                            return True
                        else:
                            self.logger.error(f"❌ 更新失败: {full_name} | {update_response.errors}")
                            return False
                    else:
                        self.logger.warning(f"⚠️ 跳过: {full_name} | 无法获取watchers_count")
                        return False
            
            # 并发处理所有记录
            tasks = [fix_single_record(record) for record in records]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计结果
            success_count = sum(1 for r in results if r is True)
            failed_count = len(results) - success_count
            
            self.logger.info(f"修复完成: 成功 {success_count}, 失败 {failed_count}")
            
        except Exception as e:
            self.logger.error(f"批量修复异常: {e}")
        finally:
            await self.close_session()
    
    def verify_fix_results(self):
        """验证修复结果"""
        try:
            # 查询修复后的统计
            sql = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN watchers_count = stargazers_count THEN 1 END) as incorrect_watchers,
                COUNT(CASE WHEN watchers_count != stargazers_count THEN 1 END) as correct_watchers,
                COUNT(CASE WHEN watchers_count = 0 THEN 1 END) as zero_watchers
            FROM github_ai_post_attr
            """
            
            response = self.cf.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=sql
            )
            
            if response.success:
                result = response.result[0].results[0]
                total = result['total_records']
                incorrect = result['incorrect_watchers']
                correct = result['correct_watchers']
                zero = result['zero_watchers']
                
                self.logger.info("=" * 60)
                self.logger.info("📊 Watchers Count 修复结果统计")
                self.logger.info("=" * 60)
                self.logger.info(f"总记录数: {total}")
                self.logger.info(f"正确的watchers_count: {correct} ({correct/total*100:.1f}%)")
                self.logger.info(f"错误的watchers_count: {incorrect} ({incorrect/total*100:.1f}%)")
                self.logger.info(f"零值watchers_count: {zero} ({zero/total*100:.1f}%)")
                
                if incorrect == 0 and zero == 0:
                    self.logger.info("🎉 所有watchers_count字段已修复完成！")
                else:
                    self.logger.warning(f"⚠️ 仍有 {incorrect + zero} 条记录需要修复")
                
                # 显示一些修复后的示例
                example_sql = """
                SELECT full_name, stargazers_count, watchers_count,
                       (watchers_count * 100.0 / stargazers_count) as watchers_ratio
                FROM github_ai_post_attr
                WHERE watchers_count != stargazers_count AND watchers_count > 0
                ORDER BY stargazers_count DESC
                LIMIT 5
                """
                
                example_response = self.cf.d1.database.query(
                    database_id=self.config.D1_DATABASE_ID,
                    account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                    sql=example_sql
                )
                
                if example_response.success and example_response.result[0].results:
                    self.logger.info("\n📋 修复后的示例记录:")
                    for record in example_response.result[0].results:
                        self.logger.info(f"  {record['full_name']}: {record['stargazers_count']}⭐ - {record['watchers_count']}👀 (比例: {record['watchers_ratio']:.1f}%)")
                
            else:
                self.logger.error(f"验证查询失败: {response.errors}")
                
        except Exception as e:
            self.logger.error(f"验证过程异常: {e}")

async def main():
    """主函数"""
    fixer = WatchersCountFixerV2()
    
    print("🔧 Watchers Count 彻底修复方案 v2.0")
    print("=" * 50)
    
    # 1. 验证当前状态
    print("1. 验证当前状态...")
    fixer.verify_fix_results()
    
    # 2. 批量修复
    print("\n2. 开始批量修复...")
    await fixer.fix_watchers_count_batch(batch_size=100, max_concurrent=5)
    
    # 3. 验证修复结果
    print("\n3. 验证修复结果...")
    fixer.verify_fix_results()

if __name__ == "__main__":
    asyncio.run(main())
