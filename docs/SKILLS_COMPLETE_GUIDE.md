# MiniClaw Skills 完整使用指南

## 🎯 核心功能

MiniClaw Skills 系统提供**完整的技能生命周期管理**，让 LangChain Agent 真正能自动识别和调用你的自定义技能。

### 核心特性

✅ **前端可视化创建** - 通过 Web 界面直接创建技能  
✅ **自动加载** - 创建后自动扫描并加载到内存  
✅ **Agent 自动识别** - LangChain Agent 可直接调用所有技能  
✅ **热插拔** - 支持动态加载/卸载/重载  
✅ **权限控制** - 基于 RBAC 的角色绑定  

---

## 📋 目录结构

```
backend/core/skills/custom_skills/
├── file_reader/          # 文件读取技能
│   ├── skill.py          # Python 实现（LangChain Tool）
│   └── SKILL.md          # 技能文档
├── feishu_notifier/      # 飞书通知技能
│   ├── skill.py
│   └── SKILL.md
└── your_new_skill/       # 你的新技能
    ├── skill.py
    └── SKILL.md
```

---

## 🚀 快速开始

### 方法一：前端可视化创建（推荐）

#### 步骤 1：访问 Skills 页面

打开浏览器访问：`http://localhost:8000/skills`

#### 步骤 2：填写技能信息

- **技能名称**: `my_custom_skill`（只能包含字母、数字和下划线）
- **技能描述**: 描述技能的功能
- **作者**: 你的昵称
- **所需角色**: 选择哪些角色可以执行此技能
- **Python 代码**: 完整的 skill.py 代码

#### 步骤 3：点击"创建技能"

系统会自动：
1. ✅ 创建目录：`custom_skills/my_custom_skill/`
2. ✅ 写入 `skill.py` 文件
3. ✅ 写入 `SKILL.md` 文档
4. ✅ 自动加载技能到内存
5. ✅ 注册到 LangChain Agent

#### 步骤 4：验证技能

刷新页面，在"已加载的技能"列表中查看你的新技能！

---

### 方法二：手动创建（高级用户）

#### 步骤 1：创建目录

```bash
cd /Users/xuecheng.liu/code/MiniClaw/backend/core/skills/custom_skills
mkdir my_awesome_skill
```

#### 步骤 2：编写 skill.py

在目录下创建 `skill.py` 文件：

```python
"""
MyAwesomeSkill - 超酷的技能
基于 LangChain BaseTool 实现
"""
from core.skills import BaseSkill, SkillMetadata, SkillParameter


class MyAwesomeSkill(BaseSkill):
    """我的超酷技能"""
    
    metadata = SkillMetadata(
        name="my_awesome_skill",
        description="这是一个非常厉害的技能，可以做 XXX",
        version="1.0.0",
        author="Your Name",
        required_roles=["user"],
        tags=["awesome", "cool"],
    )
    
    parameters = [
        SkillParameter(
            name="input_text",
            type="str",
            required=True,
            description="输入文本",
        ),
    ]
    
    def _run(self, input_text: str) -> dict:
        """
        技能核心执行方法
        
        Returns:
            dict: 执行结果
        """
        # 你的业务逻辑
        result = {
            "original": input_text,
            "upper": input_text.upper(),
            "length": len(input_text),
            "reversed": input_text[::-1],
        }
        return result
```

#### 步骤 3：编写 SKILL.md

```markdown
---
name: "my_awesome_skill"
description: "我的超酷技能"
author: "Your Name"
version: "1.0.0"
required_roles: ["user"]
async_support: true
tags: ["awesome", "cool"]
parameters:
  - name: "input_text"
    type: "str"
    required: true
    description: "输入文本"
---

# 功能说明

这个技能可以将文本转换为大写，并返回多种格式。

## 使用示例

```json
{
  "input_text": "hello world"
}
```

响应：
```json
{
  "original": "hello world",
  "upper": "HELLO WORLD",
  "length": 11,
  "reversed": "dlrow olleh"
}
```
```

#### 步骤 4：重启后端（或调用加载 API）

```bash
# 方式 A：重启后端（最简单）
cd /Users/xuecheng.liu/code/MiniClaw/backend
python main.py

# 方式 B：调用 API 热加载
curl -X POST http://localhost:8000/api/v1/skills/load \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"skill_path": "/path/to/my_awesome_skill"}'
```

---

## 🤖 Agent 自动识别原理

### 核心机制

当你创建技能后，系统会：

1. **扫描目录** → 发现 `custom_skills/` 下的所有子目录
2. **加载 skill.py** → 动态导入 Python 模块
3. **实例化 Skill** → 创建 LangChain Tool 实例
4. **注册到 Agent** → 添加到 LangChain Agent 的 tools 列表
5. **Agent 推理** → Agent 根据用户输入自动选择合适的技能

### Agent 如何调用技能？

当用户提问时：

```
用户："帮我把 'hello world' 转成大写"

Agent 思考过程：
1. 分析用户需求 → 需要文本转换
2. 查看所有可用技能 → 发现 my_awesome_skill
3. 决定调用技能 → Action: my_awesome_skill
4. 传递参数 → Action Input: {"input_text": "hello world"}
5. 接收结果 → Observation: {"upper": "HELLO WORLD", ...}
6. 回复用户 → Final Answer: "转换结果是：HELLO WORLD"
```

---

## 📝 代码模板

### 基础模板（复制粘贴即可）

```python
"""
YourSkillName - 技能名称
基于 LangChain BaseTool 实现
"""
from core.skills import BaseSkill, SkillMetadata, SkillParameter


class YourSkillClass(BaseSkill):
    """你的技能类"""
    
    metadata = SkillMetadata(
        name="your_skill_name",  # 必须与文件名一致
        description="简短描述技能功能",
        version="1.0.0",
        author="Your Name",
        required_roles=["user"],  # 或 ["admin"], ["user", "admin"]
        tags=["tag1", "tag2"],
    )
    
    parameters = [
        SkillParameter(
            name="param1",
            type="str",
            required=True,
            description="参数 1 描述",
        ),
        SkillParameter(
            name="param2",
            type="int",
            required=False,
            default=0,
            description="参数 2 描述",
        ),
    ]
    
    def _run(self, param1: str, param2: int = 0) -> dict:
        """
        技能核心执行方法
        
        Args:
            param1: 参数 1
            param2: 参数 2
            
        Returns:
            dict: 执行结果（必须是字典）
        """
        # TODO: 你的业务逻辑
        result = {
            "status": "success",
            "message": "执行成功",
            "data": {},  # 返回你的数据
        }
        return result
```

---

## 🔧 常见问题

### Q1: 创建技能后，Agent 为什么没有自动识别？

**A**: 检查以下几点：
1. ✅ 确认 `skill.py` 文件中定义了继承自 `BaseSkill` 的类
2. ✅ 确认类有 `metadata` 属性（SkillMetadata 类型）
3. ✅ 确认实现了 `_run()` 方法
4. ✅ 重启后端服务或调用 `/api/v1/skills/reload/{skill_name}`

### Q2: 技能执行失败怎么办？

**A**: 
1. 查看后端日志：`tail -f backend/logs/app.log`
2. 检查参数是否正确传递
3. 确认权限是否足够（required_roles）
4. 测试单独执行技能：`POST /api/v1/skills/execute/{skill_name}`

### Q3: 如何在 Chat 中使用技能？

**A**: 
直接在聊天中输入自然语言，Agent 会自动判断是否需要调用技能：

```
用户："帮我读取 /tmp/miniclaw_files/test.txt 文件"
→ Agent 自动调用 file_reader 技能

用户："发送一条飞书消息到群聊"
→ Agent 自动调用 feishu_notifier 技能
```

### Q4: 技能之间如何共享数据？

**A**: 
通过返回值和外部存储：

```python
# 技能 A 返回数据
def _run(self):
    return {"data": "shared_value"}

# 技能 B 从 Redis/数据库读取
def _run(self):
    data = redis.get("shared_key")
    return {"result": data}
```

---

## 🎨 最佳实践

### 1. 命名规范

✅ **好的命名**:
- `file_reader` - 清晰明确
- `weather_query` - 描述功能
- `image_processor` - 说明用途

❌ **不好的命名**:
- `skill1` - 不明确
- `my_skill` - 太笼统
- `test` - 临时感

### 2. 错误处理

```python
def _run(self, file_path: str) -> dict:
    try:
        # 业务逻辑
        result = self.process(file_path)
        return {
            "status": "success",
            "data": result,
        }
    except FileNotFoundError as e:
        logger.error(f"文件不存在：{e}")
        raise RuntimeError(f"文件不存在：{file_path}")
    except Exception as e:
        logger.error(f"执行失败：{e}")
        raise RuntimeError(f"技能执行失败：{str(e)}")
```

### 3. 日志记录

```python
from loguru import logger

def _run(self, **kwargs):
    logger.info(f"🚀 开始执行：{self.metadata.name}")
    try:
        result = self.process(**kwargs)
        logger.info(f"✅ 执行成功：{self.metadata.name}")
        return result
    except Exception as e:
        logger.error(f"❌ 执行失败：{self.metadata.name}, error={e}")
        raise
```

---

## 📊 API 接口一览

| 接口 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/api/v1/skills` | GET | 获取技能列表 | 所有用户 |
| `/api/v1/skills` | POST | 创建技能 | 所有用户 |
| `/api/v1/skills/{name}` | GET | 获取技能详情 | 所有用户 |
| `/api/v1/skills/load` | POST | 加载技能 | 管理员 |
| `/api/v1/skills/unload/{name}` | POST | 卸载技能 | 管理员 |
| `/api/v1/skills/reload/{name}` | POST | 热重载技能 | 管理员 |
| `/api/v1/skills/execute/{name}` | POST | 执行技能（同步） | 已授权用户 |
| `/api/v1/skills/execute/async/{name}` | POST | 执行技能（异步） | 已授权用户 |

---

## 🎯 总结

MiniClaw Skills 系统提供**完整的技能开发生态**：

1. ✅ **前端可视化创建** - 零门槛创建技能
2. ✅ **自动加载** - 无需手动配置
3. ✅ **Agent 自动识别** - LangChain Agent 智能调用
4. ✅ **热插拔** - 动态管理技能
5. ✅ **权限控制** - 安全的 RBAC 体系

现在就开始创建你的第一个技能吧！🚀