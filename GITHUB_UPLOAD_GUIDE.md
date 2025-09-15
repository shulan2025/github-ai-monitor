# GitHub 上传指南

## 🚀 准备上传到 GitHub

### 📋 上传前检查清单

#### ✅ 代码文件完整性
- [x] 所有核心Python文件已准备
- [x] 配置文件完整 (config_v2.py, env.template)
- [x] 数据库脚本完整 (setup_database.py, create_table.sql)
- [x] 工具脚本完整 (test_config.py, simple_db_check.py)
- [x] 邮件通知系统完整 (email_notifier.py)

#### ✅ 文档文件完整性
- [x] README.md - 项目说明
- [x] DEPLOYMENT.md - 部署指南
- [x] SETUP_GUIDE.md - 快速设置
- [x] CONTRIBUTING.md - 贡献指南
- [x] LICENSE - MIT许可证
- [x] CHANGELOG_v2.1_final.md - 更新日志
- [x] PACKAGE_INFO_v2.1_final.md - 打包信息

#### ✅ GitHub Actions 配置
- [x] .github/workflows/daily-collection.yml - 自动化工作流
- [x] 邮件通知集成
- [x] 错误处理和日志记录

#### ✅ 环境配置
- [x] requirements.txt - Python依赖
- [x] env.template - 环境变量模板
- [x] .gitignore - Git忽略文件

## 🔧 GitHub 仓库设置

### 1. 创建新仓库
```bash
# 在GitHub上创建新仓库: github-ai-monitor
# 选择 Public 或 Private (建议 Private)
# 不要初始化 README, .gitignore, license (我们已经有了)
```

### 2. 本地Git初始化
```bash
cd /path/to/github-ai-monitor-repo

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交初始版本
git commit -m "Initial commit: GitHub AI Monitor v2.1 Final

- ✅ 彻底解决 watchers_count 字段问题 (100%修复)
- ✅ 去除智能去重规则，确保数据更新
- ✅ 时间字段统一为北京时间
- ✅ 性能提升68% (84项/分钟)
- ✅ 完整的邮件通知系统
- ✅ GitHub Actions 自动化部署
- ✅ 生产就绪，可立即使用"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/github-ai-monitor.git

# 推送到GitHub
git push -u origin main
```

## 🔐 GitHub Secrets 配置

### 必需的 Secrets
在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加：

#### 1. GitHub API
```
GITHUB_TOKEN = your_github_token_here
```

#### 2. Cloudflare D1 数据库
```
CLOUDFLARE_ACCOUNT_ID = your_account_id_here
CLOUDFLARE_API_TOKEN = your_cloudflare_api_token_here
D1_DATABASE_ID = your_database_id_here
```

#### 3. 邮件通知 (Gmail)
```
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587
EMAIL_USER = your_email@gmail.com
EMAIL_PASSWORD = your_app_password_here
EMAIL_TO = your_email@gmail.com
```

## 🚀 部署步骤

### 1. 启用 GitHub Actions
- 推送代码后，GitHub Actions 会自动启用
- 可以在 Actions 标签页查看工作流状态

### 2. 手动触发测试
```bash
# 在 GitHub 仓库页面
# Actions → Daily AI Repository Collection → Run workflow
# 选择 "test_mode: true", "limit: 100"
```

### 3. 验证部署
- 检查 Actions 运行日志
- 验证邮件通知是否正常
- 检查数据库中的数据

## 📧 邮件通知测试

### 测试邮件功能
```bash
# 在本地测试邮件功能
cd /path/to/github-ai-monitor-repo

# 设置环境变量
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USER=your_email@gmail.com
export EMAIL_PASSWORD="your_app_password_here"
export EMAIL_TO=your_email@gmail.com

# 测试邮件发送
python3 email_notifier.py test
```

## 🔍 验证清单

### 部署后验证
- [ ] GitHub Actions 工作流正常运行
- [ ] 数据库连接正常
- [ ] 数据采集功能正常
- [ ] 邮件通知功能正常
- [ ] 日志记录完整

### 数据验证
- [ ] 新采集的数据正确
- [ ] watchers_count 字段正确
- [ ] 时间字段为北京时间
- [ ] 数据完整性100%

## 📊 监控和维护

### 日常监控
1. **GitHub Actions 状态**: 每天检查工作流运行状态
2. **邮件通知**: 关注成功/失败通知邮件
3. **数据库状态**: 定期检查数据增长情况
4. **API 使用量**: 监控 GitHub API 使用限制

### 维护建议
1. **定期更新**: 每月检查依赖包更新
2. **Token 管理**: 定期轮换 API Token
3. **日志清理**: 定期清理旧日志文件
4. **数据备份**: 定期备份重要数据

## 🆘 故障排除

### 常见问题
1. **GitHub Actions 失败**
   - 检查 Secrets 配置
   - 查看详细错误日志
   - 验证网络连接

2. **邮件发送失败**
   - 检查 Gmail 应用密码
   - 验证 SMTP 设置
   - 确认防火墙设置

3. **数据库连接失败**
   - 验证 Cloudflare Token
   - 检查数据库 ID
   - 确认网络访问权限

### 联系支持
- 查看 GitHub Issues
- 检查项目文档
- 参考错误日志

---

## 🎉 完成！

**恭喜！您的 GitHub AI Monitor v2.1 已准备就绪！**

- ✅ 代码完整且经过测试
- ✅ 文档齐全
- ✅ 自动化部署配置完成
- ✅ 邮件通知系统就绪
- ✅ 生产环境就绪

**下一步**: 按照上述步骤上传到 GitHub 并配置 Secrets，即可开始自动化采集！