# Google Gemini 使用指南

## 📋 配置步骤

### 1. 获取 API Key

访问 [Google AI Studio](https://aistudio.google.com/app/apikey)，登录 Google 账号并创建 API Key。

API Key 格式：以 `AIza` 开头的字符串，例如：
```
AIzaSyCHwwgZuPt3RUroNKB3sxc3BnpBMYZCyrU
```

### 2. 在前端添加模型

1. 打开 **http://127.0.0.1:5173/models**
2. 点击 **【添加模型】**
3. 选择提供商：**Google Gemini**
4. 填写以下信息：

```
┌─────────────────────────────────────┐
│ 添加模型                            │
├─────────────────────────────────────┤
│ 提供商：Google Gemini ▼            │
│                                     │
│ 📋 只需填写 2 个参数：               │
│ 1. 模型名称                          │
│ 2. API Key                          │
│                                     │
│ 🤖 模型名称：                        │
│ ┌──────────────────────────────┐   │
│ │ gemini-2.5-flash             │   │
│ └──────────────────────────────┘   │
│                                     │
│ 🔑 API Key:                         │
│ ┌──────────────────────────────┐   │
│ │ ●●●●●●●●●●●●●●●●●●●●        │   │
│ └──────────────────────────────┘   │
│                                     │
│          ┌──────┐  ┌──────┐       │
│          │ 取消 │  │ 确定 │       │
│          └──────┘  └──────┘       │
└─────────────────────────────────────┘
```

### 3. 可用模型列表

| 模型名称 | 特点 | 推荐场景 |
|---------|------|---------|
| `gemini-2.5-flash` | 最新 Flash 模型 | ⭐ 推荐 - 速度快、质量好 |
| `gemini-2.0-flash-exp` | 实验版本 | 尝鲜测试 |
| `gemini-1.5-pro` | 高质量模型 | 复杂任务 |
| `gemini-1.5-flash` | 平衡模型 | 日常对话 |

### 4. 测试连接

1. 添加成功后，在模型列表中找到刚添加的模型
2. 点击 **【测试连接】** 按钮
3. 看到 ✅ 成功提示即可使用

### 5. 开始对话

1. 切换到 **【对话】** 页面
2. 发送消息测试
3. 等待 AI 回复（通常 1-3 秒）

---

## ❗ 常见问题

### Q1: API Key 无效？

**原因：**
- API Key 输入错误
- 包含空格或特殊字符
- API Key 已过期或被撤销

**解决方法：**
1. 重新从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取新的 API Key
2. 复制时确保没有多余空格
3. 删除旧模型，重新添加

### Q2: 网络连接失败？

**原因：**
- 无法访问 Google 服务
- 网络环境问题

**解决方法：**
1. 检查网络连接
2. 确认能访问 google.com
3. 检查防火墙设置

### Q3: 模型不可用？

**原因：**
- 模型名称拼写错误
- 该模型在你的地区不可用

**解决方法：**
1. 使用推荐的 `gemini-2.5-flash`
2. 尝试 `gemini-1.5-flash`

---

## 🔧 技术细节

### 适配器实现

后端使用官方 Google GenAI SDK：

```python
from google import genai

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="你的问题"
)

print(response.text)
```

### 参数说明

- **模型名称**：必填，如 `gemini-2.5-flash`
- **API Key**：必填，从 Google AI Studio 获取
- **温度参数**：自动设置为 0.7（推荐值）
- **最大 Token**：自动设置为 8192（Gemini 支持的最大值）
- **API 端点**：自动设置为 `https://generativelanguage.googleapis.com`

### 环境变量（可选）

如果不想在前端输入 API Key，可以在 `.env` 文件中配置：

```bash
GOOGLE_GEMINI_API_KEY=AIzaSyCHwwgZuPt3RUroNKB3sxc3BnpBMYZCyrU
```

---

## 📞 获取帮助

遇到问题请查看：
- [Google AI Studio 文档](https://ai.google.dev/)
- [Gemini API 参考](https://ai.google.dev/api)
- 项目 Issues
