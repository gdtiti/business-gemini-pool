# 部署方案总结

## 🎯 项目概述

Business Gemini Pool 现已完全支持通过环境变量配置，并具备完整的 CI/CD 流水线，可以自动构建和推送到 GitHub Container Registry。

## 📋 部署方案对比

| 部署方式 | 优势 | 适用场景 | 配置复杂度 |
|----------|------|----------|------------|
| **本地开发** | 快速调试，完全控制 | 开发测试 | 低 |
| **Docker 部署** | 环境一致，易于扩展 | 生产环境 | 中 |
| **HuggingFace Space** | 免费托管，自动部署 | 原型演示 | 低 |
| **GitHub Container Registry** | 自动化 CI/CD，多平台 | 企业部署 | 中 |

## 🚀 快速部署选择

### 1. 原型验证 → HuggingFace Space

```bash
# 1. Fork 项目到 GitHub
# 2. 创建 HuggingFace Space
# 3. 在 Space 设置中配置环境变量
ACCOUNTS_CONFIG='[{"team_id":"your-team-id","secure_c_ses":"your-ses","host_c_oses":"your-oses","csesidx":"your-csesidx","available":true}]'

# 4. 启动即可使用
```

### 2. 生产部署 → GitHub Container Registry

```bash
# 1. 推送代码到 GitHub（自动触发 CI/CD）
git push origin main

# 2. 部署镜像
docker run -d \
  --name business-gemini-pool \
  --restart unless-stopped \
  -p 8000:8000 \
  -e ACCOUNTS_CONFIG='[{"team_id":"your-team-id","secure_c_ses":"your-ses","host_c_oses":"your-oses","csesidx":"your-csesidx","available":true}]' \
  ghcr.io/your-username/business-gemini-pool:latest
```

### 3. 自建部署 → Docker Compose

```bash
# 1. 克隆项目
git clone https://github.com/your-username/business-gemini-pool.git
cd business-gemini-pool

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 启动服务
docker-compose up -d
```

## ⚙️ 环境变量配置模板

### 最小配置（必需）

```bash
# 账号配置（必需）
ACCOUNTS_CONFIG='[{"team_id":"your-team-id","secure_c_ses":"your-secure-ses","host_c_oses":"your-host-oses","csesidx":"your-csesidx","user_agent":"Mozilla/5.0...","available":true}]'
```

### 完整配置（推荐）

```bash
# 账号配置（必需）
ACCOUNTS_CONFIG='[{"team_id":"your-team-id","secure_c_ses":"your-secure-ses","host_c_oses":"your-host-oses","csesidx":"your-csesidx","user_agent":"Mozilla/5.0...","available":true}]'

# 代理配置（可选）
PROXY_URL=http://your-proxy:port

# 图片服务配置（可选）
IMAGE_BASE_URL=https://your-domain.com/

# 模型配置（可选）
MODELS_CONFIG='[{"id":"gemini-enterprise","name":"Gemini Enterprise","description":"Google Gemini Enterprise 模型","context_length":32768,"max_tokens":8192,"enabled":true}]'
```

## 🏗️ CI/CD 流水线特性

### 自动触发条件

- ✅ `main` 分支推送 → 生产构建
- ✅ `develop` 分支推送 → 开发构建
- ✅ 版本标签推送 → 版本构建
- ✅ Pull Request → 测试构建

### 构建阶段

1. **代码验证**
   - Python 语法检查
   - 导入测试
   - 环境变量加载测试

2. **多平台构建**
   - linux/amd64 (标准服务器)
   - linux/arm64 (ARM 架构)

3. **安全扫描**
   - Trivy 漏洞扫描
   - GitHub Security 集成

4. **自动推送**
   - GitHub Container Registry
   - 多架构标签管理

### 镜像标签策略

```yaml
tags:
  main 分支:     ghcr.io/user/repo:latest
  develop 分支:  ghcr.io/user/repo:develop-{commit}
  版本标签:      ghcr.io/user/repo:v1.0.0
  提交标签:      ghcr.io/user/repo:{branch}-{commit}
```

## 🔧 故障排除速查

### 环境变量问题

```bash
# 检查环境变量加载
docker run --rm \
  -e ACCOUNTS_CONFIG='[{"team_id":"test","secure_c_ses":"test","host_c_oses":"test","csesidx":"test","available":true}]' \
  ghcr.io/your-username/business-gemini-pool:latest \
  python -c "
from gemini import load_config_from_env
config = load_config_from_env()
print(f'加载账号数: {len(config[\"accounts\"])}')
print('环境变量配置正常')
"
```

### Docker 部署问题

```bash
# 检查容器状态
docker ps
docker logs business-gemini-pool

# 检查健康状态
curl http://localhost:8000/health
curl http://localhost:8000/v1/status
```

### CI/CD 问题

- 查看构建日志: GitHub Actions 页面
- 检查权限设置: Repository Settings > Actions
- 验证环境变量: Repository Settings > Secrets

## 📊 性能建议

### 生产环境优化

```yaml
# Docker Compose 生产配置
version: '3.8'
services:
  app:
    image: ghcr.io/your-username/business-gemini-pool:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ACCOUNTS_CONFIG=${ACCOUNTS_CONFIG}
      - PROXY_URL=${PROXY_URL}
    resources:
      limits:
        memory: 512M
        cpus: '0.5'
      reservations:
        memory: 256M
        cpus: '0.25'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 高可用部署

```bash
# 多实例部署
docker run -d --name gemini-1 -p 8001:8000 -e ACCOUNTS_CONFIG='...' ghcr.io/your-username/business-gemini-pool:latest
docker run -d --name gemini-2 -p 8002:8000 -e ACCOUNTS_CONFIG='...' ghcr.io/your-username/business-gemini-pool:latest
docker run -d --name gemini-3 -p 8003:8000 -e ACCOUNTS_CONFIG='...' ghcr.io/your-username/business-gemini-pool:latest

# 使用负载均衡器（如 Nginx）
```

## 🔒 安全最佳实践

### 环境变量安全

1. **使用 Secrets 管理器**
   - GitHub Repository Secrets
   - HashiCorp Vault
   - AWS Secrets Manager

2. **最小权限原则**
   ```yaml
   permissions:
     contents: read
     packages: write
     security-events: write
   ```

3. **定期轮换密钥**
   - 每季度更新访问令牌
   - 使用短期有效的凭证

### 网络安全

```bash
# 使用网络隔离
docker network create gemini-net
docker run --network gemini-net --name gemini-app ...

# 防火墙规则（仅开放必要端口）
# 仅开放 8000 端口
```

## 📈 监控和日志

### 应用监控

```bash
# 健康检查端点
GET /health          # 基础健康检查
GET /v1/status       # 详细状态信息
```

### 日志收集

```bash
# 应用日志
docker logs -f business-gemini-pool

# 结构化日志（推荐）
# 应用日志包含时间戳、级别、消息等结构化信息
```

### 监控指标

- 账号可用性
- API 响应时间
- 错误率统计
- 资源使用情况

## 🆘 获取帮助

### 文档资源

- [项目 README](../README.md)
- [CI/CD 详细指南](ci-cd.md)
- [GitHub Secrets 配置](github-secrets.md)
- [贡献指南](../CONTRIBUTING.md)

### 社区支持

- GitHub Issues: 报告问题和功能建议
- GitHub Discussions: 一般讨论和问答
- Pull Requests: 代码贡献

### 联系方式

- 项目维护者: [your-username](https://github.com/your-username)
- 问题报告: [创建 Issue](https://github.com/your-username/business-gemini-pool/issues)

---

**🎉 恭喜！您的 Business Gemini Pool 现在已具备完整的容器化和自动化部署能力！**