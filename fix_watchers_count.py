#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复watchers_count字段脚本
功能: 为现有数据获取真正的subscribers_count
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict
from cloudflare import Cloudflare
from config_v2 import Config, APIConfig
from enhanced_data_processor import EnhancedDataProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WatchersCountFixer:
    """修复watchers_count字段"""
    
    def __init__(self):
        self.config = Config()
        self.cf = Cloudflare(api_token=self.config.CLOUDFLARE_API_TOKEN)
        self.session = None
        self.logger = logging.getLogger('watchers_fixer')
        
    async def initialize_session(self):
        """初始化HTTP会话"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"token {self.config.GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_real_watchers_count(self, repo_full_name: str) -> int:
        """获取真正的watchers_count (subscribers_count)"""
        try:
            await self.initialize_session()
            
            # 调用GitHub API获取仓库详细信息
            url = f"{APIConfig.GITHUB_API_BASE}/repos/{repo_full_name}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    subscribers_count = data.get("subscribers_count", 0)
                    self.logger.info(f"获取真实watchers_count: {repo_full_name} -> {subscribers_count}")
                    return subscribers_count
                else:
                    self.logger.warning(f"获取仓库详情失败: {repo_full_name} - {response.status}")
                    return 0
                    
        except Exception as e:
            self.logger.error(f"获取watchers_count异常: {repo_full_name} | {e}")
            return 0
    
    async def get_repos_to_fix(self, limit: int = 100) -> List[Dict]:
        """获取需要修复的仓库列表"""
        try:
            # 查询数据库中watchers_count等于stargazers_count的记录
            sql = """
            SELECT id, full_name, stargazers_count, watchers_count 
            FROM github_ai_post_attr 
            WHERE watchers_count = stargazers_count 
            ORDER BY stargazers_count DESC 
            LIMIT ?
            """
            
            response = self.cf.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=sql,
                params=[limit]
            )
            
            if response.success:
                results = response.result[0].results
                repos = []
                for result in results:
                    repos.append({
                        'id': result['id'],
                        'full_name': result['full_name'],
                        'stargazers_count': result['stargazers_count'],
                        'watchers_count': result['watchers_count']
                    })
                return repos
            else:
                self.logger.error(f"查询数据库失败: {response.errors}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取仓库列表失败: {e}")
            return []
    
    async def update_watchers_count(self, repo_id: str, new_watchers_count: int) -> bool:
        """更新数据库中的watchers_count"""
        try:
            sql = """
            UPDATE github_ai_post_attr 
            SET watchers_count = ?, collection_time = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            
            response = self.cf.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=sql,
                params=[new_watchers_count, repo_id]
            )
            
            if response.success:
                self.logger.info(f"更新成功: {repo_id} -> watchers_count: {new_watchers_count}")
                return True
            else:
                self.logger.error(f"更新失败: {repo_id} | {response.errors}")
                return False
                
        except Exception as e:
            self.logger.error(f"更新异常: {repo_id} | {e}")
            return False
    
    async def fix_watchers_count_batch(self, batch_size: int = 50):
        """批量修复watchers_count"""
        self.logger.info(f"开始批量修复watchers_count，批次大小: {batch_size}")
        
        try:
            # 获取需要修复的仓库
            repos = await self.get_repos_to_fix(batch_size)
            self.logger.info(f"找到 {len(repos)} 个需要修复的仓库")
            
            if not repos:
                self.logger.info("没有需要修复的仓库")
                return
            
            # 并发处理，但限制并发数
            semaphore = asyncio.Semaphore(5)  # 最多5个并发请求
            
            async def fix_single_repo(repo):
                async with semaphore:
                    repo_full_name = repo['full_name']
                    repo_id = repo['id']
                    current_watchers = repo['watchers_count']
                    stars = repo['stargazers_count']
                    
                    # 获取真实的watchers_count
                    real_watchers = await self.get_real_watchers_count(repo_full_name)
                    
                    if real_watchers > 0 and real_watchers != current_watchers:
                        # 更新数据库
                        success = await self.update_watchers_count(repo_id, real_watchers)
                        if success:
                            self.logger.info(f"✅ 修复成功: {repo_full_name} | {current_watchers} -> {real_watchers} (stars: {stars})")
                        else:
                            self.logger.error(f"❌ 修复失败: {repo_full_name}")
                    else:
                        self.logger.info(f"⏭️ 跳过: {repo_full_name} | watchers: {real_watchers} (无变化)")
                    
                    # 避免API限制
                    await asyncio.sleep(0.5)
            
            # 创建所有任务
            tasks = [fix_single_repo(repo) for repo in repos]
            
            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
            self.logger.info("批量修复完成")
            
        except Exception as e:
            self.logger.error(f"批量修复异常: {e}")
        finally:
            await self.close_session()
    
    async def get_fix_statistics(self):
        """获取修复统计信息"""
        try:
            # 统计需要修复的记录数
            sql_fix_needed = """
            SELECT COUNT(*) as count 
            FROM github_ai_post_attr 
            WHERE watchers_count = stargazers_count
            """
            
            response = self.cf.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=sql_fix_needed
            )
            
            fix_needed = 0
            if response.success:
                results = response.result[0].results
                if results:
                    fix_needed = results[0]['count']
            
            # 统计已修复的记录数
            sql_fixed = """
            SELECT COUNT(*) as count 
            FROM github_ai_post_attr 
            WHERE watchers_count != stargazers_count
            """
            
            response = self.cf.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=sql_fixed
            )
            
            fixed = 0
            if response.success:
                results = response.result[0].results
                if results:
                    fixed = results[0]['count']
            
            # 统计总记录数
            sql_total = "SELECT COUNT(*) as count FROM github_ai_post_attr"
            
            response = self.cf.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=sql_total
            )
            
            total = 0
            if response.success:
                results = response.result[0].results
                if results:
                    total = results[0]['count']
            
            self.logger.info("📊 修复统计信息:")
            self.logger.info(f"   总记录数: {total}")
            self.logger.info(f"   已修复: {fixed}")
            self.logger.info(f"   需要修复: {fix_needed}")
            self.logger.info(f"   修复进度: {fixed}/{total} ({fixed/total*100:.1f}%)")
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")

async def main():
    """主函数"""
    fixer = WatchersCountFixer()
    
    try:
        # 显示当前统计信息
        await fixer.get_fix_statistics()
        
        # 询问用户是否继续
        print("\n是否开始修复watchers_count字段？(y/n): ", end="")
        # 在脚本中自动选择y
        choice = "y"
        
        if choice.lower() == 'y':
            # 批量修复 - 增加批次大小以加快速度
            await fixer.fix_watchers_count_batch(batch_size=100)
            
            # 显示修复后的统计信息
            print("\n修复完成后的统计信息:")
            await fixer.get_fix_statistics()
        else:
            print("取消修复操作")
            
    except Exception as e:
        print(f"主程序异常: {e}")
    finally:
        await fixer.close_session()

if __name__ == "__main__":
    asyncio.run(main())
