"""
Ollama 模型适配器
"""
import httpx
import os
from typing import Optional, List, Dict, Any
from loguru import logger


class OllamaAdapter:
    """Ollama 本地模型适配器"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        # 强制使用 IPv4（避免 IPv6 解析问题）
        if "localhost" in base_url:
            base_url = base_url.replace("localhost", "127.0.0.1")
        
        self.base_url = base_url
        
        # 设置 NO_PROXY 环境变量，确保 ollama 库能绕过代理
        # 这会影响所有使用 httpx 的库（包括 ollama-python 和 langchain-ollama）
        existing_no_proxy = os.environ.get('NO_PROXY', '')
        if '127.0.0.1' not in existing_no_proxy and 'localhost' not in existing_no_proxy:
            if existing_no_proxy:
                os.environ['NO_PROXY'] = f"127.0.0.1,localhost,{existing_no_proxy}"
            else:
                os.environ['NO_PROXY'] = '127.0.0.1,localhost'
        
        logger.info(f"Ollama 适配器初始化完成：{base_url} (已设置 NO_PROXY)")
    
    def get_langchain_model(self, model_name: str):
        """
        获取 LangChain 兼容的模型实例
        
        Args:
            model_name: Ollama 模型名称
        
        Returns:
            LangChain ChatOllama 实例
        """
        from langchain_ollama import ChatOllama
        
        return ChatOllama(
            model=model_name,
            base_url=self.base_url,
            # 使用 async_client_kwargs 传递 httpx AsyncClient 的配置
            # trust_env=False 禁用系统代理，避免被公司 Squid 代理拦截
            async_client_kwargs={
                'trust_env': False,
                'timeout': 60.0,
            },
        )
    
    async def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        调用 Ollama 聊天模型
        
        Args:
            model: 模型名称，如 'qwen2:0.5b'
            messages: 消息列表，格式为 [{"role": "user", "content": "你好"}]
            temperature: 温度参数
        
        Returns:
            AI 回复的内容
        """
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            logger.debug(f"调用 Ollama API: {url}, model: {model}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("message", {}).get("content", "")
            
            logger.info(f"Ollama 回复：{content[:100]}...")
            return content
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama API 调用失败：{e}")
            raise Exception(f"Ollama 请求失败：{str(e)}")
        except Exception as e:
            logger.error(f"Ollama 调用异常：{e}")
            raise Exception(f"AI 模型调用失败：{str(e)}")
    
    async def generate(self, model: str, prompt: str, temperature: float = 0.7) -> str:
        """
        调用 Ollama 生成模型（兼容旧接口）
        
        Args:
            model: 模型名称
            prompt: 提示词
            temperature: 温度参数
        
        Returns:
            生成的内容
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Ollama 生成调用失败：{e}")
            raise Exception(f"AI 生成失败：{str(e)}")
    
    async def test_connection(self, model: str) -> bool:
        """
        测试模型连接
        
        Args:
            model: 模型名称
        
        Returns:
            是否连接成功
        """
        try:
            # 先检查服务是否可用
            health_url = f"{self.base_url}/api/tags"
            response = await self.client.get(health_url)
            response.raise_for_status()
            
            # 检查模型是否存在
            models_response = await self.client.get(health_url)
            models_data = models_response.json()
            models = [m.get("name") for m in models_data.get("models", [])]
            
            if model not in models and not any(model in m for m in models):
                raise Exception(f"模型 '{model}' 不存在，可用模型：{', '.join(models)}")
            
            # 发送一个简单的测试消息
            test_messages = [{"role": "user", "content": "Hi"}]
            await self.chat(model, test_messages, temperature=0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Ollama 连接测试失败：{e}")
            return False
    
    async def close(self):
        """关闭客户端连接"""
        await self.client.aclose()
