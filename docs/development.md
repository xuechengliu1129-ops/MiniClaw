# MiniClaw 开发文档

## 模块设计说明

### 1. Skills 技能管理模块

#### 架构设计
```
backend/core/skills/
├── __init__.py          # 核心类与接口定义
├── skill_base.py        # 技能基类（待扩展）
├── skill_manager.py     # 技能管理器（待扩展）
└── builtin/             # 内置技能（待实现）
    ├── web_search.py
    ├── file_manager.py
    └── ...
```

#### 技能开发规范

**步骤 1: 继承 SkillBase 基类**
```python
from core.skills import SkillBase, SkillMetadata, SkillParameter, SkillResult

class MyCustomSkill(SkillBase):
    metadata = SkillMetadata(
        name="my_skill",
        description="我的自定义技能",
        version="1.0.0",
        author="Your Name",
        tags=["custom", "demo"],
    )
    
    parameters = [
        SkillParameter(
            name="input",
            type="str",
            description="输入参数",
            required=True,
        ),
    ]
    
    async def execute(self, input: str, **kwargs) -> SkillResult:
        # 实现技能逻辑
        return SkillResult(success=True, data={"result": "done"})
```

**步骤 2: 注册技能**
```python
from core.skills import get_skill_manager

skill_manager = get_skill_manager()
skill_manager.register_skill(MyCustomSkill())
```

**步骤 3: 配置权限**
在权限管理中为技能分配可执行的角色

---

### 2. Memory 记忆管理模块

#### 记忆分级策略

- **用户级记忆 (user)**: 与特定用户关联，如偏好设置、历史记录
- **技能级记忆 (skill)**: 技能执行过程中的中间结果和上下文
- **全局级记忆 (global)**: 系统级知识，所有用户和技能共享

#### 记忆优化机制

1. **去重**: 基于内容哈希值识别重复记忆
2. **过期清理**: 定期扫描 expires_at 字段，删除过期记忆
3. **重要性评分**: 
   - 基础分：创建时指定 (0-1)
   - 访问加成：每次访问 +0.01，上限 0.3
   - 时间衰减：每天 -0.001

#### 检索策略

```python
from core.memory import get_memory_manager, MemorySearchRequest

memory_manager = get_memory_manager()

# 关键词检索
request = MemorySearchRequest(
    query="用户偏好",
    level="user",
    user_id=1,
    top_k=5,
)
memories = await memory_manager.search_memories(request)

# 向量检索（需要向量模型支持）
request = MemorySearchRequest(
    query="相关内容",
    use_vector_search=True,
    top_k=10,
)
```

---

### 3. Model 模型适配模块

#### 支持的模型提供商

**Ollama 本地模型**
```python
from core.model import ModelConfig, get_model_manager

config = ModelConfig(
    name="llama2",
    provider="ollama",
    base_url="http://localhost:11434",
    model_type="chat",
    context_window=4096,
    max_tokens=2048,
    temperature=0.7,
    is_default=True,
)

model_manager = get_model_manager()
model_manager.register_model(config)
```

**OpenAI 兼容模型**
```python
config = ModelConfig(
    name="gpt-3.5-turbo",
    provider="openai",
    base_url="https://api.openai.com/v1",
    api_key="sk-xxx",
    model_type="chat",
)
```

#### 模型降级策略

当首选模型调用失败时，自动尝试默认模型：
```python
response = await model_manager.execute_with_fallback(
    model_name="gpt-4",
    messages=[{"role": "user", "content": "你好"}],
)
```

---

### 4. Feishu 飞书集成模块

#### 配置流程

1. **创建飞书应用**
   - 访问 https://open.feishu.cn/
   - 创建企业自建应用
   - 获取 App ID、App Secret

2. **配置权限**
   - 机器人能力：发送消息、接收消息
   - 事件订阅：im.message

3. **环境变量配置**
```env
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxx (可选)
```

#### 指令格式

用户发送：`/技能名 参数`

示例：
```
/web_search 今天北京的天气
/file_manager 整理 /home/user/downloads 目录
```

---

### 5. Gateway 网关模块

#### 限流算法

基于 Redis 的令牌桶算法：
- 桶容量：100 个令牌
- 补充速率：10 个/秒
- 每请求消耗：1 个令牌

#### 日志级别

- **DEBUG**: 详细调试信息
- **INFO**: 一般信息
- **WARN**: 警告信息
- **ERROR**: 错误信息

---

### 6. Auth RBAC 权限模块

#### 预设角色

| 角色 | 标识 | 权限 |
|------|------|------|
| 超级管理员 | super_admin | 所有权限 |
| 普通用户 | normal_user | API 访问、技能执行、记忆读写 |
| 技能开发者 | skill_developer | API 访问、技能执行、记忆读取、模型配置 |
| 只读用户 | readonly_user | API 访问、记忆读取 |

#### 权限粒度

- **接口权限**: `api:access`
- **技能执行**: `skill:execute:<skill_name>`
- **记忆操作**: `memory:read`, `memory:write`
- **模型配置**: `model:config`
- **管理后台**: `admin:access`

---

## 数据库表结构

### users 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| email | VARCHAR(100) | 邮箱 |
| password_hash | VARCHAR(255) | 密码哈希 |
| roles | JSON | 角色列表 |
| enabled | BOOLEAN | 是否启用 |

### skills 技能表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 技能名称（唯一） |
| description | TEXT | 描述 |
| version | VARCHAR(20) | 版本 |
| parameters | JSON | 参数定义 |
| enabled | BOOLEAN | 是否启用 |

### memories 记忆表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| content | TEXT | 内容 |
| level | VARCHAR(20) | 级别 |
| vector | JSON | 向量表示 |
| importance | FLOAT | 重要性评分 |

---

## API 接口规范

### 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误码定义
- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 权限不足
- 404: 资源不存在
- 429: 请求过于频繁
- 500: 服务器内部错误

---

## 测试规范

### 单元测试
```bash
cd backend
pytest tests/test_skills.py -v
pytest tests/test_memory.py -v
pytest tests/test_auth.py -v
```

### 覆盖率要求
- 核心模块：>80%
- API 层：>70%
- 总体：>75%
