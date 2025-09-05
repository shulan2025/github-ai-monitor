#!/usr/bin/env python3
"""
项目运行入口脚本
提供交互式菜单来运行不同的功能
"""

import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """打印项目横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    GitHub AI 仓库爬虫                         ║
║                                                              ║
║   🤖 自动收集 GitHub 上最新的 AI 项目                         ║
║   📊 同步数据到 Cloudflare D1 数据库                        ║
║   ⏰ 支持定时任务自动化运行                                   ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import requests
        import cloudflare
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件是否存在"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env 文件不存在")
        print("请复制 env_template.txt 为 .env 并填入你的 API 凭证")
        return False
    return True

def run_script(script_name, description):
    """运行 Python 脚本"""
    print(f"\n🚀 {description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print(f"\n✅ {description}完成!")
        else:
            print(f"\n❌ {description}失败 (退出码: {result.returncode})")
            
    except Exception as e:
        print(f"\n❌ 运行 {script_name} 时出错: {e}")
    
    input("\n按回车键继续...")

def show_logs():
    """显示日志文件"""
    log_path = Path("logs/sync.log")
    
    if not log_path.exists():
        print("❌ 日志文件不存在，请先运行同步脚本")
        input("按回车键继续...")
        return
    
    print("\n📄 最新日志内容 (最后20行):")
    print("-" * 50)
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-20:]:
                print(line.rstrip())
    except Exception as e:
        print(f"读取日志文件时出错: {e}")
    
    input("\n按回车键继续...")

def show_menu():
    """显示主菜单"""
    menu = """
📋 请选择要执行的操作:

1. 🧪 测试配置 (验证 API 凭证和依赖)
2. 🚀 运行数据同步 (获取 GitHub 数据并同步到 D1)
3. ⏰ 设置定时任务 (配置自动化运行)
4. 📄 查看运行日志 (查看最近的同步记录)
5. 📊 查看项目统计 (数据库中的仓库统计)
6. 🔧 重新安装依赖
7. ❓ 查看帮助文档
8. 🚪 退出

"""
    print(menu)

def install_dependencies():
    """安装依赖包"""
    print("\n📦 正在安装依赖包...")
    print("-" * 50)
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ 依赖包安装完成!")
        else:
            print(f"\n❌ 依赖包安装失败 (退出码: {result.returncode})")
            
    except Exception as e:
        print(f"\n❌ 安装依赖包时出错: {e}")
    
    input("\n按回车键继续...")

def show_help():
    """显示帮助信息"""
    help_text = """
📖 GitHub AI 仓库爬虫 - 使用指南

🎯 项目功能:
- 自动搜索 GitHub 上的 AI/LLM/机器学习相关仓库
- 筛选高星标(>100)的优质项目
- 将数据同步到 Cloudflare D1 数据库
- 支持定时任务自动化运行

📋 使用步骤:
1. 首先运行"测试配置"确保所有 API 凭证正确
2. 运行"数据同步"开始收集数据
3. 设置"定时任务"实现自动化运行
4. 定期查看"运行日志"监控同步状态

🔧 配置要求:
- GitHub Personal Access Token
- Cloudflare API Token
- Cloudflare Account ID  
- D1 Database ID

📁 重要文件:
- .env: 环境变量配置文件
- sync_d1.py: 主要同步脚本
- create_table.sql: 数据库表结构
- logs/sync.log: 运行日志

💡 故障排除:
- 如果 API 调用失败，检查 Token 是否有效
- 如果数据库连接失败，检查 Account ID 和 Database ID
- 查看日志文件获取详细错误信息

🌐 相关链接:
- GitHub Token: https://github.com/settings/tokens
- Cloudflare Dashboard: https://dash.cloudflare.com/
- 项目文档: README.md
"""
    print(help_text)
    input("\n按回车键继续...")

def show_stats():
    """显示数据库统计信息"""
    print("\n📊 正在查询数据库统计信息...")
    print("-" * 50)
    
    # 这里可以添加查询 D1 数据库的代码
    # 暂时显示提示信息
    print("💡 要查看详细统计信息，请在 Cloudflare D1 控制台中运行以下查询:")
    print()
    print("-- 仓库总数")
    print("SELECT COUNT(*) as total_repos FROM repos;")
    print()
    print("-- 按所有者分组的仓库数量")
    print("SELECT owner, COUNT(*) as repo_count FROM repos GROUP BY owner ORDER BY repo_count DESC LIMIT 10;")
    print()
    print("-- 最高星标的仓库")
    print("SELECT name, owner, stars, description FROM repos ORDER BY stars DESC LIMIT 10;")
    print()
    print("-- 最近同步的数据")
    print("SELECT name, owner, stars, sync_time FROM repos ORDER BY sync_time DESC LIMIT 10;")
    
    input("\n按回车键继续...")

def main():
    """主函数"""
    while True:
        clear_screen()
        print_banner()
        
        # 预检查
        if not check_dependencies():
            print("\n⚠️ 请先安装依赖包")
            input("按回车键继续...")
            continue
            
        if not check_env_file():
            print("\n⚠️ 请先配置环境变量文件")
            input("按回车键继续...")
            continue
        
        show_menu()
        
        try:
            choice = input("请输入选项 (1-8): ").strip()
            
            if choice == '1':
                run_script("test_config.py", "测试配置")
            elif choice == '2':
                run_script("sync_d1.py", "运行数据同步")
            elif choice == '3':
                run_script("setup_scheduler.py", "设置定时任务")
            elif choice == '4':
                show_logs()
            elif choice == '5':
                show_stats()
            elif choice == '6':
                install_dependencies()
            elif choice == '7':
                show_help()
            elif choice == '8':
                print("\n👋 感谢使用 GitHub AI 仓库爬虫!")
                break
            else:
                print("\n❌ 无效的选项，请输入 1-8")
                input("按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用 GitHub AI 仓库爬虫!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()
