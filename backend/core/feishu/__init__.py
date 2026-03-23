"""
飞书机器人集成模块
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import base64
import json


class FeishuMessageType:
    """飞书消息类型枚举"""
    TEXT = "text"
    MARKDOWN = "post"
    CARD = "interactive_card"


class FeishuMessage(BaseModel):
    """飞书消息模型"""
    receive_id: str = Field(..., description="接收者 ID")
    msg_type: str = Field(default=FeishuMessageType.TEXT, description="消息类型")
    content: Dict[str, Any] = Field(..., description="消息内容")
    open_id: Optional[str] = Field(default=None, description="用户 Open ID")
    union_id: Optional[str] = Field(default=None, description="用户 Union ID")
    chat_id: Optional[str] = Field(default=None, description="群聊 ID")


class FeishuEvent(BaseModel):
    """飞书事件模型"""
    schema: str = Field(..., description="事件 schema")
    header: Dict[str, Any] = Field(..., description="事件头")
    event: Dict[str, Any] = Field(..., description="事件内容")
    token: str = Field(..., description="验证 token")
    type: str = Field(..., description="事件类型")


class FeishuUserMapping(BaseModel):
    """飞书用户与系统用户映射"""
    feishu_open_id: str = Field(..., description="飞书 Open ID")
    feishu_union_id: Optional[str] = Field(default=None, description="飞书 Union ID")
    system_user_id: int = Field(..., description="系统用户 ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class FeishuAdapter:
    """飞书适配器 - 处理飞书消息收发与事件解析"""
    
    def __init__(self, app_id: str, app_secret: str, verification_token: str, encrypt_key: Optional[str] = None):
        """
        初始化飞书适配器
        
        Args:
            app_id: 应用 App ID
            app_secret: 应用 App Secret
            verification_token: 验证 Token
            encrypt_key: 加密密钥（可选）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key
        self.access_token: Optional[str] = None
        self.token_expire_time: Optional[datetime] = None
    
    async def get_access_token(self) -> str:
        """获取访问令牌"""
        # TODO: 调用飞书 API 获取 access_token
        # 如果已有 token 未过期则直接返回
        if self.access_token and self.token_expire_time and datetime.now() < self.token_expire_time:
            return self.access_token
        
        # 模拟获取新 token
        self.access_token = "mock_access_token_12345"
        self.token_expire_time = datetime.now()
        
        return self.access_token
    
    def verify_signature(self, timestamp: str, token: str, signature: str) -> bool:
        """
        验证请求签名
        
        Args:
            timestamp: 时间戳
            token: 验证 Token
            signature: 签名
            
        Returns:
            bool: 是否验证通过
        """
        # 拼接 timestamp + token
        string_to_sign = f"{timestamp}{token}"
        
        # 计算 SHA256
        signature_computed = hashlib.sha256(string_to_sign.encode()).hexdigest()
        
        return signature == signature_computed
    
    def decrypt_message(self, encrypted_message: str) -> Dict:
        """
        解密飞书消息
        
        Args:
            encrypted_message: 加密消息
            
        Returns:
            Dict: 解密后的消息
        """
        if not self.encrypt_key:
            raise ValueError("未配置加密密钥")
        
        # TODO: 实现 AES 解密逻辑
        # 这里仅做示例
        try:
            decoded = base64.b64decode(encrypted_message)
            # 实际需要使用 encrypt_key 进行 AES 解密
            return {"decrypted": "mock_decrypted_data"}
        except Exception as e:
            raise ValueError(f"解密失败：{str(e)}")
    
    async def send_message(self, message: FeishuMessage) -> bool:
        """
        发送飞书消息
        
        Args:
            message: 消息对象
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 获取 access token
            token = await self.get_access_token()
            
            # 构建请求
            url = f"https://open.feishu.cn/open-apis/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "receive_id": message.receive_id,
                "msg_type": message.msg_type,
                "content": json.dumps(message.content),
            }
            
            # TODO: 实际调用飞书 API
            print(f"[Mock] 发送飞书消息到 {message.receive_id}: {message.content}")
            
            return True
        except Exception as e:
            print(f"发送飞书消息失败：{e}")
            return False
    
    async def send_text_message(self, receive_id: str, text: str, **kwargs) -> bool:
        """发送文本消息"""
        message = FeishuMessage(
            receive_id=receive_id,
            msg_type=FeishuMessageType.TEXT,
            content={"text": text},
            **kwargs,
        )
        return await self.send_message(message)
    
    async def send_markdown_message(self, receive_id: str, markdown: str, **kwargs) -> bool:
        """发送 Markdown 消息"""
        content = {
            "post": {
                "zh_cn": {
                    "title": "MiniClaw 通知",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": markdown,
                            }
                        ]
                    ],
                }
            }
        }
        
        message = FeishuMessage(
            receive_id=receive_id,
            msg_type=FeishuMessageType.MARKDOWN,
            content=content,
            **kwargs,
        )
        return await self.send_message(message)
    
    async def send_card_message(self, receive_id: str, card_content: Dict, **kwargs) -> bool:
        """发送卡片消息"""
        message = FeishuMessage(
            receive_id=receive_id,
            msg_type=FeishuMessageType.CARD,
            content=card_content,
            **kwargs,
        )
        return await self.send_message(message)
    
    def parse_event(self, request_body: Dict) -> FeishuEvent:
        """
        解析飞书事件
        
        Args:
            request_body: 请求体
            
        Returns:
            FeishuEvent: 事件对象
        """
        # TODO: 处理加密事件
        if self.encrypt_key and request_body.get("encrypt"):
            decrypted = self.decrypt_message(request_body["encrypt"])
            return FeishuEvent(**decrypted)
        
        return FeishuEvent(**request_body)
    
    async def handle_url_verification(self, event: FeishuEvent) -> Dict:
        """
        处理 URL 验证（初次配置时使用）
        
        Args:
            event: 验证事件
            
        Returns:
            Dict: 验证响应
        """
        if event.header.get("event_type") == "url_verification":
            challenge = event.event.get("challenge")
            return {
                "challenge": challenge,
            }
        return {}


class FeishuCommandParser:
    """飞书指令解析器 - 解析 /技能名 参数 格式"""
    
    @staticmethod
    def parse_command(message: str) -> Optional[Dict]:
        """
        解析指令
        
        Args:
            message: 消息内容
            
        Returns:
            Optional[Dict]: 解析结果 {"skill_name": str, "args": str}
        """
        if not message.startswith("/"):
            return None
        
        parts = message[1:].strip().split(maxsplit=1)
        
        if not parts:
            return None
        
        result = {
            "skill_name": parts[0],
            "args": parts[1] if len(parts) > 1 else "",
        }
        
        return result
    
    @staticmethod
    def build_response_message(skill_name: str, result: Dict) -> str:
        """
        构建响应消息
        
        Args:
            skill_name: 技能名称
            result: 执行结果
            
        Returns:
            str: 响应消息文本
        """
        if result.get("success"):
            return f"✅ 技能 `{skill_name}` 执行成功\n\n结果：{result.get('data', '')}"
        else:
            return f"❌ 技能 `{skill_name}` 执行失败\n\n错误：{result.get('error', '')}"


# 全局飞书适配器实例（需要时初始化）
feishu_adapter: Optional[FeishuAdapter] = None


def init_feishu_adapter(app_id: str, app_secret: str, verification_token: str, encrypt_key: Optional[str] = None):
    """初始化飞书适配器"""
    global feishu_adapter
    feishu_adapter = FeishuAdapter(app_id, app_secret, verification_token, encrypt_key)


def get_feishu_adapter() -> Optional[FeishuAdapter]:
    """获取飞书适配器实例"""
    return feishu_adapter
