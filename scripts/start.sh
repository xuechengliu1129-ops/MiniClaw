#!/bin/bash

# MiniClaw 快速启动脚本
# 用于本地开发环境一键启动

set -e

echo "🦞 MiniClaw 快速启动脚本"
echo "========================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo "📋 检查环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Python 3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python 版本：$PYTHON_VERSION${NC}"

# 检查 Node.js 版本
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Node.js${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js 版本：$NODE_VERSION${NC}"

echo ""

# 后端设置
echo "🔧 配置后端环境..."
cd backend

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "创建环境变量配置..."
    cp ../.env.example .env
    echo -e "${YELLOW}⚠️  请编辑 backend/.env 文件配置必要参数${NC}"
fi

echo -e "${GREEN}✅ 后端环境准备完成${NC}"
echo ""

# 前端设置
echo "🎨 配置前端环境..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

if [ ! -f ".env" ]; then
    echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env
fi

echo -e "${GREEN}✅ 前端环境准备完成${NC}"
echo ""

# 启动服务
echo "🚀 启动服务..."
echo ""

# 启动后端（后台运行）
cd ../backend
echo "启动后端服务..."
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo "访问 API 文档：http://localhost:8000/docs"
echo ""

# 启动前端
cd ../frontend
echo "启动前端服务..."
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo "访问前端页面：http://localhost:5173"
echo ""

echo "========================="
echo "✨ MiniClaw 已成功启动!"
echo ""
echo "停止服务请按 Ctrl+C"
echo "或者运行：kill $BACKEND_PID $FRONTEND_PID"
echo ""

# 等待用户中断
wait
