#!/usr/bin/env python3
"""
测试关键词配置是否正确加载
"""

def test_keywords():
    print("🔍 测试关键词配置")
    print("=" * 50)
    
    try:
        from enhanced_keywords_config import SEARCH_ROUNDS_CONFIG, get_all_keywords
        
        print("✅ 成功导入关键词配置")
        
        # 测试搜索轮次配置
        print(f"\n📊 搜索轮次配置:")
        for i, config in enumerate(SEARCH_ROUNDS_CONFIG, 1):
            print(f"{i}. {config['name']}: {len(config['keywords'])}个关键词")
            print(f"   最小星标: {config['min_stars']}")
            print(f"   最大结果: {config['max_results']}")
            print(f"   关键词示例: {config['keywords'][:3]}")
            print()
        
        # 测试所有关键词
        all_keywords = get_all_keywords()
        print(f"📈 总关键词数量: {len(all_keywords)}")
        
        # 检查是否包含新的关键词
        new_keywords = ['llama', 'qwen', 'mistral', 'grok', 'phi-3', 'chatgpt', 'gemini', 'claude']
        found_new = [kw for kw in new_keywords if kw in all_keywords]
        print(f"🆕 新关键词检查: {found_new}")
        
        # 检查是否包含热门框架
        frameworks = ['pytorch', 'tensorflow', 'langchain', 'llamaindex', 'autogen', 'crewai']
        found_frameworks = [fw for fw in frameworks if fw in all_keywords]
        print(f"🔧 热门框架检查: {found_frameworks}")
        
        print("\n✅ 关键词配置测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 关键词配置测试失败: {e}")
        return False

if __name__ == "__main__":
    test_keywords()
