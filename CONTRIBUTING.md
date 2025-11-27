# 贡献指南

感谢您对 Business Gemini Pool 项目的关注！我们欢迎各种形式的贡献。

## 贡献方式

### 🐛 报告问题

如果您发现了问题，请：

1. 检查 [Issues](https://github.com/your-username/business-gemini-pool/issues) 是否已有相关问题
2. 如果没有，请创建新的 Issue，包含：
   - 问题描述
   - 重现步骤
   - 环境信息（操作系统、Python版本、Docker版本等）
   - 错误日志（如有）

### 💡 功能建议

欢迎提出新功能建议：

1. 在 Issues 中描述功能需求
2. 说明使用场景和预期效果
3. 讨论实现方案

### 🔧 代码贡献

#### 开发环境设置

1. **Fork 项目**
   ```bash
   git clone https://github.com/your-username/business-gemini-pool.git
   cd business-gemini-pool
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加必要的配置
   ```

#### 代码规范

- **Python**: 遵循 PEP 8 规范
- **文档**: 使用中文注释，英文变量名
- **测试**: 确保新功能有相应测试

#### 提交流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发和测试**
   - 编写代码
   - 添加测试（如需要）
   - 确保所有测试通过
   ```bash
   python -m py_compile gemini.py
   python -c "from gemini import load_config_from_env; print('Import test passed')"
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

4. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**
   - 提供清晰的 PR 描述
   - 说明更改内容和测试结果
   - 等待代码审查

### 📝 文档贡献

文档改进同样重要：

- API 文档更新
- 配置说明完善
- 使用示例补充
- 错误修复

### 🌟 其他贡献方式

- **测试**: 在不同环境中测试项目
- **反馈**: 使用后提供使用体验
- **推广**: 推荐项目给其他开发者
- **翻译**: 协助文档翻译

## 开发指南

### 项目结构

```
├── gemini.py              # 主要服务逻辑
├── app.py                 # HuggingFace 入口
├── index.html             # Web 管理界面
├── .github/workflows/     # CI/CD 配置
├── docs/                  # 项目文档
└── tests/                 # 测试文件（待添加）
```

### 核心功能

- **AccountManager**: 账号管理
- **FileManager**: 文件管理
- **环境变量配置**: 从环境变量加载配置
- **多平台 Docker**: 支持 amd64/arm64

### 开发工具

推荐的开发工具：

- **IDE**: VS Code, PyCharm
- **API 测试**: Postman, curl
- **Docker**: Docker Desktop
- **版本控制**: Git, GitHub Desktop

## 代码审查

### 审查标准

1. **功能正确性**: 代码实现符合需求
2. **代码质量**: 遵循项目编码规范
3. **安全性**: 无安全漏洞和敏感信息泄露
4. **性能**: 不影响现有性能
5. **兼容性**: 不破坏现有功能
6. **文档**: 包含必要的注释和文档

### 审查流程

1. 自动化测试通过
2. 代码审查（至少一人）
3. 安全扫描通过
4. 维护者合并

## 发布流程

### 版本管理

项目使用 [语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 发布步骤

1. **更新版本号**
   ```bash
   # 更新版本标签
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **自动化构建**
   - GitHub Actions 自动构建 Docker 镜像
   - 自动推送到 Container Registry
   - 自动运行安全扫描

3. **发布说明**
   - 更新 CHANGELOG.md
   - 创建 GitHub Release

## 社区

### 行为准则

我们致力于为每个人提供友好、安全和欢迎的环境，无论：

- 性别、性别认同和表达
- 性取向
- 残疾
- 外貌
- 身体大小
- 种族
- 年龄
- 宗教

### 沟通渠道

- **Issues**: 报告问题和功能建议
- **Discussions**: 一般讨论和问答
- **Pull Requests**: 代码贡献和审查

## 致谢

感谢所有为这个项目做出贡献的开发者！

### 主要贡献者

- [@your-username](https://github.com/your-username) - 项目创建者和维护者

### 特别感谢

- Google Gemini 团队提供强大的 API
- 开源社区提供的工具和库
- 所有测试和反馈的用户

## 许可证

通过贡献代码，您同意您的贡献将在 [MIT 许可证](LICENSE) 下发布。