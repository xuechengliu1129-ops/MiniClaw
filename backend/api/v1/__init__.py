"""
API v1 路由模块 - 统一导出所有路由
"""
from fastapi import APIRouter
from . import chat, models, skills

router = APIRouter()

# 注册所有子路由
router.include_router(chat.router)
router.include_router(models.router)
router.include_router(skills.router)

# 健康检查接口
@router.get("/ping")
async def ping():
    """健康检查"""
    return {"message": "pong", "status": "ok"}


@router.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "project": "MiniClaw",
    }