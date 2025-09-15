# -*- coding: utf-8 -*-
"""
高频采集器 - 数据模型定义
更新时间: 2025-09-12
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class RepositoryData:
    """仓库数据模型"""
    
    # 基础信息
    id: int
    full_name: str
    name: str
    owner: str
    description: Optional[str] = None
    url: str = ""
    
    # 统计信息
    stargazers_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    
    # 时间信息
    created_at: str = ""
    updated_at: str = ""
    pushed_at: str = ""
    
    # 技术信息
    language: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    
    # AI 分类信息
    ai_category: str = ""
    ai_tags: List[str] = field(default_factory=list)
    
    # 评分信息
    quality_score: float = 0.0
    trending_score: float = 0.0
    
    # 采集信息
    collection_round: int = 1
    last_fork_count: int = 0
    fork_growth: int = 0
    collection_hash: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        if self.ai_tags is None:
            self.ai_tags = []
        if self.topics is None:
            self.topics = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'name': self.name,
            'owner': self.owner,
            'description': self.description,
            'url': self.url,
            'stargazers_count': self.stargazers_count,
            'forks_count': self.forks_count,
            'watchers_count': self.watchers_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'pushed_at': self.pushed_at,
            'language': self.language,
            'topics': ','.join(self.topics) if self.topics else '',
            'ai_category': self.ai_category,
            'ai_tags': ','.join(self.ai_tags) if self.ai_tags else '',
            'quality_score': self.quality_score,
            'trending_score': self.trending_score,
            'collection_round': self.collection_round,
            'last_fork_count': self.last_fork_count,
            'fork_growth': self.fork_growth,
            'collection_hash': self.collection_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RepositoryData':
        """从字典创建实例"""
        # 处理列表字段
        topics = data.get('topics', [])
        if isinstance(topics, str) and topics:
            topics = [t.strip() for t in topics.split(',') if t.strip()]
        
        ai_tags = data.get('ai_tags', [])
        if isinstance(ai_tags, str) and ai_tags:
            ai_tags = [t.strip() for t in ai_tags.split(',') if t.strip()]
        
        return cls(
            id=data.get('id', 0),
            full_name=data.get('full_name', ''),
            name=data.get('name', ''),
            owner=data.get('owner', ''),
            description=data.get('description'),
            url=data.get('url', ''),
            stargazers_count=data.get('stargazers_count', 0),
            forks_count=data.get('forks_count', 0),
            watchers_count=data.get('watchers_count', 0),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            pushed_at=data.get('pushed_at', ''),
            language=data.get('language'),
            topics=topics,
            ai_category=data.get('ai_category', ''),
            ai_tags=ai_tags,
            quality_score=data.get('quality_score', 0.0),
            trending_score=data.get('trending_score', 0.0),
            collection_round=data.get('collection_round', 1),
            last_fork_count=data.get('last_fork_count', 0),
            fork_growth=data.get('fork_growth', 0),
            collection_hash=data.get('collection_hash', '')
        )
    
    def calculate_hash(self) -> str:
        """计算采集哈希值"""
        import hashlib
        content = f"{self.id}_{self.full_name}_{self.stargazers_count}_{self.forks_count}_{self.updated_at}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_ai_related(self) -> bool:
        """判断是否为AI相关项目"""
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'gpt', 'chatgpt', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv'
        ]
        
        # 检查描述
        if self.description:
            desc_lower = self.description.lower()
            if any(keyword in desc_lower for keyword in ai_keywords):
                return True
        
        # 检查标签
        if self.topics:
            topics_lower = [topic.lower() for topic in self.topics]
            if any(keyword in topics_lower for keyword in ai_keywords):
                return True
        
        # 检查AI标签
        if self.ai_tags:
            return True
        
        return False
    
    def get_quality_indicators(self) -> Dict[str, Any]:
        """获取质量指标"""
        return {
            'stars': self.stargazers_count,
            'forks': self.forks_count,
            'watchers': self.watchers_count,
            'has_description': bool(self.description),
            'has_language': bool(self.language),
            'has_topics': len(self.topics) > 0,
            'is_ai_related': self.is_ai_related(),
            'quality_score': self.quality_score,
            'trending_score': self.trending_score
        }
