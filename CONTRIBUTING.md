# 贡献指南

感谢您对 GitHub AI Monitor 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 1. Fork 项目

1. 点击项目页面右上角的 "Fork" 按钮
2. 将 Fork 的仓库克隆到本地：
   ```bash
   git clone https://github.com/your-username/github-ai-monitor.git
   cd github-ai-monitor
   ```

### 2. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或者
git checkout -b fix/your-bug-fix
```

### 3. 开发环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量模板
cp env.template .env

# 编辑 .env 文件，填入必要的配置
```

### 4. 进行开发

- 遵循项目的代码风格
- 添加必要的测试
- 更新相关文档
- 确保代码通过所有测试

### 5. 提交更改

```bash
git add .
git commit -m "feat: 添加新功能描述"
# 或者
git commit -m "fix: 修复问题描述"
```

### 6. 推送并创建 Pull Request

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 📝 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: 添加新的 AI 关键词分类
fix: 修复数据库连接超时问题
docs: 更新 README 安装说明
```

## 🧪 测试

在提交代码前，请确保：

1. **配置测试**：
   ```bash
   python3 test_config.py
   ```

2. **数据库测试**：
   ```bash
   python3 simple_db_check.py
   ```

3. **小规模采集测试**：
   ```bash
   python3 optimized_fast_collector.py --test --limit 10
   ```

## 📋 代码规范

### Python 代码风格

- 使用 4 个空格缩进
- 行长度不超过 120 字符
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串

### 文件组织

```
github-ai-monitor/
├── .github/workflows/     # GitHub Actions 工作流
├── config_v2.py          # 配置文件
├── optimized_fast_collector.py  # 主采集器
├── data_processor.py     # 数据处理器
├── deduplication_manager.py  # 去重管理器
├── enhanced_data_processor.py  # 增强数据处理器
├── simple_db_check.py    # 数据库检查工具
├── setup_database.py     # 数据库初始化
├── requirements.txt      # 依赖列表
├── README.md            # 项目说明
└── LICENSE              # 许可证
```

## 🐛 报告问题

如果您发现了 bug 或有功能建议，请：

1. 检查 [Issues](https://github.com/your-username/github-ai-monitor/issues) 是否已有相关问题
2. 如果没有，请创建新的 Issue
3. 提供详细的问题描述和复现步骤

### Issue 模板

```markdown
**问题描述**
简要描述遇到的问题

**复现步骤**
1. 执行命令 '...'
2. 点击 '...'
3. 看到错误

**预期行为**
描述您期望的行为

**实际行为**
描述实际发生的情况

**环境信息**
- 操作系统: [e.g. Ubuntu 20.04]
- Python 版本: [e.g. 3.9.7]
- 项目版本: [e.g. v2.1]

**日志信息**
如果有错误日志，请贴出相关部分
```

## 💡 功能建议

我们欢迎新功能建议！请：

1. 在 [Discussions](https://github.com/your-username/github-ai-monitor/discussions) 中提出想法
2. 详细描述功能需求和预期效果
3. 考虑实现的复杂度和影响范围

## 📚 文档贡献

文档改进同样重要：

- 修复文档中的错误
- 添加使用示例
- 改进说明的清晰度
- 翻译文档到其他语言

## 🏷️ 标签说明

我们使用以下标签来组织 Issues 和 PR：

- `bug` - 错误报告
- `enhancement` - 功能增强
- `documentation` - 文档相关
- `good first issue` - 适合新手的任务
- `help wanted` - 需要帮助的任务
- `question` - 问题讨论

## 🎯 开发路线图

当前我们关注的重点：

- [ ] 提高采集性能
- [ ] 增加更多数据源
- [ ] 改进数据分析功能
- [ ] 优化用户界面
- [ ] 增加监控和告警功能

## 📞 联系方式

- **项目维护者**: [Your Name](https://github.com/your-username)
- **讨论区**: [GitHub Discussions](https://github.com/your-username/github-ai-monitor/discussions)
- **问题反馈**: [GitHub Issues](https://github.com/your-username/github-ai-monitor/issues)

## 🙏 致谢

感谢所有为项目做出贡献的开发者！

---

再次感谢您的贡献！🎉
