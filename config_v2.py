#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub AI Monitor v2.1 配置文件
功能: 系统配置和环境变量管理
"""

import os
from typing import Dict, Any

class Config:
    """系统配置类"""
    
    # API配置
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "your_github_token_here")
    CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "your_cloudflare_api_token_here")
    CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "your_account_id_here")
    D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID", "your_database_id_here")
    
    # Gmail配置
    GMAIL_EMAIL = os.environ.get("GMAIL_EMAIL", "your_email@gmail.com")
    GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "your_app_password_here")
    
    # 采集配置
    COLLECTION_FREQUENCY_HOURS = 6          # 采集频率(小时)
    TARGET_COLLECTION_SIZE = 2500           # 单次采集目标数量
    MAX_API_CALLS_PER_CYCLE = 4000         # 每周期最大API调用次数
    
    # 搜索配置
    MIN_STARS = int(os.environ.get("MIN_STARS", "100"))                    # 最小星标数
    CREATED_YEARS_BACK = int(os.environ.get("CREATED_YEARS_BACK", "10"))   # 创建时间范围(年)
    UPDATED_DAYS_BACK = int(os.environ.get("UPDATED_DAYS_BACK", "365"))    # 更新时间范围(天)
    
    # 去重配置
    DEDUP_WINDOW_DAYS = int(os.environ.get("DEDUP_WINDOW_DAYS", "7"))      # 去重窗口期(天)
    
    # 性能配置
    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "50"))                   # 批量处理大小
    MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", "5"))            # 最大并发数
    REQUEST_DELAY = float(os.environ.get("REQUEST_DELAY", "0.1"))          # 请求延迟(秒)
    
    # 日志配置
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "collection.log")
    
    # 开发配置
    DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
    VERBOSE_LOGGING = os.environ.get("VERBOSE_LOGGING", "false").lower() == "true"
    TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"
    TEST_LIMIT = int(os.environ.get("TEST_LIMIT", "100"))

class APIConfig:
    """API配置类"""
    
    # GitHub API
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_SEARCH_ENDPOINT = f"{GITHUB_API_BASE}/search/repositories"
    GITHUB_REPO_ENDPOINT = f"{GITHUB_API_BASE}/repos"
    
    # 请求头
    DEFAULT_HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-AI-Monitor/2.1"
    }
    
    # 速率限制
    RATE_LIMIT_PER_HOUR = 5000
    RATE_LIMIT_PER_MINUTE = 60

class DatabaseConfig:
    """数据库配置类"""
    
    # 表名
    TABLE_NAME = "github_ai_post_attr"
    
    # 插入SQL
    INSERT_SQL = f"""
    INSERT INTO {TABLE_NAME} (
        id, full_name, name, owner, description, url,
        stargazers_count, forks_count, watchers_count,
        created_at, updated_at, pushed_at, language,
        topics, ai_category, ai_tags, quality_score,
        trending_score, collection_round, last_fork_count,
        fork_growth, collection_hash, collection_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # 更新SQL
    UPDATE_SQL = f"""
    UPDATE {TABLE_NAME} SET
        full_name = ?, name = ?, owner = ?, description = ?, url = ?,
        stargazers_count = ?, forks_count = ?, watchers_count = ?,
        created_at = ?, updated_at = ?, pushed_at = ?, language = ?,
        topics = ?, ai_category = ?, ai_tags = ?, quality_score = ?,
        trending_score = ?, collection_round = ?, last_fork_count = ?,
        fork_growth = ?, collection_hash = ?, collection_time = ?
    WHERE id = ?
    """

    # 查询SQL
    SELECT_SQL = f"""
    SELECT id, full_name, stargazers_count, forks_count, watchers_count,
           created_at, updated_at, pushed_at, language, topics,
           ai_category, ai_tags, quality_score, trending_score,
           collection_round, last_fork_count, fork_growth,
           collection_hash, collection_time
    FROM {TABLE_NAME}
    WHERE id = ?
    """
    
    # 统计SQL
    COUNT_SQL = f"SELECT COUNT(*) as total FROM {TABLE_NAME}"

class EmailConfig:
    """邮件配置类"""
    
    # SMTP配置
    SMTP_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_USER = os.environ.get("EMAIL_USER", "your_email@gmail.com")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your_app_password_here")
    EMAIL_TO = os.environ.get("EMAIL_TO", "your_email@gmail.com")
    
    # 邮件模板
    SUCCESS_SUBJECT = "✅ GitHub AI Monitor - 采集成功"
    FAILURE_SUBJECT = "❌ GitHub AI Monitor - 采集失败"

def get_config() -> Dict[str, Any]:
    """获取配置字典"""
    config = Config()
    return {
        "github_token": config.GITHUB_TOKEN,
        "cloudflare_token": config.CLOUDFLARE_API_TOKEN,
        "cloudflare_account_id": config.CLOUDFLARE_ACCOUNT_ID,
        "d1_database_id": config.D1_DATABASE_ID,
        "gmail_email": config.GMAIL_EMAIL,
        "gmail_password": config.GMAIL_PASSWORD,
        "collection_frequency": config.COLLECTION_FREQUENCY_HOURS,
        "target_size": config.TARGET_COLLECTION_SIZE,
        "min_stars": config.MIN_STARS,
        "created_years_back": config.CREATED_YEARS_BACK,
        "updated_days_back": config.UPDATED_DAYS_BACK,
        "dedup_window": config.DEDUP_WINDOW_DAYS,
        "batch_size": config.BATCH_SIZE,
        "max_concurrent": config.MAX_CONCURRENT,
        "log_level": config.LOG_LEVEL,
        "debug_mode": config.DEBUG_MODE,
        "test_mode": config.TEST_MODE
    }

def validate_config() -> bool:
    """验证配置完整性"""
    config = Config()
    
    required_fields = [
        "GITHUB_TOKEN",
        "CLOUDFLARE_API_TOKEN", 
        "CLOUDFLARE_ACCOUNT_ID",
        "D1_DATABASE_ID"
    ]
    
    for field in required_fields:
        value = getattr(config, field)
        if not value or value.startswith("your_"):
            print(f"❌ 配置缺失: {field}")
            return False
    
    print("✅ 配置验证通过")
    return True

if __name__ == "__main__":
    # 测试配置
    print("🔧 GitHub AI Monitor v2.1 配置测试")
    print("=" * 50)
    
    config = get_config()
    for key, value in config.items():
        if "token" in key.lower() or "password" in key.lower():
            print(f"{key}: {'*' * 10}")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "=" * 50)
    validate_config()