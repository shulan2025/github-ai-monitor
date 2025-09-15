#!/usr/bin/env python3
"""
优化版高频采集器 - 解决3大核心问题
========================================

修复内容:
1. ✅ 修复日期解析错误 (deduplication_manager.py已修复)
2. ✅ 简化watchers_count处理 (暂时使用搜索API数据)
3. ✅ 优化采集速度 (减少额外API调用)

Author: Claude
Date: 2025-09-12
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import aiohttp
from tqdm import tqdm

# 导入项目模块
from config_v2 import Config
from enhanced_keywords_config import SEARCH_ROUNDS_CONFIG
from enhanced_data_processor_v2 import EnhancedDataProcessorV2
from deduplication_manager import DeduplicationManager
from monitoring_system import CollectionMetrics, MonitoringSystem
from email_notifier import EmailNotifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class OptimizedHighFrequencyCollector:
    """优化版高频采集器"""
    
    def __init__(self):
        self.config = Config()
        self.data_processor = EnhancedDataProcessorV2()
        self.dedup_manager = DeduplicationManager(
            cloudflare_client=None,  # 将在初始化时设置
            config=self.config
        )
        self.monitoring = MonitoringSystem()
        self.email_notifier = EmailNotifier()
        self.session = None
        self.logger = logging.getLogger('optimized_collector')
        
        # 性能配置
        self.BATCH_SIZE = 50  # 批量处理大小
        self.MAX_CONCURRENT = 5  # 最大并发数
        
    async def initialize_system(self):
        """初始化系统"""
        self.logger.info("🚀 初始化优化版采集系统...")
        
        # 初始化HTTP会话
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"token {self.config.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # 初始化去重管理器的Cloudflare客户端
        from cloudflare import Cloudflare
        cloudflare_client = Cloudflare(api_token=self.config.CLOUDFLARE_API_TOKEN)
        self.dedup_manager.cloudflare_client = cloudflare_client
        
        self.logger.info("✅ 系统初始化完成")
        
    async def search_repositories(self) -> List[Dict[str, Any]]:
        """搜索仓库 - 优化版"""
        all_repos = []
        
        self.logger.info("🔍 开始执行多轮搜索策略")
        
        for config in SEARCH_ROUNDS_CONFIG:
            round_name = config["name"]
            self.logger.info(f"🚀 执行 {round_name}")
            
            keywords = config["keywords"][:3]  # 限制关键词数量以提升速度
            target_count = min(config.get("expected_results", 300), 300)  # 限制单轮数量
            
            round_repos = await self._search_round(keywords, target_count)
            all_repos.extend(round_repos)
            
            self.logger.info(f"✅ {round_name} 完成: {len(round_repos)}个仓库")
            
            # 避免API限制
            await asyncio.sleep(1)
        
        # 去重
        unique_repos = {}
        for repo in all_repos:
            repo_id = repo.get('id')
            if repo_id and repo_id not in unique_repos:
                unique_repos[repo_id] = repo
        
        final_repos = list(unique_repos.values())
        self.logger.info(f"🏁 搜索完成: 共 {len(final_repos)} 个去重后的仓库")
        
        # 如果搜索结果太少，使用备用搜索策略
        if len(final_repos) < 50:
            self.logger.warning(f"⚠️ 搜索结果太少({len(final_repos)}个)，启用备用搜索策略")
            backup_repos = await self._backup_search_strategy()
            final_repos.extend(backup_repos)
            self.logger.info(f"🔄 备用搜索获得 {len(backup_repos)} 个仓库，总计 {len(final_repos)} 个")
        
        return final_repos
    
    async def _search_round(self, keywords: List[str], target_count: int) -> List[Dict[str, Any]]:
        """执行单轮搜索 - 优化为发现新仓库"""
        repos = []
        per_keyword = max(1, target_count // len(keywords))
        
        for keyword in keywords:
            try:
                # 动态时间过滤器 - 分层搜索策略
                from datetime import datetime, timedelta
                # 第一层：搜索最近30天有更新的仓库
                recent_updated_filter = "updated:>" + (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                # 第二层：搜索最近90天有更新的仓库
                extended_updated_filter = "updated:>" + (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                # 第三层：搜索最近1年有更新的仓库
                fallback_updated_filter = "updated:>" + (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                
                # 优先搜索最近30天有更新的仓库，降低星标要求
                min_stars = max(10, self.config.MIN_STARS // 2)  # 降低星标要求
                query = f"{keyword} {recent_updated_filter} stars:>={min_stars}"
                
                params = {
                    "q": query,
                    "sort": "updated",  # 按更新时间排序，优先最近更新的仓库
                    "order": "desc",
                    "per_page": min(100, per_keyword)
                }
                
                from config_v2 import APIConfig
                async with self.session.get(
                    APIConfig.GITHUB_SEARCH_ENDPOINT,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        repos.extend(items)
                        
                        # 分层搜索策略：如果结果不足，逐步放宽条件
                        if len(items) < per_keyword * 0.3:  # 如果结果少于预期的30%
                            self.logger.info(f"🔍 {keyword} 最近30天结果不足({len(items)}个)，搜索最近90天")
                            extended_query = f"{keyword} {extended_updated_filter} stars:>={min_stars}"
                            extended_params = {
                                "q": extended_query,
                                "sort": "updated",
                                "order": "desc", 
                                "per_page": min(100, per_keyword - len(items))
                            }
                            
                            async with self.session.get(
                                APIConfig.GITHUB_SEARCH_ENDPOINT,
                                params=extended_params
                            ) as extended_response:
                                if extended_response.status == 200:
                                    extended_data = await extended_response.json()
                                    extended_items = extended_data.get("items", [])
                                    repos.extend(extended_items)
                                    self.logger.info(f"✅ {keyword} 90天搜索获得 {len(extended_items)} 个仓库")
                                    
                                    # 如果90天结果仍然不足，搜索最近1年
                                    if len(items) + len(extended_items) < per_keyword * 0.5:
                                        self.logger.info(f"🔍 {keyword} 90天结果仍不足，搜索最近1年")
                                        fallback_query = f"{keyword} {fallback_updated_filter} stars:>={min_stars}"
                                        fallback_params = {
                                            "q": fallback_query,
                                            "sort": "updated",
                                            "order": "desc",
                                            "per_page": min(100, per_keyword - len(items) - len(extended_items))
                                        }
                                        
                                        async with self.session.get(
                                            APIConfig.GITHUB_SEARCH_ENDPOINT,
                                            params=fallback_params
                                        ) as fallback_response:
                                            if fallback_response.status == 200:
                                                fallback_data = await fallback_response.json()
                                                fallback_items = fallback_data.get("items", [])
                                                repos.extend(fallback_items)
                                                self.logger.info(f"✅ {keyword} 1年搜索获得 {len(fallback_items)} 个仓库")
                                    
                    elif response.status == 403:
                        self.logger.warning(f"⚠️ API限频: {keyword}")
                        await asyncio.sleep(10)
                    else:
                        self.logger.error(f"❌ API错误 {keyword}: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"❌ 搜索失败 {keyword}: {e}")
                
        return repos
    
    async def _backup_search_strategy(self) -> List[Dict[str, Any]]:
        """备用搜索策略 - 使用更宽松的条件"""
        self.logger.info("🔄 执行备用搜索策略")
        backup_repos = []
        
        # 使用更宽松的搜索条件
        backup_keywords = [
            "machine learning", "deep learning", "neural network", 
            "artificial intelligence", "AI", "ML", "pytorch", "tensorflow"
        ]
        
        for keyword in backup_keywords[:3]:  # 只使用前3个关键词
            try:
                # 使用更宽松的时间范围和星标要求
                query = f"{keyword} stars:>=10 created:>2020-01-01"
                
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 50
                }
                
                from config_v2 import APIConfig
                async with self.session.get(
                    APIConfig.GITHUB_SEARCH_ENDPOINT,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        backup_repos.extend(items)
                        self.logger.info(f"✅ 备用搜索 {keyword}: {len(items)} 个仓库")
                    elif response.status == 403:
                        self.logger.warning(f"⚠️ 备用搜索API限频: {keyword}")
                        await asyncio.sleep(5)
                    else:
                        self.logger.error(f"❌ 备用搜索API错误 {keyword}: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"❌ 备用搜索失败 {keyword}: {e}")
        
        # 去重
        unique_backup = {}
        for repo in backup_repos:
            repo_id = repo.get('id')
            if repo_id and repo_id not in unique_backup:
                unique_backup[repo_id] = repo
        
        return list(unique_backup.values())
    
    async def process_repositories(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理仓库数据 - 使用增强版处理器确保watchers_count正确"""
        self.logger.info(f"🔄 开始处理 {len(repos)} 个仓库数据 (增强版)")
        
        # 使用增强版数据处理器批量处理，确保watchers_count正确
        processed_repos = await self.data_processor.process_repositories_batch(repos, max_concurrent=10)
        
        self.logger.info(f"✅ 数据处理完成: {len(processed_repos)} 个有效仓库")
        return processed_repos
    
    async def store_repositories(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """存储仓库数据 - 批量优化"""
        self.logger.info(f"💾 开始存储 {len(repos)} 个仓库到数据库")
        
        stats = {"new": 0, "updated": 0, "skipped": 0, "total_processed": 0}
        
        # 批量处理以提升性能
        with tqdm(repos, desc="存储仓库数据", disable=False, mininterval=2.0) as pbar:
            for repo in pbar:
                try:
                    stats["total_processed"] += 1
                    
                    # 检查去重逻辑
                    should_store, reason = await self.dedup_manager.should_store_repository(repo)
                    
                    if should_store:
                        # 存储到数据库
                        success = await self.store_single_repository(repo)
                        
                        if success:
                            if "新项目" in reason:
                                stats["new"] += 1
                                self.logger.info(f"✅ 新增仓库: {repo.full_name}")
                            elif "重要更新" in reason:
                                stats["updated"] += 1
                                self.logger.info(f"🔄 更新仓库: {repo.full_name}")
                            else:
                                stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    else:
                        stats["skipped"] += 1
                        self.logger.debug(f"跳过存储: {repo.full_name} | {reason}")
                        
                except Exception as e:
                    self.logger.error(f"存储失败 {repo.full_name}: {e}")
                    stats["skipped"] += 1
                    
                pbar.update(1)
        
        self.logger.info(f"✅ 存储完成: 新增{stats['new']}, 更新{stats['updated']}, 跳过{stats['skipped']}")
        return stats
    
    async def store_single_repository(self, repo) -> bool:
        """存储单个仓库到数据库"""
        try:
            # 准备数据
            from datetime import datetime, timezone, timedelta
            beijing_tz = timezone(timedelta(hours=8))
            current_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
            
            params = [
                repo.id, repo.full_name, repo.name, repo.owner,
                repo.description or '', repo.url, repo.stargazers_count,
                repo.forks_count, repo.watchers_count, repo.created_at,
                repo.updated_at, repo.pushed_at, repo.language or '',
                ','.join(repo.topics) if repo.topics else '',  # 序列化topics
                repo.ai_category or '', 
                ','.join(repo.ai_tags) if repo.ai_tags else '',  # 序列化ai_tags
                repo.quality_score, repo.trending_score, 1,  # collection_round
                repo.last_fork_count, repo.fork_growth, repo.collection_hash or '',
                current_time  # collection_time
            ]
            
            # 执行插入/更新
            response = self.dedup_manager.cloudflare_client.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=self.dedup_manager.db_config.UPSERT_SQL,
                params=params
            )
            
            if response.success:
                return True
            else:
                self.logger.error(f"数据库存储失败: {response.errors}")
                return False
                
        except Exception as e:
            self.logger.error(f"存储异常: {e}")
            return False
    
    async def run_optimized_collection(self):
        """运行优化版采集"""
        start_time = datetime.now()
        
        try:
            await self.initialize_system()
            
            # 1. 搜索仓库
            repos = await self.search_repositories()
            
            # 2. 处理数据
            processed_repos = await self.process_repositories(repos)
            
            # 3. 存储数据
            stats = await self.store_repositories(processed_repos)
            
            # 4. 生成报告
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() / 60
            
            self.logger.info("\n" + "="*50)
            self.logger.info("✅ 最近更新仓库采集完成!")
            self.logger.info("="*50)
            self.logger.info(f"📊 总搜索数量: {len(processed_repos)}")
            self.logger.info(f"🆕 新增仓库: {stats['new']}")
            self.logger.info(f"🔄 更新仓库: {stats['updated']}")
            self.logger.info(f"⏭️ 跳过仓库: {stats['skipped']}")
            # 安全计算比率，避免除零错误
            total_processed = stats['total_processed']
            if total_processed > 0:
                new_rate = stats['new']/total_processed*100
                update_rate = stats['updated']/total_processed*100
                self.logger.info(f"📈 新增率: {new_rate:.1f}%")
                self.logger.info(f"📈 更新率: {update_rate:.1f}%")
            else:
                self.logger.info(f"📈 新增率: 0.0% (无处理数据)")
                self.logger.info(f"📈 更新率: 0.0% (无处理数据)")
            self.logger.info(f"⏱️ 采集耗时: {duration:.1f}分钟")
            self.logger.info(f"🚀 平均速度: {len(processed_repos)/duration:.1f}项/分钟")
            
            # 发送成功通知邮件
            email_stats = {
                'total': len(processed_repos),
                'new': stats['new'],
                'updated': stats['updated'],
                'skipped': stats['skipped'],
                'duration': f"{duration:.1f}分钟",
                'speed': f"{len(processed_repos)/duration:.1f}项/分钟"
            }
            self.email_notifier.send_success_notification(email_stats)
            
        except Exception as e:
            self.logger.error(f"❌ 采集过程中发生错误: {e}")
            # 发送失败通知邮件
            try:
                self.email_notifier.send_failure_notification(str(e))
            except Exception as email_error:
                self.logger.error(f"❌ 发送失败通知邮件失败: {email_error}")
            raise
        finally:
            if self.session:
                try:
                    await self.session.close()
                except Exception as close_error:
                    self.logger.error(f"❌ 关闭HTTP会话失败: {close_error}")

async def main():
    """主函数"""
    collector = OptimizedHighFrequencyCollector()
    await collector.run_optimized_collection()

if __name__ == "__main__":
    asyncio.run(main())
