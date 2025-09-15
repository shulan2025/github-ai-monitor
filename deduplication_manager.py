# -*- coding: utf-8 -*-
"""
GitHub AI仓库去重管理器 V2.0
功能: 7天fork增长去重机制
更新时间: 2025-09-06
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from cloudflare import Cloudflare

from config_v2 import Config, DatabaseConfig
from high_frequency_collector import RepositoryData

class DeduplicationManager:
    """去重管理器"""
    
    def __init__(self, cloudflare_client: Cloudflare, config: Config):
        self.cloudflare_client = cloudflare_client
        self.config = config
        self.db_config = DatabaseConfig()
        self.logger = logging.getLogger('ai_collector_v2.dedup')
    
    async def should_store_repository(self, repo: RepositoryData) -> Tuple[bool, str]:
        """
        判断是否应该存储仓库
        返回: (是否存储, 原因说明)
        """
        try:
            # 查询已存在的记录
            existing_record = await self.get_existing_record(repo.id)
            
            if not existing_record:
                # 新项目直接收录
                return True, "新项目"
            
            # 去除智能去重规则 - 直接更新现有记录
            return True, "更新现有记录"
            
        except Exception as e:
            self.logger.error(f"去重检查失败: {repo.full_name} | {e}")
            # 出错时默认存储，确保数据完整性
            return True, f"去重检查异常，强制存储: {e}"
    
    async def get_existing_record(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """获取已存在的仓库记录"""
        try:
            response = self.cloudflare_client.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=self.db_config.SELECT_EXISTING_SQL,
                params=[repo_id]
            )
            
            if response.success and response.result and response.result[0].results:
                results = response.result[0].results
                if results and len(results) > 0:
                    row = results[0]
                    # 修复: 确保映射正确且值不为字段名
                    if len(row) >= 4:
                        record = {
                            'id': row[0],
                            'forks_count': row[1], 
                            'last_collected_at': row[2],
                            'collection_hash': row[3]
                        }
                        
                        # 关键修复: 检查last_collected_at是否为字段名
                        if record['last_collected_at'] == 'last_collected_at':
                            self.logger.warning(f"检测到字段名作为值的问题，记录ID: {repo_id}")
                            record['last_collected_at'] = None
                            
                        return record
            
            return None
            
        except Exception as e:
            self.logger.error(f"查询已存在记录失败: {repo_id} | {e}")
            return None
    
    async def check_deduplication_rules(self, repo: RepositoryData, 
                                      existing_record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查去重规则
        核心规则: 7天内如果fork有增长则可以重新收录
        """
        try:
            current_forks = repo.forks_count
            last_forks = existing_record.get('forks_count', 0)
            last_collected_str = existing_record.get('last_collected_at')
            
            # 确保数据类型正确
            try:
                last_forks = int(last_forks) if last_forks else 0
                current_forks = int(current_forks) if current_forks else 0
            except (ValueError, TypeError):
                last_forks = 0
                current_forks = int(current_forks) if current_forks else 0
            
            # 计算fork增长
            fork_growth = current_forks - last_forks
            repo.fork_growth = max(0, fork_growth)
            
            # 检查上次收录时间
            if not last_collected_str:
                return True, "无历史收录时间记录"
            
            # 解析时间
            last_collected = self.parse_datetime(last_collected_str)
            if not last_collected:
                return True, "无法解析历史收录时间"
            
            # 计算时间差
            time_diff = datetime.utcnow() - last_collected
            days_since_last = time_diff.days
            
            self.logger.debug(
                f"去重检查: {repo.full_name} | "
                f"距离上次: {days_since_last}天 | "
                f"Fork增长: {fork_growth} | "
                f"当前Fork: {current_forks}"
            )
            
            # 应用7天去重规则
            if days_since_last <= self.config.DEDUP_WINDOW_DAYS:
                # 7天内的项目
                if fork_growth > 0:
                    return True, f"7天内fork增长 +{fork_growth} (从{last_forks}到{current_forks})"
                else:
                    return False, f"7天内无fork增长 ({current_forks}fork)"
            else:
                # 超过7天的项目
                return True, f"超过{self.config.DEDUP_WINDOW_DAYS}天窗口期 ({days_since_last}天)"
            
        except Exception as e:
            self.logger.error(f"去重规则检查失败: {repo.full_name} | {e}")
            return False, f"去重规则异常: {e}"
    
    def parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """解析日期时间字符串"""
        try:
            # 尝试多种格式
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            # 尝试ISO格式
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00')).replace(tzinfo=None)
            
        except Exception as e:
            self.logger.warning(f"日期解析失败: {datetime_str} | {e}")
            return None
    
    async def check_content_changes(self, repo: RepositoryData, 
                                  existing_record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查内容是否有变化
        """
        try:
            # 计算当前内容哈希
            current_hash = self.calculate_content_hash(repo)
            last_hash = existing_record.get('collection_hash', '')
            
            if current_hash != last_hash:
                return True, "项目内容有更新"
            else:
                return False, "项目内容无变化"
                
        except Exception as e:
            self.logger.error(f"内容变化检查失败: {repo.full_name} | {e}")
            return True, "内容检查异常，默认允许"
    
    def calculate_content_hash(self, repo: RepositoryData) -> str:
        """计算仓库内容哈希"""
        import hashlib
        
        content = "|".join([
            repo.name,
            repo.description or "",
            str(repo.stargazers_count),
            str(repo.forks_count),
            repo.language or "",
            json.dumps(sorted(repo.topics))
        ])
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def get_deduplication_stats(self) -> Dict[str, Any]:
        """获取去重统计信息"""
        try:
            # 查询总项目数
            total_response = self.cloudflare_client.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql="SELECT COUNT(*) as total FROM github_ai_post_attr"
            )
            
            total_count = 0
            if total_response.success and total_response.result:
                results = total_response.result[0].results
                if results and len(results) > 0:
                    total_count = results[0][0] if results[0] else 0
            
            # 查询最近7天的更新数
            recent_response = self.cloudflare_client.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql="""
                SELECT COUNT(*) as recent 
                FROM github_ai_post_attr 
                WHERE last_collected_at >= datetime('now', '-7 days')
                """
            )
            
            recent_count = 0
            if recent_response.success and recent_response.result:
                results = recent_response.result[0].results
                if results and len(results) > 0:
                    recent_count = results[0][0] if results[0] else 0
            
            # 查询有fork增长的项目数
            growth_response = self.cloudflare_client.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql="""
                SELECT COUNT(*) as growth 
                FROM github_ai_post_attr 
                WHERE fork_growth > 0 AND last_collected_at >= datetime('now', '-7 days')
                """
            )
            
            growth_count = 0
            if growth_response.success and growth_response.result:
                results = growth_response.result[0].results
                if results and len(results) > 0:
                    growth_count = results[0][0] if results[0] else 0
            
            return {
                "total_projects": total_count,
                "recent_updates": recent_count,
                "fork_growth_projects": growth_count,
                "dedup_window_days": self.config.DEDUP_WINDOW_DAYS,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取去重统计失败: {e}")
            return {
                "total_projects": 0,
                "recent_updates": 0,
                "fork_growth_projects": 0,
                "error": str(e)
            }
    
    async def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """
        清理过期记录
        保留最近N天的数据，删除更早的记录
        """
        try:
            self.logger.info(f"开始清理{days_to_keep}天前的记录")
            
            # 删除过期记录
            response = self.cloudflare_client.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=f"""
                DELETE FROM github_ai_post_attr 
                WHERE collection_time < datetime('now', '-{days_to_keep} days')
                AND is_active = 0
                """
            )
            
            if response.success:
                # 获取删除的行数 (D1可能不支持affected_rows)
                self.logger.info("过期记录清理完成")
                return 1  # 返回操作成功标记
            else:
                self.logger.error(f"清理过期记录失败: {response.errors}")
                return 0
                
        except Exception as e:
            self.logger.error(f"清理过期记录异常: {e}")
            return 0
    
    async def mark_inactive_projects(self, inactive_days: int = 365) -> int:
        """
        标记不活跃项目
        超过N天没有更新的项目标记为不活跃
        """
        try:
            self.logger.info(f"标记{inactive_days}天未更新的项目为不活跃")
            
            response = self.cloudflare_client.d1.database.query(
                database_id=self.config.D1_DATABASE_ID,
                account_id=self.config.CLOUDFLARE_ACCOUNT_ID,
                sql=f"""
                UPDATE github_ai_post_attr 
                SET is_active = 0 
                WHERE pushed_at < datetime('now', '-{inactive_days} days')
                AND is_active = 1
                """
            )
            
            if response.success:
                self.logger.info("不活跃项目标记完成")
                return 1
            else:
                self.logger.error(f"标记不活跃项目失败: {response.errors}")
                return 0
                
        except Exception as e:
            self.logger.error(f"标记不活跃项目异常: {e}")
            return 0

class AdvancedDeduplicationRules:
    """高级去重规则 (可扩展)"""
    
    @staticmethod
    def quality_based_reentry(repo: RepositoryData, existing_record: Dict[str, Any]) -> Tuple[bool, str]:
        """基于质量提升的重新收录"""
        try:
            current_quality = repo.quality_score
            last_quality = existing_record.get('quality_score', 0)
            
            quality_improvement = current_quality - last_quality
            
            if quality_improvement >= 10:  # 质量分提升10分以上
                return True, f"质量显著提升 +{quality_improvement}分"
            
            return False, f"质量提升不足 +{quality_improvement}分"
            
        except Exception:
            return False, "质量检查异常"
    
    @staticmethod
    def star_growth_based_reentry(repo: RepositoryData, existing_record: Dict[str, Any]) -> Tuple[bool, str]:
        """基于星标增长的重新收录"""
        try:
            current_stars = repo.stargazers_count
            last_stars = existing_record.get('stargazers_count', 0)
            
            star_growth = current_stars - last_stars
            growth_rate = star_growth / max(last_stars, 1)  # 避免除零
            
            if star_growth >= 100 or growth_rate >= 0.5:  # 绝对增长100+ 或 增长率50%+
                return True, f"星标显著增长 +{star_growth} ({growth_rate:.1%})"
            
            return False, f"星标增长不足 +{star_growth}"
            
        except Exception:
            return False, "星标检查异常"
    
    @staticmethod
    def category_change_based_reentry(repo: RepositoryData, existing_record: Dict[str, Any]) -> Tuple[bool, str]:
        """基于分类变化的重新收录"""
        try:
            current_category = repo.ai_category
            last_category = existing_record.get('ai_category', '')
            
            if current_category != last_category and current_category:
                return True, f"分类变化: {last_category} → {current_category}"
            
            return False, "分类无变化"
            
        except Exception:
            return False, "分类检查异常"
