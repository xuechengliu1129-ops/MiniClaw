# MiniClaw 部署指南

## 环境要求

- **操作系统**: Linux / macOS / Windows (WSL2)
- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 20.10+ (可选，用于容器化部署)
- **Redis**: 6.0+ (可选，用于缓存和限流)

---

## 方式一：本地开发环境部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd MiniClaw
```

### 2. 后端部署

#### 2.1 创建虚拟环境
```bash
cd backend
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 配置环境变量
```bash
cp ../.env.example .env
```

编辑 `.env` 文件，配置必要参数：
```env
# 基础配置
DEBUG=True
PORT=8000

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./miniclaw.db

# Redis（可选）
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT 认证
JWT_SECRET_KEY=your-secret-key-change-in-production

# 模型配置（根据需求选择）
# Ollama 本地模型
DEFAULT_MODEL=ollama/llama2
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 兼容模型
# DEFAULT_MODEL=openai/gpt-3.5-turbo
# OPENAI_API_KEY=sk-xxx
```

#### 2.4 初始化数据库
```bash
python -c "from db import init_database; import asyncio; asyncio.run(init_database('sqlite+aiosqlite:///./miniclaw.db'))"
```

#### 2.5 启动服务
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看 API 文档

---

### 3. 前端部署

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 启动开发服务器
```bash
npm run dev
```

访问 `http://localhost:5173`

#### 3.3 生产构建
```bash
npm run build
```

---

## 方式二：Docker Compose 一键部署（推荐）

### 1. 准备工作

确保已安装 Docker 和 Docker Compose：
```bash
docker --version
docker-compose --version
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要参数。

### 3. 启动所有服务

```bash
docker-compose up -d
```

查看服务状态：
```bash
docker-compose ps
```

查看日志：
```bash
docker-compose logs -f
```

### 4. 停止服务

```bash
docker-compose down
```

### 5. 清理数据（谨慎使用）

```bash
docker-compose down -v  # 删除所有数据卷
```

---

## 方式三：Ollama 本地模型部署

### 1. 安装 Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 下载安装程序：https://ollama.com/download/windows
```

### 2. 拉取模型

```bash
ollama pull llama2
```

### 3. 验证模型

```bash
ollama run llama2 "你好"
```

### 4. 配置 MiniClaw

在 `.env` 文件中配置：
```env
DEFAULT_MODEL=ollama/llama2
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 飞书机器人配置

### 1. 创建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录企业账号
3. 点击「创建应用」
4. 选择「企业自建应用」
5. 填写应用名称、图标等信息

### 2. 获取凭证

在「凭证与基础信息」页面获取：
- App ID
- App Secret
- Verification Token

### 3. 配置权限

在「权限管理」页面添加：
- 机器人能力：发送消息、接收消息
- 群组读写权限

### 4. 订阅事件

在「事件订阅」页面：
1. 配置订阅地址：`http://your-domain/api/v1/feishu/event`
2. 订阅事件：`im.message`（接收消息）
3. 复制 Encrypt Key（如果启用加密）

### 5. 发布应用

在「版本管理与发布」页面提交审核并发布

### 6. 配置到 MiniClaw

在 `.env` 文件中配置：
```env
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxx (可选)
```

---

## 生产环境部署建议

### 1. 安全配置

- 修改 `JWT_SECRET_KEY` 为强随机字符串
- 启用 HTTPS（使用 Nginx 反向代理）
- 配置防火墙规则
- 定期更新依赖包

### 2. 性能优化

- 使用 PostgreSQL 替代 SQLite（大数据量场景）
- 配置 Redis 集群（高并发场景）
- 启用 Gzip 压缩
- 配置 CDN 加速静态资源

### 3. 监控告警

- 配置日志收集（ELK Stack）
- 监控系统资源（Prometheus + Grafana）
- 设置告警规则（邮件/短信/飞书通知）

### 4. 备份策略

- 数据库每日自动备份
- 配置文件版本控制
- 定期测试恢复流程

---

## 常见问题

### Q1: 后端启动失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**: 
```bash
pip install -r requirements.txt --upgrade
```

### Q2: 前端无法连接后端

**问题**: 浏览器控制台显示 CORS 错误

**解决**: 
检查 `.env` 中的 `CORS_ORIGINS` 配置，确保包含前端地址

### Q3: Ollama 模型调用超时

**问题**: 请求长时间无响应

**解决**:
1. 检查 Ollama 服务是否运行：`ollama list`
2. 增加超时时间配置
3. 使用更小的模型

### Q4: Redis 连接失败

**问题**: `redis.exceptions.ConnectionError`

**解决**:
1. 检查 Redis 服务是否启动
2. 验证 `.env` 中的 Redis 配置
3. 检查防火墙规则

---

## 技术支持

- GitHub Issues: https://github.com/your-repo/miniclaw/issues
- 官方文档：https://docs.miniclaw.ai
- 社区论坛：https://community.miniclaw.ai
