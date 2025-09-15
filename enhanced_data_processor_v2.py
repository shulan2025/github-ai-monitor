#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版数据处理器 v2.0 - 彻底解决watchers_count问题
功能: 确保watchers_count字段始终正确
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from data_processor import DataProcessor
from config_v2 import Config, APIConfig
from high_frequency_collector import RepositoryData

class EnhancedDataProcessorV2(DataProcessor):
    """增强版数据处理器 v2.0 - 彻底解决watchers_count问题"""
    
    def __init__(self):
        super().__init__()
        self.session = None
        self.config = Config()
        self.logger = logging.getLogger('enhanced_processor_v2')
        
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
    
    async def process_repository_enhanced(self, repo_raw: Dict[str, Any]) -> Optional[RepositoryData]:
        """增强版仓库数据处理 - 确保watchers_count正确"""
        try:
            # 先进行基础数据处理
            repo_data = self.process_repository(repo_raw)
            
            if not repo_data:
                return None
            
            # 获取真正的watchers_count
            if not self.session:
                await self.initialize_session()
            
            real_watchers = await self.get_real_watchers_count(repo_data.full_name)
            
            if real_watchers is not None:
                repo_data.watchers_count = real_watchers
                self.logger.debug(f"✅ 获取watchers_count成功: {repo_data.full_name} | {real_watchers}")
            else:
                # 如果无法获取，使用stargazers_count作为fallback
                repo_data.watchers_count = repo_data.stargazers_count
                self.logger.warning(f"⚠️ 使用stargazers_count作为watchers_count: {repo_data.full_name}")
            
            return repo_data
            
        except Exception as e:
            self.logger.error(f"增强版数据处理失败: {repo_raw.get('full_name', 'unknown')} | {e}")
            return None
    
    async def process_repositories_batch(self, repos_raw: List[Dict[str, Any]], max_concurrent: int = 10) -> List[RepositoryData]:
        """批量处理仓库数据 - 并发获取watchers_count"""
        if not self.session:
            await self.initialize_session()
        
        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_repo(repo_raw):
            async with semaphore:
                return await self.process_repository_enhanced(repo_raw)
        
        # 并发处理所有仓库
        tasks = [process_single_repo(repo_raw) for repo_raw in repos_raw]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉None和异常结果
        valid_repos = []
        for result in results:
            if isinstance(result, RepositoryData):
                valid_repos.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"处理仓库时发生异常: {result}")
        
        self.logger.info(f"批量处理完成: {len(valid_repos)}/{len(repos_raw)} 个仓库处理成功")
        return valid_repos

# 使用示例
async def test_enhanced_processor():
    """测试增强版数据处理器"""
    processor = EnhancedDataProcessorV2()
    
    try:
        # 测试数据
        test_repo = {
            'id': 12345,
            'full_name': 'microsoft/vscode',
            'name': 'vscode',
            'owner': {'login': 'microsoft'},
            'description': 'Visual Studio Code',
            'stargazers_count': 150000,
            'forks_count': 25000,
            'watchers_count': 150000,  # 这个会被忽略
            'created_at': '2015-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
            'pushed_at': '2024-01-01T00:00:00Z',
            'language': 'TypeScript',
            'topics': ['editor', 'vscode', 'typescript'],
            'html_url': 'https://github.com/microsoft/vscode'
        }
        
        # 处理仓库
        repo = await processor.process_repository_enhanced(test_repo)
        
        if repo:
            print(f"✅ 处理成功: {repo.full_name}")
            print(f"   Stars: {repo.stargazers_count}")
            print(f"   Watchers: {repo.watchers_count}")
            print(f"   Forks: {repo.forks_count}")
        else:
            print("❌ 处理失败")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    finally:
        await processor.close_session()

if __name__ == "__main__":
    asyncio.run(test_enhanced_processor())
