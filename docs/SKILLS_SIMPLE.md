# MiniClaw Skills - DeepAgent 原生实现

## 🎯 核心理念

**极简主义**：只需编写 `SKILL.md` 文档，DeepAgent 自动识别和执行。

```
custom_skills/
└── file_reader/
    └── SKILL.md  # 只需要这个文件！
```

---

## 📝 快速开始

### 步骤 1：创建 SKILL.md

在 `backend/core/skills/custom_skills/your_skill_name/` 目录下创建 `SKILL.md`：

```markdown
---
name: "file_reader"
description: "读取本地文件内容"
author: "Your Name"
async_support: true
parameters:
  - name: "file_path"
    type: "str"
    required: true
    description: "文件路径"
---

# 功能说明

详细描述你的技能...

# 使用示例

示例代码...
```

### 步骤 2：重启后端

```bash
cd backend
python main.py
```

### 步骤 3：在聊天中使用

直接在聊天中输入：
```
帮我读取 example.txt 文件
```

DeepAgent 会自动调用 `file_reader` 技能！

---

## 📋 SKILL.md 完整格式

```yaml
---
# 必填字段
name: "skill_unique_name"        # 唯一标识（与目录名一致）
description: "简短描述"           # 用于 Agent 理解

# 可选字段
author: "Your Name"              # 作者
version: "1.0.0"                 # 版本
async_support: true              # 是否支持异步
parameters:                      # 参数定义
  - name: "param1"
    type: "str"                  # str|int|float|bool|list|dict
    required: true               # 是否必填
    description: "参数描述"
    default: "default_value"     # 默认值
---

# Markdown 正文（DeepAgent 的理解依据）

## 功能说明
详细描述技能的功能、适用场景

## 执行步骤
1. 接收参数 {param1}
2. 执行 XXX 操作
3. 返回结果

## 使用示例
提供具体的调用示例

## 异常处理
说明常见异常及处理方式
```

---

## 🤖 DeepAgent 工作原理

### 1. 自动扫描

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    skills=["./custom_skills/"],  # 自动扫描所有子目录
)
```

### 2. 渐进式加载

- ✅ 只加载 `SKILL.md` 元数据到内存
- ✅ 执行时才加载完整内容
- ✅ 节省 Token 消耗

### 3. 智能推理

当用户请求时：

```
用户："帮我读取文件"

DeepAgent 思考：
1. 分析意图 → 需要读取文件
2. 查看可用技能 → 发现 file_reader
3. 提取参数 → file_path="xxx"
4. 执行技能 → 调用 file_reader
5. 返回结果 → 给用户
```

---

## 📚 示例 Skills

### 示例 1：文件读取

```markdown
---
name: "file_reader"
description: "读取本地文件内容（安全限制目录）"
parameters:
  - name: "file_path"
    type: "str"
    required: true
---

# 文件读取技能

## 功能说明
安全读取 `/tmp/miniclaw_files` 目录下的文件

## 使用示例
用户："读取 config.json"
→ {"file_path": "config.json"}
```

### 示例 2：飞书通知

```markdown
---
name: "feishu_notifier"
description: "发送消息到飞书群聊"
parameters:
  - name: "webhook_url"
    type: "str"
    required: true
  - name: "message"
    type: "str"
    required: true
  - name: "msg_type"
    type: "str"
    default: "text"
---

# 飞书消息推送

## 功能说明
通过 Webhook 发送消息到飞书群聊

## 使用示例
用户："发送飞书消息：测试成功"
→ {"webhook_url": "...", "message": "测试成功"}
```

---

## 🔧 前端创建技能

访问 `http://localhost:8000/skills` 页面：

1. 填写表单（名称、描述）
2. 点击"创建 SKILL.md"
3. 系统自动生成文档
4. 重启后端服务

---

## ❓ 常见问题

### Q: 为什么我创建的 Skill 没有生效？

**A**: 需要重启后端服务或手动触发热重载。

### Q: SKILL.md的格式要求？

**A**: 
- YAML Front Matter（`---`包裹）必须规范
- Markdown 正文要清晰详细
- 参数定义要完整

### Q: DeepAgent 如何理解我的技能？

**A**: 
通过分析 `SKILL.md` 中的：
- `description` 字段（用途）
- `parameters` 定义（输入）
- Markdown 正文（执行逻辑）

### Q: 可以写 Python 代码吗？

**A**: 
DeepAgent 的原生 Skills **只需要 SKILL.md**。如果需要复杂逻辑：
1. 在 SKILL.md 中描述清楚步骤
2. DeepAgent 会自行推理执行
3. 或参考 DeepAgents 高级文档实现自定义 Tool

---

## 🎨 最佳实践

✅ **推荐**：
- 清晰的 `description`（帮助 Agent 理解）
- 完整的参数定义
- 详细的执行步骤说明
- 提供多个使用示例

❌ **避免**：
- 模糊的描述
- 缺少参数说明
- 过于简略的文档

---

## 📖 参考资料

- [DeepAgents 官方文档](https://github.com/langchain-ai/deepagents)
- [SKILL.md 规范](https://github.com/langchain-ai/deepagents/tree/main/libs/cli/examples/skills)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)

---

**总结**：DeepAgent 的 Skills 机制让技能开发变得极其简单——**只需写文档，AI 自己学会使用工具！** 🎉