#!/usr/bin/env python3
"""
基于时间的去重配置
实现30天内不重复，30天后可重新收录的逻辑
"""

from datetime import datetime, timedelta

# ================================
# 📅 时间去重配置
# ================================

TIME_DEDUP_CONFIG = {
    # 去重时间窗口
    "dedup_window_days": 30,        # 30天内不重复
    
    # 重新收录条件
    "reentry_conditions": {
        "min_days_since_last": 30,  # 距离上次收录至少30天
        "activity_required": True,   # 需要有新的活动
        "star_growth_threshold": 10, # 星标增长至少10个
        "update_time_check": True    # 检查是否有新的推送
    },
    
    # 质量提升门槛 (重新收录时的更高要求)
    "reentry_quality_boost": {
        "min_score_increase": 5,     # 评分至少提升5分
        "category_change_bonus": 3,  # 分类变化额外加分
        "new_tech_tags_bonus": 2     # 新技术标签加分
    }
}

# ================================
# 🔄 时间去重SQL语句
# ================================

def get_time_dedup_sql():
    """获取基于时间的去重SQL语句"""
    
    # 检查30天内是否已存在的SQL
    check_existing_sql = """
    SELECT id, sync_time, stars, relevance_score, category
    FROM repos 
    WHERE id = ? 
      AND sync_time >= datetime('now', '-30 days')
    ORDER BY sync_time DESC 
    LIMIT 1
    """
    
    # 插入新记录的SQL (带时间标识)
    insert_with_time_sql = """
    INSERT INTO repos (
        id, name, owner, stars, forks, description, url, 
        created_at, updated_at, category, tags, summary, 
        relevance_score, sync_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """
    
    # 更新现有记录的SQL
    update_existing_sql = """
    UPDATE repos SET
        stars = ?,
        updated_at = ?,
        category = ?,
        tags = ?,
        summary = ?,
        relevance_score = ?,
        sync_time = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    
    return {
        "check_existing": check_existing_sql,
        "insert_new": insert_with_time_sql,
        "update_existing": update_existing_sql
    }

# ================================
# 🎯 重新收录评估函数
# ================================

def should_reentry_repo(existing_record, new_data):
    """
    判断是否应该重新收录项目
    
    Args:
        existing_record: 数据库中的现有记录
        new_data: 新获取的项目数据
    
    Returns:
        tuple: (should_reentry, reason, action)
    """
    
    if not existing_record:
        return True, "新项目", "insert"
    
    # 检查时间间隔
    last_sync = datetime.fromisoformat(existing_record['sync_time'])
    days_since_last = (datetime.now() - last_sync).days
    
    if days_since_last < TIME_DEDUP_CONFIG["dedup_window_days"]:
        # 30天内，检查是否需要更新
        return should_update_recent_record(existing_record, new_data)
    
    # 超过30天，检查重新收录条件
    return evaluate_reentry_conditions(existing_record, new_data)

def should_update_recent_record(existing_record, new_data):
    """检查是否需要更新30天内的记录"""
    
    old_stars = existing_record.get('stars', 0)
    new_stars = new_data.get('stargazers_count', 0)
    
    # 显著的星标增长
    if new_stars - old_stars >= 50:
        return True, "星标显著增长", "update"
    
    # 分类发生变化
    # (这里需要重新计算新数据的分类)
    
    # 评分显著提升
    # (这里需要重新计算新数据的评分)
    
    return False, "30天内无显著变化", "skip"

def evaluate_reentry_conditions(existing_record, new_data):
    """评估30天后的重新收录条件"""
    
    conditions = TIME_DEDUP_CONFIG["reentry_conditions"]
    reasons = []
    
    # 1. 检查活跃度
    if conditions["activity_required"]:
        last_update = existing_record.get('updated_at', '')
        new_update = new_data.get('pushed_at', '')
        
        if new_update and new_update > last_update:
            reasons.append("项目有新活动")
        elif conditions["activity_required"]:
            return False, "项目无新活动", "skip"
    
    # 2. 检查星标增长
    old_stars = existing_record.get('stars', 0)
    new_stars = new_data.get('stargazers_count', 0)
    star_growth = new_stars - old_stars
    
    if star_growth >= conditions["star_growth_threshold"]:
        reasons.append(f"星标增长{star_growth}个")
    
    # 3. 检查质量提升
    # (这里需要重新计算评分)
    
    if len(reasons) >= 1:  # 至少满足一个条件
        return True, f"重新收录: {', '.join(reasons)}", "reinsert"
    
    return False, "不满足重新收录条件", "skip"

# ================================
# 📊 时间去重统计
# ================================

def get_time_dedup_stats_sql():
    """获取时间去重统计的SQL语句"""
    
    stats_queries = {
        # 30天内的记录数
        "recent_records": """
        SELECT COUNT(*) as count 
        FROM repos 
        WHERE sync_time >= datetime('now', '-30 days')
        """,
        
        # 重复检查统计
        "duplicate_check": """
        SELECT 
            DATE(sync_time) as sync_date,
            COUNT(*) as daily_count
        FROM repos 
        WHERE sync_time >= datetime('now', '-30 days')
        GROUP BY DATE(sync_time)
        ORDER BY sync_date DESC
        """,
        
        # 项目活跃度分布
        "activity_distribution": """
        SELECT 
            CASE 
                WHEN updated_at >= datetime('now', '-7 days') THEN '极活跃(7天)'
                WHEN updated_at >= datetime('now', '-30 days') THEN '活跃(30天)'
                WHEN updated_at >= datetime('now', '-90 days') THEN '中等(90天)'
                ELSE '不活跃'
            END as activity_level,
            COUNT(*) as count
        FROM repos 
        GROUP BY activity_level
        """
    }
    
    return stats_queries

# ================================
# 💡 使用示例
# ================================

USAGE_EXAMPLE = """
🎯 时间去重机制使用示例:

1. 首次发现项目:
   - 项目A在第1天被发现并收录
   - 状态: 新项目，直接插入

2. 30天内再次遇到:
   - 第15天再次遇到项目A
   - 检查: 是否有显著变化 (星标+50, 分类变化等)
   - 动作: 有显著变化则更新，否则跳过

3. 30天后再次遇到:
   - 第35天再次遇到项目A  
   - 检查: 是否满足重新收录条件
   - 条件: 有新活动 + 星标增长 + 质量提升
   - 动作: 满足条件则重新插入新记录

4. 数据库状态:
   - 项目A可能有多条记录，代表不同时期的状态
   - 每条记录间隔至少30天
   - 记录了项目的发展历程

优势:
✅ 避免30天内的重复收录
✅ 捕获项目的重要发展节点  
✅ 保持数据的时效性
✅ 记录项目发展轨迹
"""

if __name__ == "__main__":
    print("📅 时间去重配置加载完成")
    print(f"🔄 去重窗口: {TIME_DEDUP_CONFIG['dedup_window_days']} 天")
    print("📊 重新收录条件已配置")
    print("\n" + USAGE_EXAMPLE)
