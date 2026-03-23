"""
Google Gemini 模型适配器 - 极简版本
严格遵循官方示例调用方式
"""
from typing import List, Dict
from loguru import logger

try:
    from google import genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False


class GoogleGeminiAdapter:
    """Google Gemini 适配器 - 极简实现"""
    
    def __init__(self, api_key: str):
        """
        初始化适配器
        
        Args:
            api_key: Google API Key
        """
        if not GOOGLE_GENAI_AVAILABLE:
            raise ImportError("请安装：pip install google-genai")
        
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        logger.info(f"✅ Google Gemini 适配器已初始化")
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """
        聊天接口
        
        Args:
            model: 模型名称，如 "gemini-2.5-flash"
            messages: 消息列表 [{"role": "user", "content": "你好"}]
            temperature: 温度参数（目前 Gemini SDK 暂不支持，保留用于未来扩展）
            max_tokens: 最大生成 token 数（目前 Gemini SDK 暂不支持，保留用于未来扩展）
        
        Returns:
            AI 回复内容
        """
        try:
            # 构建提示词
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # 添加角色前缀
                if role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
            
            # 拼接成完整 prompt
            prompt = "\n".join(prompt_parts)
            
            logger.debug(f"📡 调用 Gemini: model={model}, temperature={temperature}, max_tokens={max_tokens}")
            
            # 严格按官方示例调用
            # 注意：Google GenAI SDK 目前不支持 temperature 和 max_tokens 参数
            # 这些参数保留用于未来版本扩展
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
            )
            
            if response and response.text:
                logger.info(f"✅ Gemini 回复成功")
                return response.text
            else:
                return ""
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Gemini 调用失败：{error_msg}")
            
            # 详细错误提示
            if "API key not valid" in error_msg:
                raise Exception(
                    f"API Key 无效，请检查：\n"
                    f"1. API Key 是否正确（应以 AIza 开头）\n"
                    f"2. 是否有多余空格\n"
                    f"3. API Key 是否已过期\n"
                    f"\n获取新 Key: https://aistudio.google.com/app/apikey"
                )
            else:
                raise Exception(f"调用失败：{error_msg}")
    
    async def test_connection(self, model: str) -> bool:
        """
        测试连接
        
        Args:
            model: 模型名称
        
        Returns:
            是否成功
        """
        try:
            test_prompt = "Hi, please respond with 'OK' if you are working."
            
            response = self.client.models.generate_content(
                model=model,
                contents=test_prompt,
            )
            
            if response and response.text:
                logger.info(f"✅ 连接测试成功：{response.text[:50]}...")
                return True
            else:
                logger.warning("⚠️ 返回空响应")
                return False
                
        except Exception as e:
            logger.error(f"❌ 连接测试失败：{str(e)}")
            return False
