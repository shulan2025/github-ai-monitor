#!/usr/bin/env python3
"""
定时任务设置脚本
帮助用户在不同操作系统上设置定时任务
"""

import os
import sys
import platform
from pathlib import Path

def get_project_path():
    """获取项目绝对路径"""
    return Path(__file__).parent.absolute()

def get_python_executable():
    """获取 Python 可执行文件路径"""
    return sys.executable

def setup_cron_linux_mac():
    """为 Linux/macOS 设置 cron 任务"""
    project_path = get_project_path()
    python_path = get_python_executable()
    script_path = project_path / "sync_d1.py"
    log_path = project_path / "logs"
    
    # 创建日志目录
    log_path.mkdir(exist_ok=True)
    
    cron_command = f"0 2 * * * cd {project_path} && {python_path} {script_path} >> {log_path}/sync.log 2>&1"
    
    print("🐧 Linux/macOS 定时任务设置")
    print("="*50)
    print("请按以下步骤设置 cron 定时任务：")
    print("\n1. 打开终端并运行以下命令编辑 crontab：")
    print("   crontab -e")
    print("\n2. 在文件末尾添加以下行（每天凌晨2点执行）：")
    print(f"   {cron_command}")
    print("\n3. 保存并退出编辑器")
    print("\n4. 验证 cron 任务已添加：")
    print("   crontab -l")
    
    print(f"\n📁 日志文件将保存在: {log_path}/sync.log")
    print("💡 你可以通过 'tail -f logs/sync.log' 实时查看日志")
    
    # 创建便捷脚本
    convenience_script = project_path / "add_cron.sh"
    with open(convenience_script, 'w') as f:
        f.write(f"""#!/bin/bash
# 自动添加 cron 任务的便捷脚本

echo "正在添加 cron 任务..."
(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron 任务添加成功!"
    echo "当前的 cron 任务："
    crontab -l
else
    echo "❌ Cron 任务添加失败"
fi
""")
    
    # 设置执行权限
    os.chmod(convenience_script, 0o755)
    print(f"\n🚀 便捷脚本已创建: {convenience_script}")
    print("你可以直接运行 './add_cron.sh' 来自动添加 cron 任务")

def setup_task_scheduler_windows():
    """为 Windows 设置任务计划程序"""
    project_path = get_project_path()
    python_path = get_python_executable()
    script_path = project_path / "sync_d1.py"
    
    print("🪟 Windows 定时任务设置")
    print("="*50)
    print("请按以下步骤在任务计划程序中设置定时任务：")
    print("\n1. 打开\"任务计划程序\"：")
    print("   - 按 Win+R，输入 taskschd.msc，回车")
    print("\n2. 创建基本任务：")
    print("   - 在右侧点击\"创建基本任务\"")
    print("   - 名称：GitHub AI 仓库同步")
    print("   - 描述：每日自动同步 GitHub AI 仓库到 D1 数据库")
    print("\n3. 设置触发器：")
    print("   - 选择\"每天\"")
    print("   - 开始时间：02:00:00（凌晨2点）")
    print("   - 重复间隔：1 天")
    print("\n4. 设置操作：")
    print("   - 选择\"启动程序\"")
    print(f"   - 程序/脚本：{python_path}")
    print(f"   - 添加参数：{script_path}")
    print(f"   - 起始于：{project_path}")
    print("\n5. 完成设置并测试运行")
    
    # 创建批处理脚本
    batch_script = project_path / "sync_github.bat"
    log_path = project_path / "logs"
    log_path.mkdir(exist_ok=True)
    
    with open(batch_script, 'w') as f:
        f.write(f"""@echo off
cd /d "{project_path}"
"{python_path}" "{script_path}" >> logs\\sync.log 2>&1
""")
    
    print(f"\n📁 批处理脚本已创建: {batch_script}")
    print("你也可以在任务计划程序中直接运行这个批处理文件")
    print(f"📄 日志文件将保存在: {log_path}\\sync.log")

def setup_launchd_mac():
    """为 macOS 设置 LaunchAgent（推荐方式）"""
    project_path = get_project_path()
    python_path = get_python_executable()
    script_path = project_path / "sync_d1.py"
    
    # LaunchAgent plist 文件路径
    plist_path = Path.home() / "Library/LaunchAgents/com.github.ai.sync.plist"
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.ai.sync</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{project_path}</string>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>{project_path}/logs/sync.log</string>
    
    <key>StandardErrorPath</key>
    <string>{project_path}/logs/sync_error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>"""

    print("🍎 macOS LaunchAgent 设置（推荐）")
    print("="*50)
    
    # 创建日志目录
    log_path = project_path / "logs"
    log_path.mkdir(exist_ok=True)
    
    # 创建 plist 文件
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    print(f"✅ LaunchAgent 配置文件已创建: {plist_path}")
    
    print("\n请运行以下命令来加载和启动服务：")
    print(f"launchctl load {plist_path}")
    print(f"launchctl start com.github.ai.sync")
    
    print("\n管理命令：")
    print("- 查看状态：launchctl list | grep com.github.ai.sync")
    print("- 停止服务：launchctl stop com.github.ai.sync")
    print("- 卸载服务：launchctl unload " + str(plist_path))
    
    print(f"\n📄 日志文件：")
    print(f"- 标准输出：{project_path}/logs/sync.log")
    print(f"- 错误日志：{project_path}/logs/sync_error.log")
    
    # 创建便捷管理脚本
    management_script = project_path / "manage_launchd.sh"
    with open(management_script, 'w') as f:
        f.write(f"""#!/bin/bash
# LaunchAgent 管理脚本

PLIST_PATH="{plist_path}"
SERVICE_NAME="com.github.ai.sync"

case "$1" in
    start)
        echo "启动服务..."
        launchctl load "$PLIST_PATH"
        launchctl start "$SERVICE_NAME"
        ;;
    stop)
        echo "停止服务..."
        launchctl stop "$SERVICE_NAME"
        launchctl unload "$PLIST_PATH"
        ;;
    status)
        echo "服务状态："
        launchctl list | grep "$SERVICE_NAME"
        ;;
    logs)
        echo "查看日志："
        tail -f "{project_path}/logs/sync.log"
        ;;
    *)
        echo "用法: $0 {{start|stop|status|logs}}"
        exit 1
        ;;
esac
""")
    
    os.chmod(management_script, 0o755)
    print(f"\n🛠️ 管理脚本已创建: {management_script}")
    print("使用方法：")
    print("- ./manage_launchd.sh start   # 启动服务")
    print("- ./manage_launchd.sh stop    # 停止服务")
    print("- ./manage_launchd.sh status  # 查看状态")
    print("- ./manage_launchd.sh logs    # 查看日志")

def main():
    """主函数"""
    print("⏰ 定时任务设置助手")
    print("="*50)
    
    system = platform.system().lower()
    print(f"检测到操作系统: {platform.system()}")
    
    if system in ['linux']:
        setup_cron_linux_mac()
    elif system == 'darwin':  # macOS
        print("\nmacOS 用户可以选择以下两种方式：")
        print("1. LaunchAgent（推荐）- 更稳定和功能丰富")
        print("2. Cron - 简单传统")
        
        choice = input("\n请选择 (1/2) [默认:1]: ").strip() or "1"
        
        if choice == "1":
            setup_launchd_mac()
        else:
            setup_cron_linux_mac()
            
    elif system == 'windows':
        setup_task_scheduler_windows()
    else:
        print(f"❌ 不支持的操作系统: {system}")
        print("请手动设置定时任务运行 sync_d1.py")
        return
    
    print("\n" + "="*50)
    print("📝 重要提醒：")
    print("1. 确保 .env 文件已正确配置所有环境变量")
    print("2. 建议先手动运行 python sync_d1.py 测试")
    print("3. 运行 python test_config.py 验证配置")
    print("4. 定期检查日志文件确保任务正常运行")
    print("="*50)

if __name__ == "__main__":
    main()
