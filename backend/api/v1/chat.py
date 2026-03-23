"""
Chat API - 基于 DeepAgents 的智能对话

核心逻辑：
- 直接使用 DeepAgent 进行推理
- 自动调用已加载的 Skills（通过文件系统）
- 支持多轮对话和记忆
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from db.models import ModelConfig

router = APIRouter(prefix="/chat", tags=["智能对话"])


class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    """对话响应"""
    response: str
    thread_id: str
    model_used: str


# ==================== 简化的会话管理（内存存储） ====================

# 临时存储会话数据（重启后清空）
CHAT_SESSIONS = {
    "default": {
        "id": "default",
        "title": "默认会话",
        "created_at": datetime.now().isoformat(),
        "messages": [],
    }
}


@router.get("/sessions", response_model=List[dict])
async def get_chat_sessions():
    """获取所有会话列表"""
    sessions = [
        {
            "id": session_id,
            "title": data["title"],
            "lastTime": data["created_at"],
        }
        for session_id, data in CHAT_SESSIONS.items()
    ]
    return sessions


@router.get("/sessions/{session_id}/history", response_model=List[dict])
async def get_session_history(session_id: str):
    """获取指定会话的历史消息"""
    if session_id not in CHAT_SESSIONS:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return CHAT_SESSIONS[session_id]["messages"]


@router.post("/sessions", response_model=dict)
async def create_chat_session(request: dict):
    """创建新会话"""
    import uuid
    
    session_id = str(uuid.uuid4())
    title = request.get("title", f"新会话 {datetime.now().strftime('%m-%d %H:%M')}")
    
    CHAT_SESSIONS[session_id] = {
        "id": session_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "messages": [],
    }
    
    return {
        "id": session_id,
        "title": title,
        "created_at": CHAT_SESSIONS[session_id]["created_at"],
    }


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """删除会话"""
    if session_id not in CHAT_SESSIONS:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    del CHAT_SESSIONS[session_id]
    return {"message": f"会话 {session_id} 已删除"}


# ==================== 对话接口 ====================

def create_model_instance(provider: str, api_key: Optional[str], model_name: str):
    """
    根据 provider 动态创建 LangChain 模型实例
    
    Args:
        provider: 模型提供商 (anthropic, openai, gemini, ollama)
        api_key: API Key（Ollama 不需要）
        model_name: 模型名称
    
    Returns:
        LangChain 的 BaseChatModel 实例
    """
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        if not api_key:
            raise ValueError("Anthropic 需要提供 API Key")
        return ChatAnthropic(
            model=model_name,
            api_key=api_key,
        )
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        if not api_key:
            raise ValueError("OpenAI 需要提供 API Key")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
        )
    
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not api_key:
            raise ValueError("Google Gemini 需要提供 API Key")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
        )
    
    elif provider == "ollama":
        from core.model.ollama_adapter import OllamaAdapter
        # Ollama 是本地服务，不需要 API Key
        adapter = OllamaAdapter()
        # 创建一个简单的包装器来适配 LangChain 接口
        return adapter.get_langchain_model(model_name)
    
    elif provider.lower() in ["nio", "openai_compatible"]:
        # NIO 或其他 OpenAI 兼容的服务 - 使用自定义包装器处理特殊响应格式
        from core.model.openai_adapter import NIOCompatibleChatModel
        if not api_key:
            raise ValueError("NIO/OpenAI 兼容服务需要提供 API Key")
        
        # 使用自定义的 NIO 兼容模型包装器
        base_url = "https://modelgateway.nioint.com/publicService/v1" if provider.lower() == "nio" else None
        if not base_url:
            raise ValueError("OpenAI 兼容服务需要提供 base_url")
        
        return NIOCompatibleChatModel(
            api_key=api_key,
            model=model_name,
            base_url=base_url,
        )
    
    else:
        raise ValueError(f"不支持的模型提供商：{provider}")


@router.post("/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    智能对话接口（使用全局 DeepAgent + Skills）
    
    流程：
    1. 接收用户消息
    2. 优先使用全局 Agent（如果已初始化）
    3. 调用 Agent 进行推理（自动选择合适的 Skills）
    4. 返回 Agent 的最终回复
    """
    try:
        from main import app
        
        # 优先使用全局 Agent（如果已初始化）
        agent = getattr(app.state, 'agent', None)
        
        if not agent:
            # 如果 Agent 未初始化，尝试动态创建
            logger.warning("⚠️ 全局 Agent 未初始化，尝试动态创建")
            return ChatResponse(
                response="⚠️ DeepAgent 未初始化，无法执行对话。请检查后端日志。",
                thread_id=request.thread_id,
                model_used="none",
            )
        
        logger.info(f"💬 用户消息：{request.message}")
        
        # 获取技能信息（用于在对话中展示）
        skills_info = getattr(app.state, 'skills_info', [])
        
        # 构建 invoke 参数（参考官方示例）
        invoke_params = {
            "messages": [
                {
                    "role": "user",
                    "content": request.message,
                }
            ],
        }
        
        # 如果有 Skills，添加 files 参数
        skills_files = getattr(app.state, 'skills_files', None)
        if skills_files:
            invoke_params["files"] = skills_files
        
        # 调用 DeepAgent
        result = agent.invoke(
            invoke_params,
            config={
                "configurable": {
                    "thread_id": request.thread_id,
                }
            }
        )
        
        # 提取 Agent 回复
        if isinstance(result, dict):
            # NIO 模型返回 {"messages": [...], "response": "..."}
            response_text = result.get("response", "")
            if not response_text:
                # 如果没有 response 字段，尝试从 messages 提取
                if result.get("messages") and len(result["messages"]) > 0:
                    last_msg = result["messages"][-1]
                    response_text = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                else:
                    response_text = "未收到回复"
        elif hasattr(result, 'content'):
            # LangChain AIMessage 对象
            response_text = result.content
        else:
            # 其他情况
            response_text = str(result)
        
        logger.info(f"✅ Agent 回复：{response_text[:100]}...")
        
        # 保存消息到会话
        if request.thread_id not in CHAT_SESSIONS:
            CHAT_SESSIONS[request.thread_id] = {
                "id": request.thread_id,
                "title": f"会话 {request.thread_id}",
                "created_at": datetime.now().isoformat(),
                "messages": [],
            }
        
        CHAT_SESSIONS[request.thread_id]["messages"].append({
            "role": "user",
            "content": request.message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        CHAT_SESSIONS[request.thread_id]["messages"].append({
            "role": "assistant",
            "content": response_text,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        
        return ChatResponse(
            response=response_text,
            thread_id=request.thread_id,
            model_used="global_agent",
        )
        
    except Exception as e:
        logger.error(f"❌ 对话失败：{str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"对话处理失败：{str(e)}"
        )


def create_agent_for_model(provider: str, api_key: Optional[str], model_name: str, app) -> any:
    """
    为指定的模型配置创建 Agent（简化版，无 checkpointer）
    
    Args:
        provider: 模型提供商
        api_key: API Key
        model_name: 模型名称
        app: FastAPI 应用实例
    
    Returns:
        编译后的 DeepAgent 实例
    """
    from langchain_core.language_models import BaseChatModel
    from deepagents import create_deep_agent
    
    # 1. 创建模型实例
    model_instance = create_model_instance(provider, api_key, model_name)
    
    # 2. 对于 NIO 等特殊 provider，直接使用自定义的包装器，不经过 deepagents
    if provider.lower() in ["nio", "openai_compatible"]:
        # 创建一个简化的 Agent，直接使用 NIOCompatibleChatModel
        from langgraph.graph import StateGraph, END
        from langchain_core.messages import HumanMessage, SystemMessage
        from typing import TypedDict, List, Dict
        from loguru import logger
        
        class AgentState(TypedDict):
            """Agent 状态"""
            messages: List[Dict]
            response: str
        
        def chat_node(state: AgentState) -> AgentState:
            """聊天节点"""
            try:
                # 转换消息格式 - 正确处理 LangChain 消息对象
                messages = []
                for msg in state["messages"]:
                    if isinstance(msg, dict):
                        messages.append(msg)
                    elif hasattr(msg, 'type') and hasattr(msg, 'content'):
                        # LangChain 消息对象
                        role_map = {
                            'human': 'user',
                            'ai': 'assistant',
                            'system': 'system'
                        }
                        role = role_map.get(getattr(msg, 'type', 'user'), 'user')
                        messages.append({"role": role, "content": msg.content})
                    else:
                        messages.append({"role": "user", "content": str(msg)})
                
                # 确保有 system message
                if not messages or messages[0].get("role") != "system":
                    messages.insert(0, {"role": "system", "content": "你是一个有用的 AI 助手。"})
                
                # 调用模型
                logger.info(f"调用 NIO 模型：{model_name}")
                logger.debug(f"消息列表：{messages}")
                result = model_instance.invoke(messages)
                
                # 提取回复内容
                response_text = result.content if hasattr(result, 'content') else str(result)
                logger.info(f"NIO 模型回复：{response_text[:100]}...")
                
                return {"messages": state["messages"], "response": response_text}
                
            except Exception as e:
                logger.error(f"NIO 模型调用失败：{e}")
                import traceback
                traceback.print_exc()
                return {"messages": state["messages"], "response": f"调用失败：{str(e)}"}
        
        # 构建简单的图
        workflow = StateGraph(AgentState)
        workflow.add_node("chat", chat_node)
        workflow.set_entry_point("chat")
        workflow.add_edge("chat", END)
        
        agent = workflow.compile()
        logger.info(f"✅ NIO Agent 创建成功：{provider}:{model_name}")
        return agent
    
    # 3. 对于其他 provider，使用标准的 deepagents 创建
    agent = create_deep_agent(
        model=model_instance,
        system_prompt="你是一个有用的 AI 助手。",
    )
    
    logger.info(f"✅ Agent 创建成功：{provider}:{model_name}")
    return agent
