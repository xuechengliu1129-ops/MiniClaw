"""
DeepAgent 智能体封装模块 - 基于 LangChain DeepAgents

核心功能：
- 使用 create_deep_agent 创建智能体
- 支持 Skills（通过 SKILL.md 文件系统）
- 支持 Memory（通过 Checkpointer）
- 支持多模型适配
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from loguru import logger


class AgentConfig(BaseModel):
    """智能体配置"""
    model: str = Field(default="anthropic:claude-sonnet-4-5", description="模型名称")
    skills_dirs: List[str] = Field(default_factory=list, description="Skills 目录列表")
    enable_memory: bool = Field(default=True, description="是否启用记忆")
    system_prompt: Optional[str] = Field(default=None, description="系统提示词")


class MiniClawAgent:
    """MiniClaw 智能体 - 基于 DeepAgents 封装"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化智能体
        
        Args:
            config: 智能体配置
        """
        self.config = config or AgentConfig()
        self.agent = None
        self.checkpointer = None
        self.skills_files = {}
        
    def initialize(self, skills_files: Optional[Dict[str, Any]] = None):
        """
        初始化智能体（加载技能、记忆）
        
        Args:
            skills_files: Skills 文件内容 {path: content}
        """
        try:
            logger.info("🤖 初始化 DeepAgent...")
            
            # 1. 创建 Checkpointer（用于记忆）
            if self.config.enable_memory:
                self.checkpointer = MemorySaver()
                logger.info("✅ 记忆系统已启用")
            
            # 2. 保存 Skills 文件（供后续 invoke 使用）
            if skills_files:
                self.skills_files = skills_files
                logger.info(f"✅ 加载了 {len(skills_files)} 个 Skills")
            
            # 3. 创建 DeepAgent
            from deepagents.backends.utils import create_file_data
            
            # 准备 files 参数（DeepAgent 原生格式）
            files_dict = None
            if self.skills_files:
                files_dict = {
                    path: create_file_data(content)
                    for path, content in self.skills_files.items()
                }
            
            # 解析模型配置
            # 格式："nio:DeepSeek-V3.1" -> provider="nio", model_name="DeepSeek-V3.1"
            model_parts = self.config.model.split(":", 1)
            if len(model_parts) == 2:
                provider, model_name = model_parts
            else:
                provider = "anthropic"
                model_name = self.config.model
            
            # 对于 NIO 模型，使用特殊的处理方式
            if provider.lower() == "nio":
                logger.info(f"🔧 使用 NIO 模型：{model_name}")
                # 创建一个简化的 Agent，直接使用 NIOCompatibleChatModel
                from langgraph.graph import StateGraph, END
                from langchain_core.messages import HumanMessage, SystemMessage
                from typing import TypedDict, List, Dict
                
                class AgentState(TypedDict):
                    """Agent 状态"""
                    messages: List[Dict]
                    response: str
                
                def chat_node(state: AgentState) -> AgentState:
                    """聊天节点"""
                    try:
                        logger.info(f"调用 NIO 模型：{model_name}")
                        
                        # 直接使用 httpx 同步调用 NIO API
                        import httpx
                        
                        # 构建消息
                        messages = state["messages"]
                        
                        # 添加系统提示词
                        if self.config.system_prompt:
                            messages.insert(0, {
                                "role": "system",
                                "content": self.config.system_prompt
                            })
                        
                        logger.info(f"发送请求到 NIO API，消息数：{len(messages)}")
                        
                        # 发送请求到 NIO API
                        response = httpx.post(
                            url="https://modelgateway.nioint.com/publicService/v1/chat/completions",
                            headers={
                                "Authorization": "Bearer a7425832-75a5-4f53-853c-44fad94bf4a7",
                                "Content-Type": "application/json",
                            },
                            json={
                                "model": model_name,
                                "messages": messages,
                                "temperature": 0.7,
                                "max_tokens": 2048,
                                "stream": False,
                            },
                            timeout=60.0,
                        )
                        
                        # 检查响应状态
                        if response.status_code != 200:
                            logger.error(f"NIO API 返回错误：{response.status_code}")
                            logger.error(f"响应内容：{response.text}")
                            response.raise_for_status()
                        
                        data = response.json()
                        logger.info(f"NIO API 响应：{data}")
                        
                        # 提取回复内容
                        content = ""
                        if data.get("choices") and len(data["choices"]) > 0:
                            choice = data["choices"][0]
                            if choice.get("message"):
                                content = choice["message"].get("content", "")
                        
                        logger.info(f"NIO 模型回复：{content[:100] if content else '无内容'}...")
                        
                        return {"response": content}
                    except Exception as e:
                        logger.error(f"NIO 模型调用失败：{e}")
                        raise
                
                # 构建 Agent Graph
                workflow = StateGraph(AgentState)
                workflow.add_node("chat", chat_node)
                workflow.set_entry_point("chat")
                workflow.add_edge("chat", END)
                
                # 编译并添加 checkpointer
                self.agent = workflow.compile(checkpointer=self.checkpointer)
                
            else:
                # 使用标准的 DeepAgents 创建方式
                self.agent = create_deep_agent(
                    model=self.config.model,
                    checkpointer=self.checkpointer,
                    system_prompt=self.config.system_prompt,
                )
            
            # 存储 files 到实例变量（在 invoke 时使用）
            self.files_dict = files_dict
            
            logger.info("✅ DeepAgent 初始化完成")
            
        except Exception as e:
            logger.error(f"❌ DeepAgent 初始化失败：{e}")
            raise
    
    def invoke(self, message: str, thread_id: str = "default", **kwargs) -> Dict[str, Any]:
        """
        调用智能体执行任务
        
        Args:
            message: 用户消息
            thread_id: 会话 ID（用于记忆）
            **kwargs: 其他参数
            
        Returns:
            Dict: 执行结果
        """
        if not self.agent:
            raise RuntimeError("智能体未初始化，请先调用 initialize()")
        
        try:
            # 兼容 message 为字符串或字典的情况
            if isinstance(message, dict):
                message_content = message.get("content", "")
            else:
                message_content = message
            
            logger.info(f"💬 收到消息：{message_content[:50] if len(message_content) > 50 else message_content}...")
            
            # 构建 invoke 参数
            invoke_params = {
                "messages": [
                    {
                        "role": "user",
                        "content": message_content,
                    }
                ],
            }
            
            # 添加 Skills 文件（如果有）
            if self.files_dict:
                invoke_params["files"] = self.files_dict
            
            # 调用 Agent
            result = self.agent.invoke(
                invoke_params,
                config={
                    "configurable": {
                        "thread_id": thread_id,
                    }
                }
            )
            
            # 提取回复 - 兼容不同 Agent 的返回格式
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
            
            logger.info(f"✅ 智能体回复：{response_text[:100] if len(response_text) > 100 else response_text}...")
            
            return {
                "response": response_text,
                "thread_id": thread_id,
                "model_used": self.config.model,
            }
            
        except Exception as e:
            logger.error(f"❌ 智能体执行失败：{e}")
            raise
    
    async def ainvoke(self, message: str, thread_id: str = "default", **kwargs) -> Dict[str, Any]:
        """
        异步调用智能体
        
        Args:
            message: 用户消息
            thread_id: 会话 ID
            **kwargs: 其他参数
            
        Returns:
            Dict: 执行结果
        """
        # TODO: 实现异步版本
        # 目前先同步调用
        return self.invoke(message, thread_id, **kwargs)
    
    def chat(self, message: str, thread_id: str = "default") -> str:
        """
        对话接口（简化版）
        
        Args:
            message: 用户消息
            thread_id: 会话 ID
            
        Returns:
            str: 回复消息
        """
        result = self.invoke(message, thread_id)
        return result["response"]


# 全局智能体实例（懒加载）
_agent_instance: Optional[MiniClawAgent] = None


def get_agent(config: Optional[AgentConfig] = None) -> MiniClawAgent:
    """
    获取智能体实例（单例模式）
    
    Args:
        config: 智能体配置
        
    Returns:
        MiniClawAgent: 智能体实例
    """
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = MiniClawAgent(config)
    
    return _agent_instance


def create_agent(config: Optional[AgentConfig] = None) -> MiniClawAgent:
    """
    创建新的智能体实例
    
    Args:
        config: 智能体配置
        
    Returns:
        MiniClawAgent: 智能体实例
    """
    return MiniClawAgent(config)