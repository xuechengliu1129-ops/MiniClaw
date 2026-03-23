# MiniClaw 项目结构说明

## 完整目录结构

```
MiniClaw/
│
├── README.md                          # 项目说明文档
├── .env.example                       # 环境变量示例
├── .gitignore                         # Git 忽略文件
├── docker-compose.yml                 # Docker 编排配置
│
├── docs/                              # 文档目录
│   ├── development.md                 # 开发文档
│   └── deployment.md                  # 部署指南
│
├── backend/                           # 后端工程目录
│   ├── main.py                        # FastAPI 应用入口
│   ├── requirements.txt               # Python 依赖声明
│   ├── pytest.ini                     # 测试配置
│   ├── Dockerfile                     # 后端 Docker 镜像
│   │
│   ├── api/                           # API 接口层
│   │   └── v1/
│   │       └── __init__.py            # v1 版本路由注册
│   │
│   ├── core/                          # 业务核心逻辑层
│   │   ├── agent/                     # DeepAgent 智能体封装
│   │   │   └── __init__.py
│   │   ├── skills/                    # 技能管理模块
│   │   │   └── __init__.py
│   │   ├── memory/                    # 记忆管理模块
│   │   │   └── __init__.py
│   │   ├── model/                     # 模型适配模块
│   │   │   └── __init__.py
│   │   ├── feishu/                    # 飞书集成模块
│   │   │   └── __init__.py
│   │   ├── gateway/                   # 网关模块
│   │   │   └── __init__.py
│   │   └── auth/                      # RBAC 权限管理
│   │       └── __init__.py
│   │
│   ├── config/                        # 全局配置模块
│   │   └── __init__.py
│   │
│   ├── db/                            # 数据库模型与迁移
│   │   └── __init__.py
│   │
│   └── tests/                         # 单元测试目录
│       ├── __init__.py
│       ├── test_skills.py             # Skills 模块测试
│       ├── test_memory.py             # Memory 模块测试
│       └── test_auth.py               # Auth 模块测试
│
└── frontend/                          # 前端工程目录
    ├── package.json                   # Node.js 依赖声明
    ├── vite.config.js                 # Vite 构建配置
    ├── Dockerfile                     # 前端 Docker 镜像
    ├── nginx.conf                     # Nginx 配置
    │
    └── src/                           # 源代码目录
        ├── main.js                    # 前端入口文件
        ├── App.vue                    # 根组件
        │
        ├── api/                       # API 请求封装
        │   ├── request.js             # Axios 实例配置
        │   └── skills.js              # Skills API
        │
        ├── router/                    # 路由配置
        │   └── index.js
        │
        ├── store/                     # Pinia 状态管理
        │   └── user.js                # 用户状态
        │
        └── pages/                     # 页面组件
            ├── Dashboard.vue          # 仪表盘
            ├── Skills.vue             # 技能管理
            ├── Memory.vue             # 记忆管理
            ├── Models.vue             # 模型配置
            ├── Feishu.vue             # 飞书集成
            ├── Gateway.vue            # 网关监控
            ├── Admin.vue              # 权限管理
            └── Login.vue              # 登录页面
```

---

## 核心模块说明

### 后端模块

#### 1. `core/agent/` - DeepAgent 智能体封装
- **功能**: 基于 LangChain DeepAgents 的核心智能体实现
- **核心类**: `MiniClawAgent`
- **职责**: 任务规划、技能调度、记忆检索、模型调用

#### 2. `core/skills/` - 技能管理模块
- **功能**: 技能的标准化定义、注册、加载、执行
- **核心类**: `SkillBase`, `SkillManager`
- **特性**: 支持热插拔、权限绑定、参数验证

#### 3. `core/memory/` - 记忆管理模块
- **功能**: 永久记忆的存储、检索、优化
- **核心类**: `MemoryManager`, `MemoryRecord`
- **特性**: 分级存储、向量检索、重要性评分、自动清理

#### 4. `core/model/` - 模型适配模块
- **功能**: 多模型统一适配与调度
- **核心类**: `ModelAdapter`, `ModelManager`
- **支持**: Ollama 本地模型、OpenAI 兼容接口

#### 5. `core/feishu/` - 飞书集成模块
- **功能**: 飞书机器人消息收发与事件处理
- **核心类**: `FeishuAdapter`, `FeishuCommandParser`
- **特性**: 消息加密、指令解析、身份映射

#### 6. `core/gateway/` - 网关模块
- **功能**: 统一请求入口、限流、日志、鉴权
- **核心类**: `GatewayManager`, `RateLimiter`
- **算法**: Redis 令牌桶限流

#### 7. `core/auth/` - RBAC 权限管理
- **功能**: 用户认证、角色管理、权限控制
- **核心类**: `AuthManager`, `User`, `Role`
- **机制**: JWT 无状态认证、细粒度权限

#### 8. `db/` - 数据库模块
- **功能**: ORM 模型定义、数据库初始化
- **技术**: SQLAlchemy Async
- **表结构**: users, roles, skills, memories, model_configs 等

---

### 前端模块

#### 1. `src/api/` - API 请求封装
- **request.js**: Axios 实例配置、拦截器、错误处理
- **skills.js**: Skills 相关 API 封装

#### 2. `src/router/` - 路由配置
- **功能**: Vue Router 配置、路由守卫
- **页面**: Dashboard, Skills, Memory, Models, Feishu, Gateway, Admin, Login

#### 3. `src/store/` - 状态管理
- **user.js**: 用户登录状态、权限管理

#### 4. `src/pages/` - 页面组件
- **Dashboard.vue**: 系统概览、快速开始、系统状态
- **Skills.vue**: 技能列表、启用/禁用、执行、卸载
- **Memory.vue**: 记忆列表、搜索、删除、重要性查看
- **Models.vue**: 模型配置、测试、删除
- **Feishu.vue**: 飞书配置、连接测试、状态查看
- **Gateway.vue**: 请求统计、日志查看、监控面板
- **Admin.vue**: 用户管理、角色管理、权限分配
- **Login.vue**: 登录表单、身份验证

---

## 配置文件说明

### 1. `.env.example` - 环境变量模板
包含所有必需的配置项：
- 服务配置（HOST, PORT）
- 数据库配置（DATABASE_URL, REDIS_*）
- JWT 配置（JWT_SECRET_KEY, JWT_ALGORITHM）
- 模型配置（DEFAULT_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY）
- 飞书配置（FEISHU_APP_ID, FEISHU_APP_SECRET 等）

### 2. `docker-compose.yml` - Docker 编排
定义三个服务：
- `backend`: FastAPI 后端服务
- `frontend`: Vue 前端 + Nginx
- `redis`: Redis 缓存服务

### 3. `requirements.txt` - Python 依赖
核心依赖：
- langchain, langgraph, deepagents
- fastapi, uvicorn
- sqlalchemy, aiosqlite, redis
- PyJWT, passlib
- lark-oapi (飞书 SDK)

### 4. `package.json` - Node.js 依赖
核心依赖：
- vue, vue-router, pinia
- element-plus (UI 组件库)
- axios (HTTP 客户端)
- vite (构建工具)

---

## 数据流向

### 典型请求流程

```
用户请求
  ↓
Nginx (前端静态资源 / API 代理)
  ↓
FastAPI Gateway (鉴权、限流、日志)
  ↓
Router (路由分发)
  ↓
Controller (业务逻辑)
  ↓
Core Module (技能/记忆/模型)
  ↓
Database / Redis (持久化/缓存)
  ↓
Response (统一格式返回)
```

### 技能执行流程

```
用户指令 (飞书/Web)
  ↓
指令解析 (/skill_name args)
  ↓
权限验证 (RBAC)
  ↓
SkillManager 查找技能
  ↓
Skill.execute() 执行
  ↓
Memory 记录执行历史
  ↓
返回结果
```

---

## 扩展点

### 技能扩展
1. 在 `core/skills/builtin/` 创建新技能类
2. 继承 `SkillBase` 基类
3. 实现 `execute()` 方法
4. 在技能管理器中注册

### 模型扩展
1. 在 `core/model/` 创建新的 Adapter 类
2. 继承 `ModelAdapter` 基类
3. 实现 `chat()` 和 `generate_embedding()` 方法
4. 在 ModelManager 中添加 provider 识别逻辑

### 权限扩展
1. 在 `core/auth/` 的 `PermissionType` 枚举中添加新权限
2. 在对应角色的 `permissions` 列表中添加权限
3. 在业务代码中进行权限检查

---

## 下一步开发建议

### 优先级 P0 (核心功能)
- [ ] 完成所有 API 接口的实现
- [ ] 实现数据库 CRUD 操作
- [ ] 完善 JWT 认证流程
- [ ] 实现技能执行引擎
- [ ] 完成飞书消息回调处理

### 优先级 P1 (重要功能)
- [ ] 实现向量记忆检索
- [ ] 完善 RBAC 权限检查
- [ ] 实现网关限流算法
- [ ] 添加更多内置技能
- [ ] 完善前端页面交互

### 优先级 P2 (优化增强)
- [ ] 添加 WebSocket 实时通信
- [ ] 实现技能市场
- [ ] 添加记忆可视化展示
- [ ] 实现多飞书机器人支持
- [ ] 添加性能监控

### 优先级 P3 (高级功能)
- [ ] 实现 Agent 自演进
- [ ] 添加多模态处理能力
- [ ] 实现技能组合工作流
- [ ] 添加对话历史管理
- [ ] 实现个性化 AI 人格
