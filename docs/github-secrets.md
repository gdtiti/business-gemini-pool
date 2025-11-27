# GitHub Secrets 配置指南

## 概述

此项目使用 GitHub Actions 进行自动化的 Docker 镜像构建和推送。大部分配置已经内置，但某些高级功能可能需要额外的 secrets 配置。

## 自动可用的 Secrets

GitHub Actions 会自动提供以下 secrets，无需手动配置：

- `GITHUB_TOKEN`: 用于认证和推送到 GitHub Container Registry
- `GITHUB_ACTOR`: 当前执行 Actions 的用户名

## 可选的 Secrets 配置

### 1. Docker Hub 配置（可选）

如果您想同时推送到 Docker Hub，可以配置以下 secrets：

```yaml
# 在 GitHub 仓库的 Settings > Secrets and variables > Actions 中设置
DOCKER_USERNAME: 您的 Docker Hub 用户名
DOCKER_PASSWORD: 您的 Docker Hub 访问令牌（不是密码）
```

### 2. 外部通知配置（可选）

#### Slack 通知
```yaml
SLACK_WEBHOOK_URL: Slack Webhook URL
```

#### Discord 通知
```yaml
DISCORD_WEBHOOK_URL: Discord Webhook URL
```

#### 企业微信通知
```yaml
WECHAT_WEBHOOK_URL: 企业微���机器人 Webhook URL
```

### 3. 镜像扫描配置（可选）

#### Trivy 配置
```yaml
TRIVY_TOKEN: Trivy 访问令牌（如果使用私有 Trivy 服务）
TRIVY_URL: 自定义 Trivy 服务 URL
```

## 安全最佳实践

### 1. 访问令牌生成

对于 Docker Hub，建议使用访问令牌而非密码：

1. 登录 Docker Hub
2. 进入 Account Settings > Security
3. 创建新的 Access Token
4. 设置适当的权限（读取、写入、删除）
5. 将令牌添加到 GitHub Secrets

### 2. 权限最小化

```yaml
# workflow 文件中的权限配置
permissions:
  contents: read          # 读取代码
  packages: write         # 推送包到 GitHub Registry
  security-events: write  # 上传安全扫描结果
  actions: read          # 读取 Actions 状态
```

### 3. 环境隔离

建议为不同环境使用不同的 secrets：

- 开发环境: `DEV_*` 前缀
- 测试环境: `TEST_*` 前缀
- 生产环境: `PROD_*` 前缀

## 配置示例

### 方法 1: 通过 GitHub Web 界面

1. 进入 GitHub 仓库
2. 点击 `Settings` 标签页
3. 在左侧菜单中选择 `Secrets and variables` > `Actions`
4. 点击 `New repository secret`
5. 输入 Name 和 Value
6. 点击 `Add secret`

### 方法 2: 使用 GitHub CLI

```bash
# 设置 Docker Hub 凭据
gh secret set DOCKER_USERNAME --body "your-docker-username"
gh secret set DOCKER_PASSWORD --body "your-docker-token"

# 设置通知 Webhook
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/..."
```

## 验证配置

### 1. 检查 Secrets
```bash
gh secret list
```

### 2. 测试工作流
```bash
# 创建测试分支
git checkout -b test-ci-setup

# 提交更改
git add .
git commit -m "test: add CI configuration"
git push origin test-ci-setup

# 查看 Actions 运行状态
gh workflow list
gh workflow view docker-build.yml
```

## 故障排除

### 常见问题

1. **权限不足错误**
   - 检查 `GITHUB_TOKEN` 是否有 `packages: write` 权限
   - 确认仓库设置为私有或公共（私有仓库需要特殊配置）

2. **Docker Hub 推送失败**
   - 验证 `DOCKER_USERNAME` 和 `DOCKER_PASSWORD` 是否正确
   - 检查 Docker Hub 仓库是否存在

3. **多平台构建失败**
   - 确保使用了正确的 Docker Buildx 配置
   - 检查 GitHub Actions 运行器是否支持多平台构建

### 调试技巧

1. **启用调试日志**
```yaml
- name: Debug information
  run: |
    echo "Registry: ${{ env.REGISTRY }}"
    echo "Image: ${{ env.IMAGE_NAME }}"
    echo "Actor: ${{ github.actor }}"
    docker version
    buildx version
```

2. **查看详细日志**
在 GitHub Actions 页面中点击具体的 job 查看详细输出日志。

3. **本地测试**
```bash
# 本地测试构建
docker buildx build --platform linux/amd64,linux/arm64 .

# 本地测试推送
docker buildx build --platform linux/amd64,linux/arm64 --push \
  --tag your-registry/image:tag .
```

## 更新和维护

### 定期任务

1. **更新访问令牌**: 每 90 天更新 Docker Hub 访问令牌
2. **审查权限**: 定期检查 secrets 的访问权限
3. **监控使用情况**: 查看 GitHub Actions 的使用统计

### 版本管理

建议为不同版本的配置使用不同的 secrets：

```yaml
# 开发环境
DOCKER_USERNAME_DEV: dev-docker-user
DOCKER_PASSWORD_DEV: dev-docker-token

# 生产环境
DOCKER_USERNAME_PROD: prod-docker-user
DOCKER_PASSWORD_PROD: prod-docker-token
```

## 相关链接

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [GitHub Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)