"""
MiniClaw 后端服务入口 - 基于 LangChain DeepAgents

核心架构：
- DeepAgent: 智能体核心
- Skills: 通过 SKILL.md 定义的能力（文件系统方式）
- Memory: 永久记忆存储
- FastAPI: Web 服务层

本地模式：无需登录认证，模型配置由前端传入
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from config import settings
from api.v1 import router as api_router_v1


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
)


def create_application() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="MiniClaw - 轻量化 OpenClaw 智能体网关（本地模式）",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"全局异常：{exc}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"服务器内部错误：{str(exc)}",
                "data": None,
            },
        )
    
    return app


app = create_application()


@app.on_event("startup")
async def startup_event():
    """服务启动时执行"""
    logger.info("🚀 MiniClaw 服务启动中...（本地模式）")
    
    # 初始化 DeepAgent（带 Skills）
    from core.skills import initialize_skills_system, get_available_skills, get_skills_system_prompt
    from core.agent import MiniClawAgent, AgentConfig
    
    try:
        create_agent, skills_files, skills_dir, skills_info = initialize_skills_system()
        
        # 准备 files 参数（DeepAgent 原生格式）
        from deepagents.backends.utils import create_file_data
        
        files_dict = None
        if skills_files:
            files_dict = {
                path: create_file_data(data["content"])
                for path, data in skills_files.items()
            }
            logger.info(f"📦 加载了 {len(files_dict)} 个 SKILL.md 文件")
        
        # 生成系统提示词（包含技能描述）
        system_prompt = get_skills_system_prompt(skills_info)
        logger.info(f"📝 系统提示词：{system_prompt[:200]}...")
        
        # 创建 Agent 配置 - 使用 NIO DeepSeek 模型
        agent_config = AgentConfig(
            model=f"nio:DeepSeek-V3.1",  # 使用 NIO 模型
            enable_memory=True,
            system_prompt=system_prompt,
        )
        
        # 创建全局 Agent 实例
        agent = MiniClawAgent(agent_config)
        agent.initialize(skills_files=files_dict)
        
        # 存储到 app.state 供 Chat API 使用
        app.state.agent = agent
        app.state.skills_files = files_dict
        app.state.skills_dir = skills_dir
        app.state.skills_info = skills_info  # 存储技能信息
        
        logger.info("✅ DeepAgent 初始化完成（带 Skills）")
        
    except Exception as e:
        logger.warning(f"⚠️ DeepAgent 初始化失败：{e}，将使用基础模式")
        import traceback
        traceback.print_exc()
        app.state.agent = None
        app.state.skills_files = None
        app.state.skills_info = []
    
    logger.info("✅ MiniClaw 服务启动完成（本地模式）")


@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时执行"""
    logger.info("🛑 MiniClaw 服务正在关闭...")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用 MiniClaw - 轻量化 OpenClaw 智能体网关（本地模式）",
        "version": settings.VERSION,
        "docs": "/docs",
        "mode": "local",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "mode": "local",
    }


# 注册 API 路由
app.include_router(api_router_v1, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )