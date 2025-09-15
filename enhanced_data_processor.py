#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版数据处理器 - 修复watchers_count问题
功能: 获取真正的subscribers_count (watchers_count)
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from data_processor import DataProcessor
from config_v2 import Config, APIConfig
from high_frequency_collector import RepositoryData

class EnhancedDataProcessor(DataProcessor):
    """增强版数据处理器 - 修复watchers_count问题"""
    
    def __init__(self):
        super().__init__()
        self.session = None
        self.config = Config()
        
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
                    self.logger.debug(f"获取真实watchers_count: {repo_full_name} -> {subscribers_count}")
                    return subscribers_count
                else:
                    self.logger.warning(f"获取仓库详情失败: {repo_full_name} - {response.status}")
                    return 0
                    
        except Exception as e:
            self.logger.error(f"获取watchers_count异常: {repo_full_name} | {e}")
            return 0
    
    def extract_basic_data(self, repo_raw: Dict[str, Any]) -> RepositoryData:
        """提取基础仓库数据 - 重写以处理watchers_count"""
        owner_info = repo_raw.get("owner", {})
        
        return RepositoryData(
            id=str(repo_raw.get("id", "")),
            full_name=repo_raw.get("full_name", ""),
            name=repo_raw.get("name", ""),
            owner=owner_info.get("login", ""),
            description=repo_raw.get("description", "") or "",
            url=repo_raw.get("html_url", ""),
            stargazers_count=repo_raw.get("stargazers_count", 0),
            forks_count=repo_raw.get("forks_count", 0),
            watchers_count=0,  # 暂时设为0，稍后通过API获取真实值
            created_at=self.convert_to_beijing_time(repo_raw.get("created_at", "")),
            updated_at=self.convert_to_beijing_time(repo_raw.get("updated_at", "")),
            pushed_at=self.convert_to_beijing_time(repo_raw.get("pushed_at", "")),
            language=repo_raw.get("language", "") or "Unknown",
            topics=repo_raw.get("topics", []),
            collection_round=repo_raw.get("search_round", 1)
        )
    
    async def process_repository_enhanced(self, repo_raw: Dict[str, Any]) -> Optional[RepositoryData]:
        """增强版处理单个仓库数据 - 包含真实watchers_count获取"""
        try:
            # 基础数据提取
            repo_data = self.extract_basic_data(repo_raw)
            
            # 获取真实的watchers_count (仅对高质量项目)
            if repo_data.quality_score >= 50:  # 只对高质量项目获取真实watchers_count
                real_watchers = await self.get_real_watchers_count(repo_data.full_name)
                repo_data.watchers_count = real_watchers
            else:
                # 对于低质量项目，使用估算值 (通常是stars的5-10%)
                estimated_watchers = max(1, int(repo_data.stargazers_count * 0.07))
                repo_data.watchers_count = estimated_watchers
            
            # AI分类
            repo_data.ai_category = self.categorize_ai_project(repo_data)
            
            # 提取AI技术标签
            repo_data.ai_tags = self.extract_ai_tags(repo_data)
            
            # 计算质量评分
            repo_data.quality_score = self.calculate_quality_score(repo_data)
            
            # 计算趋势评分
            repo_data.trending_score = self.calculate_trending_score(repo_data)
            
            # 质量过滤
            if repo_data.quality_score < self.config.MIN_QUALITY_SCORE:
                self.logger.debug(f"质量评分过低: {repo_data.full_name} ({repo_data.quality_score})")
                return None
            
            # AI相关性检查
            ai_relevance = self.calculate_ai_relevance(repo_data)
            if ai_relevance < 2:
                self.logger.debug(f"AI相关性过低: {repo_data.full_name} ({ai_relevance})")
                return None
            
            return repo_data
            
        except Exception as e:
            self.logger.error(f"处理仓库数据失败: {repo_raw.get('full_name', 'unknown')} | {e}")
            return None

# 批量处理增强版
async def process_repositories_batch_enhanced(repos_raw: List[Dict[str, Any]]) -> List[RepositoryData]:
    """批量处理仓库数据 - 增强版"""
    processor = EnhancedDataProcessor()
    processed_repos = []
    
    try:
        # 并发处理，但限制并发数以避免API限制
        semaphore = asyncio.Semaphore(5)  # 最多5个并发请求
        
        async def process_single_repo(repo_raw):
            async with semaphore:
                return await processor.process_repository_enhanced(repo_raw)
        
        # 创建所有任务
        tasks = [process_single_repo(repo_raw) for repo_raw in repos_raw]
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集有效结果
        for result in results:
            if isinstance(result, RepositoryData):
                processed_repos.append(result)
            elif isinstance(result, Exception):
                processor.logger.error(f"处理异常: {result}")
        
        return processed_repos
        
    finally:
        await processor.close_session()

if __name__ == "__main__":
    # 测试代码
    async def test_enhanced_processor():
        processor = EnhancedDataProcessor()
        
        # 测试获取真实watchers_count
        test_repo = "microsoft/vscode"  # 一个知名项目
        real_watchers = await processor.get_real_watchers_count(test_repo)
        print(f"测试项目 {test_repo} 的真实watchers_count: {real_watchers}")
        
        await processor.close_session()
    
    asyncio.run(test_enhanced_processor())
