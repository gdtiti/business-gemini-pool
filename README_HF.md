---
title: Business Gemini Pool
emoji: 🤖
colorFrom: blue
colorTo: red
sdk: docker
docker_file: Dockerfile
app_file: app.py
pinned: false
license: mit
---

# Business Gemini Pool

基于Google Gemini Enterprise的API代理服务，支持多账号轮训。

## 🚀 HuggingFace Space 部署

此项目已适配 HuggingFace Space 部署，支持通过环境变量进行配置。

### 环境变量配置

在 HuggingFace Space 的 `Settings` > `Variables and secrets` 中配置以下环境变量：

#### 必需配置

- `ACCOUNTS_CONFIG`: 账号配置JSON数组（必需）

```json
[
  {
    "team_id": "88bb1f65-785c-42ad-874d-239467146fa1",
    "secure_c_ses": "CSE.ARsLs01tg8lj4YwZPjk1sjGlm83l5PtnoOM_1dvu-w5N_SHF-NlYJTd31gr8sHIkUxMQIYHVaVnl_7S3PaOkWjQfz4MtC5DpBl-nq-WT1XAgJC2XBGXVsZxAokfZ4CFaoicaUwadIO-pJhIDdfnlN_e44PBb9gHipEmJWqA79tgZP0jEPZNf6TY4G2rdmnE37TEgUJ5nadAL_3bN8wvsBQc0CPBdZs3yKudzvyCnwXwtEDhtgOyjjuBdGx3lry1DmoKOyG2ivLejS7eWlXCO6FJCKdxfxC8GawJdZKJZiba-3D955dqKdiQgG8F1aeLxrvXPWLkUQJ6QWTnIt2nM2rI1Y39rFzXSE72DJ3dsZU-JOW6kuHjU20JaBFxJvDx7J61_rOOTM9TgdBkFQZ0ucmeqwUwfi47MrtOL7w2HNZq4KcaBifb7o8SHhrVKcsBi-gBqlXhVELNsbOOK",
    "host_c_oses": "COS.AQH81rjw7HwLkehCe4KN9U4G-9R6rp5Y71v0afgZn5_gp5ZCYG-wnmXogc5MW81kIv5_-oRHog78j8ZIj7wVkOjI7MwJk0h0K1euShl7tZEwFfa_S6gX_05Arh9jYfn4XMFm4bu9H4GvusCf",
    "csesidx": "1443551910",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "available": true
  }
]
```

#### 可选配置

- `PROXY_URL`: 代理服务器地址
  ```
  http://your-proxy:port
  ```

- `IMAGE_BASE_URL`: 图片服务基础URL
  ```
  https://your-space.hf.space/
  ```

- `MODELS_CONFIG`: 模型配置JSON数组（如不设置将使用默认模型）
  ```
  [{"id":"gemini-enterprise","name":"Gemini Enterprise","description":"Google Gemini Enterprise 模型","context_length":32768,"max_tokens":8192,"enabled":true},{"id":"gemini-enterprise2","name":"Gemini Enterprise","description":"Google Gemini Enterprise 模型","context_length":32768,"max_tokens":8192,"enabled":true}]
  ```

### 配置步骤

1. **Fork 项目**: 将此项目 fork 到你的 HuggingFace 账户
2. **创建 Space**: 创建新的 Docker Space
3. **设置环境变量**: 在 Space 设置中配置上述环境变量
4. **启动**: Space 将自动构建和部署

### 使用方法

服务启动后可通过以下接口访问：

- **Web管理界面**: `/`
- **API接口**: `/v1/chat/completions`
- **模型列表**: `/v1/models`
- **健康检查**: `/health`

### API 使用示例

```bash
# 聊天请求
curl -X POST https://your-space.hf.space/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-enterprise",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

### 特性

- ✅ **多账号轮训**: 自动负载均衡
- ✅ **OpenAI兼容**: 标准API格式
- ✅ **图片支持**: 支持图片输入输出
- ✅ **流式响应**: 支持SSE
- ✅ **Web管理**: 可视化管理界面
- ✅ **环境变量配置**: 无需配置文件

## 注意事项

1. **敏感信息**: 请妥善保管账号配置，使用 HuggingFace 的 secrets 功能
2. **代理设置**: 根据需要配置代理访问 Google 服务
3. **账号状态**: 系统会自动检测和管理账号可用状态
4. **资源限制**: 注意 HuggingFace Space 的资源限制

## 本地开发

```bash
# 克隆项目
git clone https://github.com/your-username/business-gemini-pool.git
cd business-gemini-pool

# 设置环境变量
export ACCOUNTS_CONFIG='[{"team_id":"your-team-id","secure_c_ses":"your-ses","host_c_oses":"your-oses","csesidx":"your-csesidx","available":true}]'

# 启动服务
python gemini.py
```

## 许可证

MIT License