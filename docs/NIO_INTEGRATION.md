# NIO公司 DeepSeek 模型集成指南

## 概述

MiniClaw 现已支持 NIO公司的 DeepSeek-V3.1 模型，通过 OpenAI 兼容的 API 接口进行集成。

## 配置信息

- **模型名称**: DeepSeek-V3.1
- **提供商**: NIO
- **Base URL**: https://modelgateway.nioint.com/publicService/v1
- **API Key**: `a7425832-75a5-4f53-853c-44fad94bf4a7`

## 使用方法

### 方法一：通过前端界面配置（推荐）

1. 访问 MiniClaw 前端的"模型配置"页面
2. 点击"添加模型"按钮
3. 在"提供商"下拉框中选择 **"NIO DeepSeek"**
4. 系统会自动填充默认配置：
   - 模型名称：`DeepSeek-V3.1`
   - Base URL: `https://modelgateway.nioint.com/publicService/v1`
5. 填写 API Key（如果需要）
6. 点击"确定"保存配置

### 方法二：通过 API 直接添加

```bash
curl -X POST http://localhost:8000/api/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DeepSeek-V3.1",
    "provider": "nio",
    "endpoint": "https://modelgateway.nioint.com/publicService/v1",
    "api_key": "a7425832-75a5-4f53-853c-44fad94bf4a7",
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

### 方法三：通过 Python 代码调用

```python
from core.model.openai_adapter import OpenAIAdapter
from core.model import ModelConfig

# 创建配置
config = ModelConfig(
    name="DeepSeek-V3.1",
    provider="nio",
    base_url="https://modelgateway.nioint.com/publicService/v1",
    api_key="a7425832-75a5-4f53-853c-44fad94bf4a7",
)

# 创建适配器
adapter = OpenAIAdapter(config)

# 调用对话
messages = [{"role": "user", "content": "你好"}]
response = await adapter.chat(messages)

if response.success:
    print(f"回复：{response.content}")
```

## 测试连接

运行测试脚本验证连接是否正常：

```bash
cd /Users/xuecheng.liu/code/MiniClaw/backend
conda activate MiniClaw
python test_nio.py
```

预期输出：
```
============================================================
🧪 测试 NIO公司 DeepSeek 模型连接
============================================================

📋 配置信息:
   模型名称：DeepSeek-V3.1
   提供商：nio
   Base URL: https://modelgateway.nioint.com/publicService/v1
   API Key: a7425832-7...bf4a7

🔍 执行健康检查...
✅ 健康检查通过

💬 测试对话...
✅ 对话成功
📝 回复内容：你好，我是 DeepSeek，由深度求索公司创造的 AI 助手，乐于为你提供智能对话与帮助！
📊 Token 使用：{'prompt_tokens': 14, 'completion_tokens': 25, 'total_tokens': 39}
```

## 支持的参数

- **temperature**: 温度参数 (0-2)，默认 0.7
- **max_tokens**: 最大生成 token 数，默认 2048
- **top_p**: Top-p 采样参数 (可选)

## 故障排查

### 问题 1：连接失败

**症状**: 无法连接到 NIO 服务

**解决方案**:
1. 检查网络连接是否正常
2. 确认 Base URL 是否正确
3. 验证 API Key 是否有效

### 问题 2：认证失败

**症状**: 返回 401 错误

**解决方案**:
1. 检查 API Key 是否正确
2. 确认 API Key 未过期
3. 联系 NIO 管理员确认权限

## 技术实现

### 架构设计

- **适配器模式**: 使用 `OpenAIAdapter` 统一处理 OpenAI 兼容的 API
- **代理绕过**: 自动设置 `NO_PROXY` 环境变量，确保本地服务正常访问
- **异步 HTTP**: 使用 `httpx.AsyncClient` 进行高效的异步请求

### 核心文件

- `backend/core/model/openai_adapter.py`: OpenAI 兼容适配器实现
- `backend/core/model/__init__.py`: 模型管理器，支持 NIO provider
- `backend/api/v1/models.py`: 模型配置 API
- `frontend/src/pages/Models.vue`: 前端模型配置界面

## 扩展其他 OpenAI 兼容服务

除了 NIO，该适配器还支持其他 OpenAI 兼容的服务：

1. 在前端选择 **"OpenAI Compatible"**
2. 填写模型名称（如 `gpt-3.5-turbo`）
3. 填写自定义 Base URL
4. 填写 API Key
5. 保存配置

支持的服務包括：
- OpenAI 官方 API
- Azure OpenAI
- 其他第三方 OpenAI 兼容服务
