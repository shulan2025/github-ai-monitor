#!/usr/bin/env python3
"""
增强版搜索配置 - 为提高有效数据收集率设计
目标：从20%有效率提升到每天200条有效数据
"""

# ================================
# 🎯 增强搜索配置
# ================================

# 基础配置：多轮次搜索策略
ENHANCED_SEARCH_CONFIG = {
    # GitHub API限制：每次最多100条
    "per_page": 100,
    
    # 多轮搜索配置
    "search_rounds": 10,  # 执行10轮搜索，理论上可获取1000条候选
    
    # 时间窗口分割
    "time_splits": 3,     # 将30天分为3个10天窗口
    
    # 星标要求分层（更现实的设置）
    "star_tiers": [
        {"min": 100, "days": 30},  # 高质量：30天内100+星标
        {"min": 50, "days": 60},   # 中质量：60天内50+星标  
        {"min": 20, "days": 90},   # 广覆盖：90天内20+星标
        {"min": 10, "days": 180},  # 发现新项目：180天内10+星标
    ]
}

# ================================
# 🔍 多维度搜索关键词
# ================================

# 核心技术栈关键词（分组搜索）
TECH_KEYWORD_GROUPS = {
    "llm_core": ["LLM", "large-language-model", "transformer", "GPT"],
    "llm_training": ["fine-tuning", "PEFT", "LoRA", "QLoRA", "instruction-tuning"],
    "llm_inference": ["inference", "serving", "vllm", "ollama", "llama"],
    
    "rag_tech": ["RAG", "retrieval-augmented", "vector-database", "embedding"],
    "rag_tools": ["chromadb", "pinecone", "weaviate", "qdrant", "milvus"],
    
    "diffusion_models": ["diffusion", "stable-diffusion", "DDPM", "DDIM"],
    "image_gen": ["text-to-image", "image-generation", "DALL-E", "midjourney"],
    
    "ml_frameworks": ["pytorch", "tensorflow", "jax", "scikit-learn"],
    "ml_algorithms": ["deep-learning", "neural-network", "machine-learning"],
    
    "cv_detection": ["object-detection", "YOLO", "RCNN", "detection"],
    "cv_recognition": ["image-classification", "face-recognition", "OCR"],
    "cv_segmentation": ["segmentation", "semantic-segmentation", "instance-segmentation"],
    
    "data_processing": ["data-science", "pandas", "numpy", "jupyter"],
    "data_analysis": ["data-analysis", "visualization", "analytics", "statistics"],
    
    "ai_agents": ["agent", "autonomous", "multi-agent", "langchain"],
    "ai_tools": ["chatbot", "assistant", "automation", "workflow"]
}

# 热门开源项目关键词
TRENDING_KEYWORDS = [
    # 2024年热门技术
    "multimodal", "vision-language", "CLIP", "BLIP",
    "code-generation", "coding-assistant", "github-copilot",
    "speech-to-text", "text-to-speech", "whisper",
    "robotics", "embodied-ai", "simulation",
    "federated-learning", "privacy-preserving",
    "edge-ai", "mobile-ai", "quantization",
    "mlops", "model-deployment", "monitoring"
]

# 编程语言组合（提高匹配度）
LANGUAGE_COMBINATIONS = [
    ["Python"],
    ["JavaScript", "TypeScript"],  
    ["Rust"],
    ["Go"],
    ["C++"],
    ["Julia", "R"]
]

# ================================
# 🎯 智能搜索策略
# ================================

def generate_search_queries():
    """生成多样化的搜索查询"""
    queries = []
    
    # 策略1：技术栈组合搜索
    for group_name, keywords in TECH_KEYWORD_GROUPS.items():
        for i in range(0, len(keywords), 2):  # 每2个关键词一组
            keyword_pair = keywords[i:i+2]
            query_terms = " OR ".join(keyword_pair)
            queries.append({
                "name": f"tech_{group_name}_{i//2}",
                "terms": query_terms,
                "focus": group_name
            })
    
    # 策略2：热门技术搜索
    for i in range(0, len(TRENDING_KEYWORDS), 3):  # 每3个关键词一组
        keyword_group = TRENDING_KEYWORDS[i:i+3]
        query_terms = " OR ".join(keyword_group)
        queries.append({
            "name": f"trending_{i//3}",
            "terms": query_terms,
            "focus": "trending"
        })
    
    # 策略3：语言特定搜索
    for lang_group in LANGUAGE_COMBINATIONS:
        for tech_group, tech_keywords in list(TECH_KEYWORD_GROUPS.items())[:3]:  # 只用前3个技术组
            lang_filter = " OR ".join([f"language:{lang}" for lang in lang_group])
            tech_filter = " OR ".join(tech_keywords[:2])  # 只用前2个关键词
            queries.append({
                "name": f"lang_{'-'.join(lang_group).lower()}_{tech_group}",
                "terms": f"({tech_filter}) {lang_filter}",
                "focus": f"language_{lang_group[0]}"
            })
    
    return queries

# ================================
# 📊 搜索排序策略
# ================================

SORT_STRATEGIES = [
    {"sort": "stars", "order": "desc"},      # 按星标降序
    {"sort": "updated", "order": "desc"},    # 按更新时间降序
    {"sort": "created", "order": "desc"},    # 按创建时间降序
]

# ================================
# 🔄 时间窗口策略
# ================================

def get_time_windows():
    """获取时间窗口列表，扩大时间范围以获取更多项目"""
    from datetime import datetime, timedelta
    
    windows = []
    
    # 最近30天（高质量项目）
    end = datetime.now()
    start = end - timedelta(days=30)
    windows.append({
        "name": "recent_month",
        "range": f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "priority": "high",
        "min_stars": 100
    })
    
    # 最近60天（中等质量）
    end = datetime.now() - timedelta(days=30)
    start = end - timedelta(days=60)
    windows.append({
        "name": "recent_2months",
        "range": f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "priority": "medium",
        "min_stars": 50
    })
    
    # 最近90天（广泛覆盖）
    end = datetime.now() - timedelta(days=60)
    start = end - timedelta(days=90)
    windows.append({
        "name": "recent_3months",
        "range": f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "priority": "medium",
        "min_stars": 20
    })
    
    # 最近180天（发现新兴项目）
    end = datetime.now() - timedelta(days=90)
    start = end - timedelta(days=180)
    windows.append({
        "name": "recent_6months",
        "range": f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}",
        "priority": "low",
        "min_stars": 10
    })
    
    return windows

# ================================
# 🎯 过滤优化配置
# ================================

# 降低过滤阈值以获取更多候选
ENHANCED_FILTER_CONFIG = {
    "ai_relevance_threshold": 1,  # 从2降到1，获取更多候选
    "min_description_length": 20,  # 至少20字符描述
    "exclude_forks": True,         # 排除Fork项目
    "exclude_archived": True,      # 排除已归档项目
    "min_repo_age_days": 1,       # 至少存在1天
}

# 重新定义高价值关键词（更全面）
HIGH_VALUE_KEYWORDS = [
    # AI核心
    "artificial-intelligence", "machine-learning", "deep-learning",
    "neural-network", "transformer", "attention", "bert", "gpt",
    
    # 具体应用
    "computer-vision", "natural-language-processing", "nlp", 
    "speech-recognition", "image-recognition", "object-detection",
    
    # 工具框架
    "pytorch", "tensorflow", "scikit-learn", "keras", "jax",
    "huggingface", "transformers", "diffusers", "langchain",
    
    # 新兴技术
    "multimodal", "foundation-model", "large-language-model",
    "diffusion-model", "generative-ai", "federated-learning"
]

# ================================
# 📈 执行策略配置
# ================================

EXECUTION_STRATEGY = {
    # 搜索轮次分配
    "primary_searches": 15,    # 主要搜索15次
    "secondary_searches": 10,  # 次要搜索10次
    "exploratory_searches": 5, # 探索性搜索5次
    
    # API调用间隔（遵守GitHub限制）
    "request_delay": 1.0,      # 每次请求间隔1秒
    "batch_delay": 10.0,       # 每批次间隔10秒
    
    # 目标设置
    "target_candidates": 1000, # 目标候选项目数
    "target_valid": 200,       # 目标有效项目数
    "expected_efficiency": 0.2 # 预期20%有效率
}

# ================================
# 💡 使用说明
# ================================
"""
🎯 增强搜索策略说明：

1. 多轮搜索：执行30轮不同的搜索查询
2. 时间分割：覆盖不同时间窗口
3. 技术分组：按AI技术栈分组搜索
4. 语言过滤：针对特定编程语言
5. 排序多样：使用不同排序策略

预期效果：
- 候选项目：1000+ 
- 有效项目：200+
- 有效率：20%+
- 重复率：<10%（通过数据库去重）

GitHub API限制：
- 搜索API：1000次/小时
- 我们使用：30次/天
- 安全余量：充足
"""
