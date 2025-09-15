# -*- coding: utf-8 -*-
"""
增强版关键词配置 - GitHub AI仓库搜索策略
更新时间: 2025-09-15
使用完整的关键词库，包含所有主分类和子分类
"""

# =============================================================================
# 主关键词分类 - 核心与主流领域
# =============================================================================

PRIMARY_KEYWORDS = {
    # 核心与主流领域
    "LLM": ["llm", "large-language-model", "大语言模型", "gpt"],
    "RAG": ["rag", "retrieval-augmented-generation", "检索增强生成"],
    "Diffusion": ["diffusion", "stable-diffusion", "dalle"],
    "MachineLearning": ["machine-learning", "ml", "机器学习"],
    "ComputerVision": ["computer-vision", "cv", "计算机视觉"],
    "DataScience": ["data-science", "数据科学"],
    
    # 新兴与交叉领域
    "Multimodal": ["multimodal", "多模态", "多模态大模型", "多模态ai"], # 融合多种数据类型
    "AI-Agent": ["ai-agent", "autonomous-agent", "ai-agents", "智能体", "auto-gpt"], # 具备自主决策能力的AI
    "NLP": ["nlp", "natural-language-processing", "自然语言处理"], # 传统NLP任务
    "Robotics": ["robotics", "机器人", "具身智能", "embodied-ai"], # AI与机器人技术结合
    "AI-Safety": ["ai-safety", "ai-ethics", "人工智能安全", "ai伦理"], # 安全与伦理研究
    "SpeechAI": ["speech", "voice-ai", "语音ai", "语音识别", "speech-recognition"], # 语音AI
    "AI-for-Science": ["ai-for-science", "ai-for-drug-discovery", "ai for science"], # AI在科学领域的应用
}

# =============================================================================
# LLM 二级分类
# =============================================================================

LLM_SUB_KEYWORDS = {
    "Agent": ["agent", "agents", "智能体", "autogen", "crewai"], # 补充具体框架
    "Prompt": ["prompt", "prompts", "prompt-engineering", "提示工程", "langchain", "llamaindex"], # 补充热门框架
    "Finetuning": ["finetuning", "fine-tuning", "微调"],
    "Inference": ["inference", "推理", "vllm", "tensorrt"], # 补充推理框架
    "Tool": ["tool", "tools", "工具调用"],
    "Chatbot": ["chatbot", "聊天机器人", "assistant"],
    "SpecificModel": ["llama", "qwen", "mistral", "grok", "phi-3", "chatgpt", "gemini", "claude"] # 补充新模型
}

# =============================================================================
# RAG 二级分类
# =============================================================================

RAG_SUB_KEYWORDS = {
    "VectorDB": ["vectordb", "vector-database", "向量数据库", "pinecone", "chromadb", "weaviate"], # 补充具体数据库
    "Framework": ["rag-framework", "rag-frameworks", "llamaindex", "langchain"],
    "Retriever": ["retriever", "检索器", "retrieval"],
    "KnowledgeBase": ["knowledge-base", "知识库"] # 新增知识库应用
}

# =============================================================================
# Diffusion 二级分类
# =============================================================================

DIFFUSION_SUB_KEYWORDS = {
    "Text2Image": ["text-to-image", "文生图"],
    "Image2Video": ["image-to-video", "图生视频", "video-generation", "视频生成", "stable-video-diffusion"], # 补充新模型
    "ControlNet": ["controlnet", "控制网"],
    "Lora": ["lora"],
    "Model": ["stable-diffusion", "dalle-3", "midjourney"] # 补充具体模型
}

# =============================================================================
# MachineLearning 二级分类
# =============================================================================

ML_SUB_KEYWORDS = {
    "Framework": ["framework", "框架", "pytorch", "tensorflow", "scikit-learn"],
    "Algorithm": ["algorithm", "算法"],
    "ReinforcementLearning": ["reinforcement-learning", "强化学习"],
}

# =============================================================================
# ComputerVision 二级分类
# =============================================================================

CV_SUB_KEYWORDS = {
    "ObjectDetection": ["object-detection", "目标检测", "yolo"], # 补充YOLO
    "ImageSegmentation": ["image-segmentation", "图像分割", "sam"], # 补充SAM
    "PoseEstimation": ["pose-estimation", "姿态估计"],
    "Face": ["face-recognition", "人脸识别"],
}

# =============================================================================
# DataScience 二级分类
# =============================================================================

DS_SUB_KEYWORDS = {
    "Visualization": ["visualization", "可视化", "matplotlib", "seaborn"],
    "DataCleaning": ["data-cleaning", "数据清洗", "pandas"],
    "EDA": ["eda", "探索性数据分析"]
}

# =============================================================================
# 搜索轮次配置 - 使用完整关键词库
# =============================================================================

def get_all_keywords():
    """获取所有关键词的扁平化列表"""
    all_keywords = []
    
    # 添加主关键词
    for category, keywords in PRIMARY_KEYWORDS.items():
        all_keywords.extend(keywords)
    
    # 添加LLM子关键词
    for category, keywords in LLM_SUB_KEYWORDS.items():
        all_keywords.extend(keywords)
    
    # 添加RAG子关键词
    for category, keywords in RAG_SUB_KEYWORDS.items():
        all_keywords.extend(keywords)
    
    # 添加Diffusion子关键词
    for category, keywords in DIFFUSION_SUB_KEYWORDS.items():
        all_keywords.extend(keywords)
    
    # 添加ML子关键词
    for category, keywords in ML_SUB_KEYWORDS.items():
        all_keywords.extend(keywords)
    
    # 添加CV子关键词
    for category, keywords in CV_SUB_KEYWORDS.items():
        all_keywords.extend(keywords)
    
    # 添加DS子关键词
    for category, keywords in DS_SUB_KEYWORDS.items():
        all_keywords.extend(keywords)
    
    # 去重并返回
    return list(set(all_keywords))

# 生成搜索轮次配置
SEARCH_ROUNDS_CONFIG = [
    {
        "name": "LLM大语言模型",
        "keywords": [kw for kw in PRIMARY_KEYWORDS["LLM"] + 
                    [item for sublist in LLM_SUB_KEYWORDS.values() for item in sublist]],
        "min_stars": 20,
        "max_results": 400
    },
    {
        "name": "RAG检索增强生成",
        "keywords": [kw for kw in PRIMARY_KEYWORDS["RAG"] + 
                    [item for sublist in RAG_SUB_KEYWORDS.values() for item in sublist]],
        "min_stars": 15,
        "max_results": 300
    },
    {
        "name": "Diffusion生成模型",
        "keywords": [kw for kw in PRIMARY_KEYWORDS["Diffusion"] + 
                    [item for sublist in DIFFUSION_SUB_KEYWORDS.values() for item in sublist]],
        "min_stars": 15,
        "max_results": 300
    },
    {
        "name": "机器学习框架",
        "keywords": [kw for kw in PRIMARY_KEYWORDS["MachineLearning"] + 
                    [item for sublist in ML_SUB_KEYWORDS.values() for item in sublist]],
        "min_stars": 10,
        "max_results": 400
    },
    {
        "name": "计算机视觉",
        "keywords": [kw for kw in PRIMARY_KEYWORDS["ComputerVision"] + 
                    [item for sublist in CV_SUB_KEYWORDS.values() for item in sublist]],
        "min_stars": 10,
        "max_results": 300
    },
    {
        "name": "数据科学",
        "keywords": [kw for kw in PRIMARY_KEYWORDS["DataScience"] + 
                    [item for sublist in DS_SUB_KEYWORDS.values() for item in sublist]],
        "min_stars": 5,
        "max_results": 200
    },
    {
        "name": "新兴AI领域",
        "keywords": [kw for kw in PRIMARY_KEYWORDS["Multimodal"] + 
                    PRIMARY_KEYWORDS["AI-Agent"] + 
                    PRIMARY_KEYWORDS["Robotics"] + 
                    PRIMARY_KEYWORDS["AI-Safety"] + 
                    PRIMARY_KEYWORDS["SpeechAI"] + 
                    PRIMARY_KEYWORDS["AI-for-Science"]],
        "min_stars": 5,
        "max_results": 300
    },
    {
        "name": "传统NLP",
        "keywords": PRIMARY_KEYWORDS["NLP"],
        "min_stars": 10,
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
