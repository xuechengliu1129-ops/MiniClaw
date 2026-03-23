"""
自定义模型适配模块
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio


class ModelType:
    """模型类型枚举"""
    CHAT = "chat"  # 对话模型
    EMBEDDING = "embedding"  # 向量模型
    COMPLETION = "completion"  # 补全模型


class ModelConfig(BaseModel):
    """模型配置"""
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商 (ollama, openai, etc.)")
    base_url: str = Field(..., description="API 基础地址")
    api_key: Optional[str] = Field(default=None, description="API 密钥")
    model_type: str = Field(default=ModelType.CHAT, description="模型类型")
    context_window: int = Field(default=4096, description="上下文窗口大小")
    max_tokens: int = Field(default=2048, description="最大生成 token 数")
    temperature: float = Field(default=0.7, description="温度参数")
    top_p: float = Field(default=0.9, description="Top-p 采样参数")
    enabled: bool = Field(default=True, description="是否启用")
    is_default: bool = Field(default=False, description="是否为默认模型")


class ModelResponse(BaseModel):
    """模型响应"""
    success: bool
    content: Optional[str] = None
    vector: Optional[List[float]] = None
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class ModelAdapter(ABC):
    """模型适配器基类"""
    
    def __init__(self, config: ModelConfig):
        """
        初始化模型适配器
        
        Args:
            config: 模型配置
        """
        self.config = config
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> ModelResponse:
        """
        对话接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "你好"}]
            **kwargs: 其他参数
            
        Returns:
            ModelResponse: 响应结果
        """
        pass
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> ModelResponse:
        """
        生成向量嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            ModelResponse: 包含向量的响应
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 是否可用
        """
        pass


class OllamaAdapter(ModelAdapter):
    """Ollama 本地模型适配器"""
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> ModelResponse:
        """Ollama 对话实现"""
        try:
            # TODO: 调用 Ollama API
            await asyncio.sleep(0.1)  # 模拟异步调用
            
            return ModelResponse(
                success=True,
                content=f"[Ollama Mock] 回复：{messages[-1]['content']}",
                usage={"prompt_tokens": 10, "completion_tokens": 20},
            )
        except Exception as e:
            return ModelResponse(
                success=False,
                error=str(e),
            )
    
    async def generate_embedding(self, text: str) -> ModelResponse:
        """Ollama 向量生成实现"""
        try:
            # TODO: 调用 Ollama 向量 API
            await asyncio.sleep(0.1)
            
            # 模拟向量（实际应为 768 或 1536 维）
            mock_vector = [0.1] * 10
            
            return ModelResponse(
                success=True,
                vector=mock_vector,
            )
        except Exception as e:
            return ModelResponse(
                success=False,
                error=str(e),
            )
    
    async def health_check(self) -> bool:
        """Ollama 健康检查"""
        try:
            # TODO: 实际检查 Ollama 服务状态
            return True
        except:
            return False


class OpenAIAdapter(ModelAdapter):
    """OpenAI 兼容模型适配器"""
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> ModelResponse:
        """OpenAI 对话实现"""
        try:
            # TODO: 调用 OpenAI 兼容 API
            await asyncio.sleep(0.1)
            
            return ModelResponse(
                success=True,
                content=f"[OpenAI Mock] 回复：{messages[-1]['content']}",
                usage={"prompt_tokens": 10, "completion_tokens": 20},
            )
        except Exception as e:
            return ModelResponse(
                success=False,
                error=str(e),
            )
    
    async def generate_embedding(self, text: str) -> ModelResponse:
        """OpenAI 向量生成实现"""
        try:
            # TODO: 调用 OpenAI Embedding API
            await asyncio.sleep(0.1)
            
            mock_vector = [0.1] * 1536
            
            return ModelResponse(
                success=True,
                vector=mock_vector,
            )
        except Exception as e:
            return ModelResponse(
                success=False,
                error=str(e),
            )
    
    async def health_check(self) -> bool:
        """OpenAI 健康检查"""
        try:
            # TODO: 实际检查 API 可用性
            return self.config.api_key is not None
        except:
            return False


class ModelManager:
    """模型管理器 - 负责多模型配置、调度与降级"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化模型管理器"""
        self.models: Dict[str, ModelAdapter] = {}
        self.configs: Dict[str, ModelConfig] = {}
        self.default_model_name: Optional[str] = None
    
    def register_model(self, config: ModelConfig):
        """
        注册模型
        
        Args:
            config: 模型配置
        """
        adapter = self._create_adapter(config)
        self.models[config.name] = adapter
        self.configs[config.name] = config
        
        if config.is_default:
            self.default_model_name = config.name
    
    def _create_adapter(self, config: ModelConfig) -> ModelAdapter:
        """
        创建模型适配器
        
        Args:
            config: 模型配置
            
        Returns:
            ModelAdapter: 适配器实例
        """
        from .openai_adapter import OpenAIAdapter
        
        if config.provider.lower() == "ollama":
            return OllamaAdapter(config)
        elif config.provider.lower() in ["openai", "nio"]:
            # NIO使用OpenAI兼容适配器
            return OpenAIAdapter(config)
        else:
            raise ValueError(f"不支持的模型提供商：{config.provider}")
    
    def get_model(self, model_name: Optional[str] = None) -> Optional[ModelAdapter]:
        """
        获取模型适配器
        
        Args:
            model_name: 模型名称（不传则使用默认模型）
            
        Returns:
            ModelAdapter: 适配器实例或 None
        """
        if not model_name:
            model_name = self.default_model_name
        
        if not model_name or model_name not in self.models:
            return None
        
        return self.models[model_name]
    
    def list_models(self) -> List[Dict]:
        """
        列出所有模型
        
        Returns:
            List[Dict]: 模型信息列表
        """
        return [
            {
                "name": config.name,
                "provider": config.provider,
                "model_type": config.model_type,
                "enabled": config.enabled,
                "is_default": config.is_default,
                "context_window": config.context_window,
                "max_tokens": config.max_tokens,
            }
            for config in self.configs.values()
        ]
    
    async def execute_with_fallback(self, model_name: str, **kwargs) -> ModelResponse:
        """
        执行带降级的模型调用
        
        Args:
            model_name: 首选模型名称
            **kwargs: 调用参数
            
        Returns:
            ModelResponse: 响应结果
        """
        # 尝试首选模型
        model = self.get_model(model_name)
        if model and model.config.enabled:
            response = await model.chat(kwargs.get("messages", []))
            if response.success:
                return response
        
        # 降级到默认模型
        if model_name != self.default_model_name:
            default_model = self.get_model()
            if default_model and default_model.config.enabled:
                return await default_model.chat(kwargs.get("messages", []))
        
        # 全部失败
        return ModelResponse(
            success=False,
            error="所有可用模型均调用失败",
        )


# 全局模型管理器实例
model_manager = ModelManager()


def get_model_manager() -> ModelManager:
    """获取模型管理器单例"""
    return model_manager
