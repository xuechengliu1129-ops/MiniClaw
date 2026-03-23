#!/bin/bash

# MiniClaw 一键启动脚本（修复版）
# 解决 localhost DNS 解析问题

set -e

echo "🦞 MiniClaw 一键启动脚本"
echo "========================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Python 3${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python: $(python3 --version)${NC}"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Node.js${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 npm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm: $(npm --version)${NC}"

echo ""
echo "📦 步骤 1/4: 准备后端环境..."
echo ""

cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📋 创建 Python 虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo -e "${BLUE}📦 安装 Python 依赖...${NC}"
pip install -q -r requirements.txt

# 创建数据目录
mkdir -p data logs

echo -e "${GREEN}✅ 后端环境准备完成${NC}"
echo ""

echo "🎨 步骤 2/4: 准备前端环境..."
echo ""

cd ../frontend

# 安装依赖（如果未安装）
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 安装 Node.js 依赖...${NC}"
    npm install
fi

echo -e "${GREEN}✅ 前端环境准备完成${NC}"
echo ""

echo "🚀 步骤 3/4: 启动后端服务..."
echo ""

cd ../backend
source venv/bin/activate

# 后台启动后端
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

sleep 3

# 检查后端是否启动成功
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}📖 API 文档：http://127.0.0.1:8000/docs${NC}"
    echo -e "${BLUE}📖 健康检查：http://127.0.0.1:8000/health${NC}"
else
    echo -e "${RED}❌ 后端启动失败，请查看日志：logs/backend.log${NC}"
    exit 1
fi

echo ""
echo "🎨 步骤 4/4: 启动前端服务..."
echo ""

cd ../frontend

# 前台启动前端（显示输出）
echo -e "${BLUE}🌐 启动前端开发服务器...${NC}"
echo ""
echo "========================="
echo "✨ MiniClaw 已成功启动!"
echo "========================="
echo ""
echo -e "${GREEN}前端地址：http://127.0.0.1:5173${NC}"
echo -e "${GREEN}后端地址：http://127.0.0.1:8000${NC}"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 启动前端（会显示在终端）
npm run dev
