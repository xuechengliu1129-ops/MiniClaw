"""
OpenAI API 兼容模型适配器
支持 NIO公司及其他 OpenAI 兼容的 API 接口
"""
import httpx
import json
from typing import List, Dict, Optional, Any
from loguru import logger

from . import ModelAdapter, ModelConfig, ModelResponse


class NIOCompatibleChatModel:
    """
    NIO 兼容的 Chat 模型包装器
    处理 NIO API 返回的非标准格式
    """
    
    def __init__(self, api_key: str, model: str, base_url: str):
        """
        初始化 NIO 兼容模型
        
        Args:
            api_key: API Key
            model: 模型名称
            base_url: Base URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
        # 创建 HTTP 客户端，禁用环境变量中的代理设置
        self.client = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=10.0),
            trust_env=False,  # 禁用系统代理
        )
        
        logger.info(f"NIO 兼容模型初始化完成：{model} @ {base_url}")
    
    def invoke(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Any:
        """
        同步调用接口（LangChain 需要）
        
        Args:
            messages: LangChain 格式的消息列表
            **kwargs: 其他参数
            
        Returns:
            AIMessage: LangChain 格式的 AI 响应消息
        """
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        
        # 转换 LangChain 消息为标准格式
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                formatted_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_messages.append({"role": "assistant", "content": msg.content})
            else:
                # 通用处理
                role = getattr(msg, 'type', 'user')
                content = getattr(msg, 'content', str(msg))
                formatted_messages.append({"role": role, "content": content})
        
        try:
            # 构建请求体
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "stream": False,
            }
            
            # 添加可选参数
            if "top_p" in kwargs:
                payload["top_p"] = kwargs["top_p"]
            
            # 发送请求
            response = self.client.post(
                url=f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            # 检查响应状态
            response.raise_for_status()
            data = response.json()
            
            # 调试日志：打印完整响应
            logger.info(f"NIO API 响应状态码：{response.status_code}")
            logger.info(f"NIO API 响应完整数据：{json.dumps(data, ensure_ascii=False)}")
            
            # 提取回复内容 - 兼容多种格式
            content = None
            
            # 标准 OpenAI 格式
            if data.get("choices") and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if choice.get("message"):
                    content = choice["message"].get("content")
                    logger.info(f"使用 choices[0].message.content 作为回复")
                elif choice.get("delta"):
                    content = choice["delta"].get("content")
                    logger.info(f"使用 choices[0].delta.content 作为回复")
            
            # 如果 choices 为空或 null，尝试其他字段
            if not content:
                logger.warning(f"choices 字段为空或未找到，尝试其他字段")
                # 尝试直接从 result 字段获取
                if data.get("result"):
                    content = data["result"]
                    logger.warning(f"使用 result 字段作为回复内容")
                # 尝试从 display_msg 获取
                elif data.get("display_msg"):
                    content = data["display_msg"]
                    logger.warning(f"使用 display_msg 作为回复内容")
            
            if not content:
                logger.error(f"NIO API 返回异常数据：{data}")
                content = "抱歉，模型返回的数据格式异常，无法解析回复内容。"
            
            # 创建 LangChain 的 AIMessage
            return AIMessage(content=content)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 错误：{e.response.status_code} - {e.response.text}")
            return AIMessage(content=f"请求失败：HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"请求错误：{str(e)}")
            return AIMessage(content=f"网络请求失败：{str(e)}")
        except Exception as e:
            logger.error(f"未知错误：{str(e)}")
            return AIMessage(content=f"处理失败：{str(e)}")
    
    def __del__(self):
        """析构函数，关闭客户端"""
        try:
            self.client.close()
        except:
            pass


class OpenAIAdapter(ModelAdapter):
    """OpenAI API 兼容适配器（支持 NIO 等第三方服务）"""
    
    def __init__(self, config: ModelConfig):
        """
        初始化 OpenAI 适配器
        
        Args:
            config: 模型配置，必须包含 base_url 和 api_key
        """
        super().__init__(config)
        
        # NIO公司的固定 Base URL
        if config.provider.lower() == "nio":
            self.base_url = config.base_url or "https://modelgateway.nioint.com/publicService/v1"
        else:
            self.base_url = config.base_url
        
        self.api_key = config.api_key
        self.model_name = config.name
        
        # 创建 HTTP 客户端，禁用环境变量中的代理设置
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            trust_env=False,  # 禁用系统代理
        )
        
        logger.info(f"OpenAI 适配器初始化完成：{self.model_name} @ {self.base_url}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> ModelResponse:
        """
        对话接口
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "你好"}]
            **kwargs: 其他参数（temperature, max_tokens 等）
            
        Returns:
            ModelResponse: 对话响应
        """
        try:
            # 构建请求体
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "stream": False,
            }
            
            # 添加可选参数
            if "top_p" in kwargs:
                payload["top_p"] = kwargs["top_p"]
            elif self.config.top_p:
                payload["top_p"] = self.config.top_p
            
            # 发送请求
            response = await self.client.post(
                url=f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            # 检查响应状态
            response.raise_for_status()
            data = response.json()
            
            # 调试日志：打印完整响应
            logger.info(f"NIO API 响应状态码：{response.status_code}")
            logger.info(f"NIO API 响应完整数据：{json.dumps(data, ensure_ascii=False)}")
            
            # 提取回复内容 - 兼容 NIO 的特殊格式
            content = None
            
            # 标准 OpenAI 格式
            if data.get("choices") and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if choice.get("message"):
                    content = choice["message"].get("content")
                    logger.info(f"使用 choices[0].message.content 作为回复")
                elif choice.get("delta"):
                    content = choice["delta"].get("content")
                    logger.info(f"使用 choices[0].delta.content 作为回复")
            
            # 如果 choices 为空或 null，尝试其他字段（NIO 特殊处理）
            if not content:
                logger.warning(f"choices 字段为空或未找到，尝试其他字段")
                # 尝试直接从 result 字段获取
                if data.get("result"):
                    content = data["result"]
                    logger.warning(f"使用 result 字段作为回复内容")
                # 尝试从 display_msg 获取
                elif data.get("display_msg"):
                    content = data["display_msg"]
                    logger.warning(f"使用 display_msg 作为回复内容")
            
            if not content:
                logger.error(f"NIO API 返回异常数据：{data}")
                return ModelResponse(
                    success=False,
                    error="API 返回格式异常：无法解析回复内容",
                )
            
            # 提取使用量统计
            usage = data.get("usage", {})
            
            return ModelResponse(
                success=True,
                content=content,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                } if usage else None,
            )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 错误：{e.response.status_code} - {e.response.text}")
            return ModelResponse(
                success=False,
                error=f"HTTP 错误 {e.response.status_code}: {e.response.text}",
            )
        except httpx.RequestError as e:
            logger.error(f"请求错误：{str(e)}")
            return ModelResponse(
                success=False,
                error=f"网络请求失败：{str(e)}",
            )
        except Exception as e:
            logger.error(f"未知错误：{str(e)}")
            return ModelResponse(
                success=False,
                error=f"未知错误：{str(e)}",
            )
    
    async def generate_embedding(self, text: str) -> ModelResponse:
        """
        生成向量嵌入（如果模型支持）
        
        Args:
            text: 输入文本
            
        Returns:
            ModelResponse: 包含向量的响应
        """
        try:
            payload = {
                "model": self.model_name,
                "input": text,
            }
            
            response = await self.client.post(
                url=f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                vector = data["data"][0]["embedding"]
                return ModelResponse(
                    success=True,
                    vector=vector,
                )
            else:
                return ModelResponse(
                    success=False,
                    error="API 返回格式异常：未找到 embeddings 数据",
                )
                
        except Exception as e:
            logger.error(f"生成向量失败：{str(e)}")
            return ModelResponse(
                success=False,
                error=f"生成向量失败：{str(e)}",
            )
    
    async def health_check(self) -> bool:
        """
        健康检查 - 测试模型连接
        
        Returns:
            bool: 是否可用
        """
        try:
            # 发送一个简单的测试消息
            test_messages = [{"role": "user", "content": "hi"}]
            response = await self.chat(test_messages)
            return response.success
        except Exception as e:
            logger.error(f"健康检查失败：{str(e)}")
            return False
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
