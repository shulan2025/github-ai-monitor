#!/bin/bash
# LaunchAgent 管理脚本

PLIST_PATH="/Users/momo/Library/LaunchAgents/com.github.ai.sync.plist"
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
        tail -f "/Users/momo/Desktop/github爬虫/logs/sync.log"
        ;;
    *)
        echo "用法: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac
