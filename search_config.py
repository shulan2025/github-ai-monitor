#!/usr/bin/env python3
"""
GitHub AI 仓库搜索配置文件
您可以通过修改这个文件来自定义搜索行为
"""

# ================================
# 🎯 搜索参数配置
# ================================

SEARCH_CONFIG = {
    # ⭐ 最小星标要求 - 平衡质量与数量
    "min_stars": 100,  # 平衡质量与数量的项目
    
    # 📅 搜索时间范围 (天) - 扩大范围
    "days_back": 30,   # 最近30天的前沿项目
    
    # 📊 每次搜索返回的最大仓库数
    "per_page": 100,  # GitHub API 限制: 最大100
}

# ================================
# 🔍 搜索关键词配置
# ================================

# 🧠 大语言模型 (LLM) - 最前沿
LLM_TERMS = [
    "LLM", "large-language-model", "transformer", "GPT", "ChatGPT", 
    "fine-tuning", "PEFT", "LoRA", "QLoRA", "instruction-tuning"
]

# 🔍 检索增强生成 (RAG) - 热门技术
RAG_TERMS = [
    "RAG", "retrieval-augmented", "vector-database", "embedding", 
    "semantic-search", "knowledge-graph", "document-qa"
]

# 🎨 扩散模型 (Diffusion) - 生成式AI前沿
DIFFUSION_TERMS = [
    "diffusion-model", "stable-diffusion", "text-to-image", 
    "image-generation", "DALL-E", "Midjourney-like", "DDPM"
]

# 🤖 机器学习 - 核心算法与框架
ML_TERMS = [
    "machine-learning", "deep-learning", "neural-network", 
    "tensorflow", "pytorch", "scikit-learn", "keras",
    "gradient-boosting", "random-forest", "SVM"
]

# 👁️ 计算机视觉 - 图像处理与识别
CV_TERMS = [
    "computer-vision", "object-detection", "image-recognition",
    "YOLO", "opencv", "image-classification", "segmentation",
    "face-recognition", "OCR", "image-processing"
]

# 📊 数据科学 - 分析与可视化
DS_TERMS = [
    "data-science", "data-analysis", "data-visualization",
    "pandas", "numpy", "matplotlib", "jupyter",
    "statistical-analysis", "data-mining", "analytics"
]

# ================================
# ⚙️ 高级搜索配置
# ================================

# 启用 / 禁用特定的搜索领域 - 全面覆盖AI技术
ENABLE_DOMAINS = {
    "LLM": True,            # 大语言模型 - 最热门
    "RAG": True,            # 检索增强生成 - 实用技术  
    "Diffusion": True,      # 扩散模型 - 生成式AI前沿
    "MachineLearning": True, # 通用机器学习 - 开启
    "ComputerVision": True,   # 计算机视觉 - 开启
    "DataScience": True      # 数据科学 - 开启
}

# 编程语言偏好 (留空表示不限制)
PREFERRED_LANGUAGES = [
    # "Python",
    # "JavaScript", 
    # "TypeScript",
    # "Rust",
    # "Go",
    # "C++",
    # "Java"
]

# ================================
# 🚫 过滤配置
# ================================

# AI 相关性评分阈值 (1-10分，>=此分数才会被保留)
AI_RELEVANCE_THRESHOLD = 2

# 是否启用严格过滤模式 (过滤更多边缘案例)
STRICT_FILTERING = True

# 自定义排除关键词 (这些项目将被过滤掉)
CUSTOM_EXCLUDE_KEYWORDS = [
    # 在这里添加您想要排除的关键词
    # 例如: "tutorial", "example", "demo"
]

# ================================
# 📈 搜索策略配置  
# ================================

# 搜索策略: "broad" (广泛搜索) 或 "focused" (精确搜索)
SEARCH_STRATEGY = "focused"

# 是否包含最近更新的仓库 (不仅仅是新创建的)
INCLUDE_RECENTLY_UPDATED = False

# ================================
# 🎛️ 快速配置预设
# ================================

def get_preset_config(preset_name):
    """获取预设配置"""
    presets = {
        "conservative": {  # 保守模式：高质量项目
            "min_stars": 100,
            "days_back": 30,
            "AI_RELEVANCE_THRESHOLD": 4,
            "STRICT_FILTERING": True
        },
        "aggressive": {    # 激进模式：更多项目
            "min_stars": 5,
            "days_back": 7,
            "AI_RELEVANCE_THRESHOLD": 1,
            "STRICT_FILTERING": False
        },
        "balanced": {      # 平衡模式：当前默认
            "min_stars": 10,
            "days_back": 7,
            "AI_RELEVANCE_THRESHOLD": 2,
            "STRICT_FILTERING": True
        }
    }
    return presets.get(preset_name, presets["balanced"])

# ================================
# 💡 使用说明
# ================================
"""
🎯 如何自定义搜索：

1. 调整星标要求：
   - 更高质量：min_stars = 100
   - 更多结果：min_stars = 5

2. 调整时间范围：
   - 最新项目：days_back = 1
   - 更多历史：days_back = 30

3. 专注特定领域：
   - 只搜索LLM：将其他域设为False
   - 只搜索CV：Enable_DOMAINS["computer_vision"] = True，其他为False

4. 使用预设配置：
   from search_config import get_preset_config
   config = get_preset_config("conservative")

5. 编程语言过滤：
   PREFERRED_LANGUAGES = ["Python", "JavaScript"]
"""
