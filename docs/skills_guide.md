# MiniClaw Skills 自定义接入指南

## 📋 目录

- [核心概念](#核心概念)
- [快速开始](#快速开始)
- [Skill基类详解](#skill-基类详解)
- [开发自定义 Skill](#开发自定义-skill)
- [示例代码](#示例代码)
- [API 接口说明](#api-接口说明)
- [最佳实践](#最佳实践)

---

## 核心概念

### 什么是 Skill？

Skill 是 MiniClaw 中的**最小功能单元**，类似于 OpenClaw 的 Skills 机制。每个 Skill 都是一个独立的、可热插拔的功能模块，具有：

- **标准化接口**：所有 Skill 继承统一的基类
- **元数据管理**：包含名称、描述、版本、作者等信息
- **权限控制**：基于 RBAC 的角色权限绑定
- **生命周期管理**：支持动态加载、卸载、重载
- **参数验证**：标准化的参数定义和验证机制

### 核心组件

| 组件 | 说明 | 文件位置 |
|------|------|---------|
| `SkillBase` | Skill基类，所有技能必须继承 | `base_skill.py` |
| `SkillMetadata` | 元数据模型，定义技能信息 | `skill_metadata.py` |
| `SkillManager` | 技能管理器，负责加载/卸载/热插拔 | `skill_manager.py` |
| `SkillExecutor` | 技能执行引擎，统一执行流程 | `skill_executor.py` |
| `SkillStorage` | 持久化存储，SQLite + Redis | `skill_storage.py` |

---

## 快速开始

### 步骤 1：创建 Skill 文件

在 `backend/core/skills/examples/` 目录下创建新的 Python 文件：

```python
# backend/core/skills/examples/my_skill.py

from core.skills import SkillBase, SkillMetadata, SkillParameter


class MyCustomSkill(SkillBase):
    """我的自定义技能"""
    
    # 定义元数据
    metadata = SkillMetadata(
        name="my_custom_skill",          # 唯一标识符
        description="这是一个自定义技能示例",
        version="1.0.0",
        author="Your Name",
        required_roles=["user"],         # 所需角色
        tags=["custom", "demo"],
    )
    
    # 定义参数
    parameters = [
        SkillParameter(
            name="message",
            type="str",
            description="要处理的消息",
            required=True,
        ),
        SkillParameter(
            name="count",
            type="int",
            description="处理次数",
            required=False,
            default=1,
            min_value=1,
            max_value=10,
        ),
    ]
    
    # 实现核心方法
    async def execute(self, message: str, count: int = 1, **kwargs):
        """技能执行逻辑"""
        result = {
            "original": message,
            "processed": message.upper() * count,
        }
        return result
```

### 步骤 2：加载 Skill

#### 方式 A：通过 API 动态加载（推荐）

```bash
curl -X POST http://127.0.0.1:8000/api/v1/skills/load \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill_path": "/path/to/my_skill.py"}'
```

#### 方式 B：启动时自动加载

在应用启动时调用：

```python
from core.skills import get_skill_manager

manager = get_skill_manager()
manager.load_all_skills("/path/to/skills")
```

### 步骤 3：执行 Skill

```bash
curl -X POST http://127.0.0.1:8000/api/v1/skills/execute/my_custom_skill \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "hello world",
    "count": 2
  }'
```

响应：

```json
{
  "success": true,
  "data": {
    "original": "hello world",
    "processed": "HELLO WORLDHELLO WORLD"
  },
  "message": "技能执行成功：my_custom_skill",
  "error": null
}
```

---

## Skill基类详解

### SkillBase 核心方法

#### 1. `metadata: SkillMetadata` （必须定义）

技能元数据，包含：

```python
metadata = SkillMetadata(
    name="unique_name",           # 必填，唯一标识
    description="技能描述",        # 必填
    version="1.0.0",              # 可选，默认 "1.0.0"
    author="作者名",               # 可选
    required_roles=["user"],      # 可选，所需角色列表
    async_support=True,           # 可选，是否支持异步
    enabled=True,                 # 可选，默认启用
    tags=["tag1", "tag2"],        # 可选，标签列表
)
```

#### 2. `parameters: List[SkillParameter]` （可选）

参数定义列表：

```python
parameters = [
    SkillParameter(
        name="param_name",        # 必填，参数名
        type="str",               # 必填，类型：str|int|float|bool|list|dict
        description="参数描述",    # 必填
        required=True,            # 可选，是否必填
        default=None,             # 可选，默认值
        min_value=0,              # 可选，最小值
        max_value=100,            # 可选，最大值
    ),
]
```

#### 3. `async def execute(self, **kwargs) -> Any` （必须实现）

核心执行方法：

```python
async def execute(self, param1: str, param2: int = 1, **kwargs):
    """
    技能执行逻辑
    
    Args:
        param1: 参数 1
        param2: 参数 2
        
    Returns:
        Any: 执行结果（任意类型）
        
    Raises:
        Exception: 执行失败时抛出异常
    """
    # 你的业务逻辑
    result = {"key": "value"}
    return result
```

#### 4. `on_load(self)` （可选）

加载钩子，技能首次加载时调用：

```python
def on_load(self):
    """初始化资源"""
    print(f"技能已加载：{self.metadata.name}")
```

#### 5. `on_unload(self)` （可选）

卸载钩子，技能移除前调用：

```python
def on_unload(self):
    """清理资源"""
    print(f"技能已卸载：{self.metadata.name}")
```

#### 6. `validate_params(self, params: Dict) -> tuple[bool, str]` （可选覆盖）

参数验证：

```python
async def validate_params(self, params: Dict):
    """
    自定义参数验证
    
    Returns:
        tuple[bool, str]: (是否通过，错误消息)
    """
    # 基础验证（自动处理必填和类型检查）
    is_valid, error_msg = await super().validate_params(params)
    if not is_valid:
        return False, error_msg
    
    # 自定义验证逻辑
    if params.get("count") > 100:
        return False, "count 不能超过 100"
    
    return True, ""
```

---

## 开发自定义 Skill

### 完整示例：天气查询 Skill

```python
"""
天气查询 Skill - 演示完整的 Skill 开发流程
"""
import requests
from typing import Any, Dict
from loguru import logger

from core.skills import SkillBase, SkillMetadata, SkillParameter


class WeatherQuerySkill(SkillBase):
    """天气查询技能"""
    
    metadata = SkillMetadata(
        name="weather_query",
        description="查询指定城市的天气信息",
        version="1.0.0",
        author="MiniClaw Team",
        required_roles=["user", "admin"],
        async_support=True,
        enabled=True,
        tags=["weather", "query", "api"],
    )
    
    parameters = [
        SkillParameter(
            name="city",
            type="str",
            description="城市名称",
            required=True,
        ),
        SkillParameter(
            name="days",
            type="int",
            description="预报天数（1-7）",
            required=False,
            default=1,
            min_value=1,
            max_value=7,
        ),
    ]
    
    def on_load(self):
        """初始化"""
        super().on_load()
        self.api_key = "your_weather_api_key"  # 替换为实际 API Key
        logger.info("天气查询技能已就绪")
    
    async def execute(self, city: str, days: int = 1, **kwargs) -> Dict[str, Any]:
        """
        执行天气查询
        
        Args:
            city: 城市名称
            days: 预报天数
            
        Returns:
            Dict[str, Any]: 天气信息
        """
        try:
            logger.info(f"查询天气：city={city}, days={days}")
            
            # 调用天气 API（示例代码）
            url = f"https://api.weather.com/v1/city/{city}"
            params = {"days": days, "key": self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            weather_data = response.json()
            
            result = {
                "city": city,
                "weather": weather_data,
                "forecast_days": days,
            }
            
            logger.info(f"天气查询成功：{city}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"天气查询超时：{city}")
            raise TimeoutError("天气查询超时")
        except Exception as e:
            logger.error(f"天气查询失败：{str(e)}")
            raise RuntimeError(f"查询失败：{str(e)}")
    
    async def validate_params(self, params: Dict) -> tuple[bool, str]:
        """自定义参数验证"""
        # 基础验证
        is_valid, error_msg = await super().validate_params(params)
        if not is_valid:
            return False, error_msg
        
        # 自定义验证：城市名称不能为空
        if not params.get("city"):
            return False, "城市名称不能为空"
        
        # 自定义验证：城市名称长度限制
        if len(params["city"]) > 50:
            return False, "城市名称过长"
        
        return True, ""
```

---

## 示例代码

### 示例 1：文件操作 Skill

详见：`backend/core/skills/examples/file_skill.py`

- `FileReaderSkill`: 读取文件内容
- `FileWriterSkill`: 写入文件内容
- 特点：包含安全检查、权限控制

### 示例 2：Shell 执行 Skill

详见：`backend/core/skills/examples/shell_skill.py`

- `ShellExecutorSkill`: 执行系统命令
- 特点：危险操作、安全过滤、仅管理员

### 示例 3：飞书推送 Skill

详见：`backend/core/skills/examples/feishu_skill.py`

- `FeishuNotifierSkill`: 发送飞书消息
- 特点：支持 Markdown、@用户、多种消息类型

---

## API 接口说明

### 获取技能列表

```http
GET /api/v1/skills
Authorization: Bearer <token>

Response:
[
  {
    "name": "file_reader",
    "description": "读取本地文件内容的技能",
    "version": "1.0.0",
    "author": "MiniClaw Team",
    "required_roles": ["user", "admin"],
    "enabled": true,
    "tags": ["file", "io", "reader"],
    "parameters": [...]
  }
]
```

### 获取技能详情

```http
GET /api/v1/skills/{skill_name}
Authorization: Bearer <token>
```

### 加载技能

```http
POST /api/v1/skills/load
Authorization: Bearer <token>
Content-Type: application/json

{
  "skill_path": "/path/to/skill.py"
}
```

**权限要求**: 管理员

### 卸载技能

```http
POST /api/v1/skills/unload/{skill_name}
Authorization: Bearer <token>
```

**权限要求**: 管理员

### 热重载技能

```http
POST /api/v1/skills/reload/{skill_name}
Authorization: Bearer <token>
```

**权限要求**: 管理员

### 执行技能

```http
POST /api/v1/skills/execute/{skill_name}
Authorization: Bearer <token>
Content-Type: application/json

{
  "param1": "value1",
  "param2": 123
}
```

**权限要求**: 已授权角色

### 查询异步任务状态

```http
GET /api/v1/skills/execution/{task_id}
Authorization: Bearer <token>
```

---

## 最佳实践

### 1. 命名规范

- ✅ 使用小写字母和下划线：`file_reader`, `weather_query`
- ❌ 避免使用大写字母和连字符：`FileReader`, `weather-query`
- ✅ 保持名称唯一性和描述性

### 2. 参数设计

```python
# ✅ 好的设计
parameters = [
    SkillParameter(name="file_path", type="str", required=True),
    SkillParameter(name="encoding", type="str", default="utf-8"),
]

# ❌ 不好的设计
parameters = [
    SkillParameter(name="f", type="str", required=True),  # 名称不明确
    SkillParameter(name="param1", type="str"),            # 无描述
]
```

### 3. 错误处理

```python
# ✅ 推荐做法
async def execute(self, **kwargs):
    try:
        # 业务逻辑
        result = await self.do_something()
        return result
    except FileNotFoundError as e:
        logger.error(f"文件不存在：{str(e)}")
        raise
    except Exception as e:
        logger.error(f"执行失败：{str(e)}")
        raise RuntimeError(f"技能执行失败：{str(e)}")
```

### 4. 安全检查

```python
# ✅ 路径安全检查
allowed_base_dir = "/tmp/miniclaw_files"
abs_path = os.path.abspath(file_path)
if not abs_path.startswith(allowed_base_dir):
    raise ValueError(f"不允许访问该路径")
```

### 5. 日志记录

```python
# ✅ 完整的日志记录
logger.info(f"开始执行：{self.metadata.name}, user={user_id}")
try:
    result = await self.execute(**params)
    logger.info(f"执行成功：{self.metadata.name}")
    return result
except Exception as e:
    logger.error(f"执行失败：{self.metadata.name}, error={str(e)}")
    raise
```

### 6. 性能优化

- 使用异步方法处理 I/O 密集型任务
- 缓存重复计算的结果
- 设置合理的超时时间
- 避免阻塞主线程

---

## 常见问题

### Q1: Skill 加载失败怎么办？

**A**: 检查以下几点：
1. 文件路径是否正确
2. 是否继承了 `SkillBase` 并实现了 `execute` 方法
3. 查看后端日志中的详细错误信息

### Q2: 如何调试 Skill？

**A**: 
1. 在 Skill 中添加 `logger.debug()` 语句
2. 查看后端日志输出
3. 使用断点调试（IDE 支持）

### Q3: Skill 之间如何通信？

**A**: 
- 通过共享的 `SkillStorage` 交换数据
- 通过外部服务（数据库、Redis、API）
- 不推荐 Skill 直接调用其他 Skill

### Q4: 如何禁用某个 Skill？

**A**: 
- 修改元数据：`enabled=False`
- 或通过 API 卸载：`POST /api/v1/skills/unload/{skill_name}`

---

## 总结

MiniClaw Skills 机制提供了：

✅ **标准化接入**：统一的基类和元数据规范  
✅ **热插拔能力**：动态加载/卸载/重载  
✅ **权限控制**：基于 RBAC 的角色绑定  
✅ **执行引擎**：标准化的执行流程  
✅ **持久化存储**：SQLite + Redis 混合存储  

遵循本指南，你可以快速开发出符合规范的自定义 Skill！

📚 **相关文档**:
- [项目结构说明](../../STRUCTURE.md)
- [部署指南](../../deployment.md)
- [开发指南](../../development.md)