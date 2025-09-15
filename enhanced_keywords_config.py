# -*- coding: utf-8 -*-
"""
增强版关键词配置 - GitHub AI仓库搜索策略
更新时间: 2025-09-12
"""

# =============================================================================
# 搜索轮次配置
# =============================================================================

SEARCH_ROUNDS_CONFIG = [
    {
        "name": "高优先级AI关键词",
        "keywords": [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "AI", "ML", "LLM", "GPT", "ChatGPT"
        ],
        "min_stars": 100,
        "max_results": 500
    },
    {
        "name": "计算机视觉",
        "keywords": [
            "computer vision", "image recognition", "object detection",
            "face recognition", "opencv", "yolo", "resnet", "cnn"
        ],
        "min_stars": 50,
        "max_results": 400
    },
    {
        "name": "自然语言处理",
        "keywords": [
            "natural language processing", "NLP", "text processing",
            "sentiment analysis", "text classification", "BERT", "transformer"
        ],
        "min_stars": 50,
        "max_results": 400
    },
    {
        "name": "数据科学",
        "keywords": [
            "data science", "data analysis", "pandas", "numpy",
            "scikit-learn", "tensorflow", "pytorch", "keras"
        ],
        "min_stars": 30,
        "max_results": 300
    },
    {
        "name": "AI工具和框架",
        "keywords": [
            "AI framework", "AI toolkit", "AI library", "AI platform",
            "AI development", "AI research", "AI application"
        ],
        "min_stars": 20,
        "max_results": 200
    }
]

# =============================================================================
# 关键词分类配置
# =============================================================================

AI_KEYWORDS = {
    "核心AI": [
        "artificial intelligence", "machine learning", "deep learning",
        "neural network", "AI", "ML", "artificial neural network"
    ],
    "大语言模型": [
        "LLM", "GPT", "ChatGPT", "language model", "transformer",
        "BERT", "T5", "BART", "RoBERTa", "DeBERTa"
    ],
    "计算机视觉": [
        "computer vision", "image recognition", "object detection",
        "face recognition", "opencv", "yolo", "resnet", "cnn",
        "image processing", "computer vision"
    ],
    "自然语言处理": [
        "natural language processing", "NLP", "text processing",
        "sentiment analysis", "text classification", "named entity recognition",
        "text generation", "text summarization"
    ],
    "数据科学": [
        "data science", "data analysis", "pandas", "numpy",
        "scikit-learn", "data mining", "statistical analysis"
    ],
    "深度学习框架": [
        "tensorflow", "pytorch", "keras", "mxnet", "caffe",
        "theano", "torch", "tensorflow lite"
    ],
    "强化学习": [
        "reinforcement learning", "RL", "Q-learning", "policy gradient",
        "actor-critic", "deep Q network", "DQN"
    ],
    "生成模型": [
        "generative model", "GAN", "VAE", "diffusion model",
        "stable diffusion", "DALL-E", "midjourney"
    ],
    "推荐系统": [
        "recommendation system", "collaborative filtering",
        "content-based filtering", "recommender system"
    ],
    "时间序列": [
        "time series", "forecasting", "LSTM", "GRU", "ARIMA",
        "prophet", "time series analysis"
    ]
}

# =============================================================================
# 搜索策略配置
# =============================================================================

SEARCH_STRATEGIES = {
    "broad_search": {
        "description": "广泛搜索策略",
        "min_stars": 10,
        "time_range": "created:>2015-01-01",
        "max_results": 1000
    },
    "focused_search": {
        "description": "聚焦搜索策略", 
        "min_stars": 100,
        "time_range": "created:>2020-01-01",
        "max_results": 500
    },
    "premium_search": {
        "description": "精品搜索策略",
        "min_stars": 1000,
        "time_range": "created:>2022-01-01", 
        "max_results": 200
    }
}

# =============================================================================
# 质量评分配置
# =============================================================================

QUALITY_SCORING = {
    "stars_weight": 0.3,
    "forks_weight": 0.2,
    "watchers_weight": 0.1,
    "recent_activity_weight": 0.2,
    "ai_relevance_weight": 0.2
}

# =============================================================================
# 去重配置
# =============================================================================

DEDUPLICATION_CONFIG = {
    "window_days": 7,
    "fork_growth_threshold": 1,
    "relevance_threshold": 0.7
}
