# -*- coding: utf-8 -*-
"""
监控系统 - 采集指标和性能监控
更新时间: 2025-09-12
"""

import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class CollectionMetrics:
    """采集指标数据类"""
    
    # 基础统计
    total_searched: int = 0
    total_collected: int = 0
    total_stored: int = 0
    total_skipped: int = 0
    
    # 分类统计
    new_repositories: int = 0
    updated_repositories: int = 0
    duplicate_repositories: int = 0
    
    # 质量统计
    avg_quality_score: float = 0.0
    avg_trending_score: float = 0.0
    avg_ai_relevance_score: float = 0.0
    
    # 性能统计
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = None
    total_duration: float = 0.0
    api_calls_made: int = 0
    api_rate_limit_remaining: int = 0
    
    # 错误统计
    api_errors: int = 0
    storage_errors: int = 0
    processing_errors: int = 0
    
    # 关键词统计
    keywords_used: List[str] = field(default_factory=list)
    search_rounds_completed: int = 0
    
    def calculate_duration(self):
        """计算总耗时"""
        if self.end_time:
            self.total_duration = (self.end_time - self.start_time).total_seconds()
        else:
            self.total_duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_searched == 0:
            return 0.0
        return (self.total_stored / self.total_searched) * 100
    
    def get_throughput(self) -> float:
        """获取吞吐量 (项目/分钟)"""
        if self.total_duration == 0:
            return 0.0
        return (self.total_stored / self.total_duration) * 60

class MonitoringSystem:
    """监控系统"""
    
    def __init__(self):
        self.metrics = CollectionMetrics()
        self.logger = logging.getLogger('monitoring')
        
    def start_collection(self):
        """开始采集监控"""
        self.metrics.start_time = datetime.now(timezone.utc)
        self.logger.info("🚀 开始采集监控")
    
    def end_collection(self):
        """结束采集监控"""
        self.metrics.end_time = datetime.now(timezone.utc)
        self.metrics.calculate_duration()
        self.logger.info("✅ 采集监控结束")
    
    def record_search(self, keyword: str, results_count: int):
        """记录搜索操作"""
        self.metrics.total_searched += results_count
        self.metrics.keywords_used.append(keyword)
        self.metrics.api_calls_made += 1
    
    def record_collection(self, count: int):
        """记录采集操作"""
        self.metrics.total_collected += count
    
    def record_storage(self, new_count: int, updated_count: int, skipped_count: int):
        """记录存储操作"""
        self.metrics.total_stored += new_count + updated_count
        self.metrics.new_repositories += new_count
        self.metrics.updated_repositories += updated_count
        self.metrics.total_skipped += skipped_count
    
    def record_duplicate(self, count: int):
        """记录重复项目"""
        self.metrics.duplicate_repositories += count
    
    def record_quality_scores(self, quality_scores: List[float], 
                            trending_scores: List[float], 
                            ai_scores: List[float]):
        """记录质量评分"""
        if quality_scores:
            self.metrics.avg_quality_score = sum(quality_scores) / len(quality_scores)
        if trending_scores:
            self.metrics.avg_trending_score = sum(trending_scores) / len(trending_scores)
        if ai_scores:
            self.metrics.avg_ai_relevance_score = sum(ai_scores) / len(ai_scores)
    
    def record_api_error(self):
        """记录API错误"""
        self.metrics.api_errors += 1
    
    def record_storage_error(self):
        """记录存储错误"""
        self.metrics.storage_errors += 1
    
    def record_processing_error(self):
        """记录处理错误"""
        self.metrics.processing_errors += 1
    
    def record_rate_limit(self, remaining: int):
        """记录API速率限制"""
        self.metrics.api_rate_limit_remaining = remaining
    
    def complete_search_round(self):
        """完成搜索轮次"""
        self.metrics.search_rounds_completed += 1
    
    def get_summary_report(self) -> str:
        """获取汇总报告"""
        self.metrics.calculate_duration()
        
        report = f"""
📊 采集统计报告
{'='*50}
⏱️  总耗时: {self.metrics.total_duration:.2f} 秒
🔍 搜索项目: {self.metrics.total_searched:,}
📥 采集项目: {self.metrics.total_collected:,}
💾 存储项目: {self.metrics.total_stored:,}
⏭️  跳过项目: {self.metrics.total_skipped:,}
🔄 重复项目: {self.metrics.duplicate_repositories:,}

📈 分类统计:
  • 新项目: {self.metrics.new_repositories:,}
  • 更新项目: {self.metrics.updated_repositories:,}

⭐ 质量评分:
  • 平均质量评分: {self.metrics.avg_quality_score:.2f}
  • 平均热度评分: {self.metrics.avg_trending_score:.2f}
  • 平均AI相关性: {self.metrics.avg_ai_relevance_score:.2f}

🚀 性能指标:
  • 成功率: {self.metrics.get_success_rate():.2f}%
  • 吞吐量: {self.metrics.get_throughput():.2f} 项目/分钟
  • API调用: {self.metrics.api_calls_made:,} 次
  • 剩余限制: {self.metrics.api_rate_limit_remaining:,}

🔧 搜索统计:
  • 搜索轮次: {self.metrics.search_rounds_completed}
  • 使用关键词: {len(set(self.metrics.keywords_used))} 个

❌ 错误统计:
  • API错误: {self.metrics.api_errors}
  • 存储错误: {self.metrics.storage_errors}
  • 处理错误: {self.metrics.processing_errors}
{'='*50}
        """
        return report
    
    def log_progress(self, current: int, total: int, operation: str = "处理"):
        """记录进度"""
        if total > 0:
            percentage = (current / total) * 100
            self.logger.info(f"📊 {operation}进度: {current}/{total} ({percentage:.1f}%)")
    
    def log_performance(self):
        """记录性能信息"""
        self.metrics.calculate_duration()
        self.logger.info(f"⚡ 性能统计: 耗时 {self.metrics.total_duration:.2f}s, "
                        f"吞吐量 {self.metrics.get_throughput():.2f} 项目/分钟")
    
    def reset_metrics(self):
        """重置指标"""
        self.metrics = CollectionMetrics()
        self.logger.info("🔄 监控指标已重置")
