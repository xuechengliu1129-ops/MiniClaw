"""
网关核心模块 - 统一请求入口、限流、日志、鉴权
"""
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from loguru import logger
import time
import json


class RequestContext:
    """请求上下文"""
    
    def __init__(self, request: Request):
        self.request = request
        self.start_time = time.time()
        self.user_id: Optional[int] = None
        self.role: Optional[str] = None
        self.token: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def get_elapsed_time(self) -> float:
        """获取请求耗时（秒）"""
        return time.time() - self.start_time


class RateLimiter:
    """令牌桶限流器"""
    
    def __init__(self, capacity: int = 100, refill_rate: float = 10.0):
        """
        初始化限流器
        
        Args:
            capacity: 桶容量（最大令牌数）
            refill_rate: 补充速率（每秒补充的令牌数）
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens: Dict[str, float] = {}  # key -> tokens
        self.last_refill: Dict[str, float] = {}  # key -> last refill time
    
    def _refill_tokens(self, key: str):
        """补充令牌"""
        current_time = time.time()
        
        if key not in self.tokens:
            self.tokens[key] = self.capacity
            self.last_refill[key] = current_time
            return
        
        # 计算应补充的令牌数
        elapsed = current_time - self.last_refill[key]
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens[key] = min(self.capacity, self.tokens[key] + tokens_to_add)
        self.last_refill[key] = current_time
    
    def consume(self, key: str, tokens: int = 1) -> bool:
        """
        消费令牌
        
        Args:
            key: 标识 key（如用户 ID、IP）
            tokens: 需要消费的令牌数
            
        Returns:
            bool: 是否成功消费
        """
        self._refill_tokens(key)
        
        if self.tokens[key] >= tokens:
            self.tokens[key] -= tokens
            return True
        
        return False
    
    def get_remaining_tokens(self, key: str) -> int:
        """获取剩余令牌数"""
        self._refill_tokens(key)
        return int(self.tokens[key])


class GatewayManager:
    """网关管理器"""
    
    def __init__(self):
        """初始化网关管理器"""
        self.rate_limiter = RateLimiter(capacity=100, refill_rate=10.0)
        self.request_logs = []
    
    async def process_request(self, request: Request) -> RequestContext:
        """
        处理请求（所有请求必经此方法）
        
        Args:
            request: FastAPI 请求对象
            
        Returns:
            RequestContext: 请求上下文
            
        Raises:
            HTTPException: 限流或鉴权失败时抛出
        """
        context = RequestContext(request)
        
        # 1. 提取 Token
        context.token = self._extract_token(request)
        
        # 2. JWT 鉴权（如果需要）
        if context.token:
            try:
                # TODO: 验证 JWT token
                # user_info = verify_jwt(context.token)
                # context.user_id = user_info["user_id"]
                # context.role = user_info["role"]
                pass
            except Exception as e:
                logger.warning(f"JWT 验证失败：{e}")
        
        # 3. 限流检查
        client_key = self._get_client_key(request)
        if not self.rate_limiter.consume(client_key):
            remaining = self.rate_limiter.get_remaining_tokens(client_key)
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，剩余令牌数：{remaining}",
            )
        
        # 4. 记录请求日志
        self._log_request(context, "STARTED")
        
        return context
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求头提取 Token"""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None
    
    def _get_client_key(self, request: Request) -> str:
        """获取客户端标识（用于限流）"""
        # 优先使用用户 ID，其次使用 IP
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _log_request(self, context: RequestContext, status: str):
        """记录请求日志"""
        log_entry = {
            "timestamp": time.time(),
            "method": context.request.method,
            "path": context.request.url.path,
            "client_ip": context.request.client.host if context.request.client else "unknown",
            "user_id": context.user_id,
            "status": status,
            "elapsed_time": context.get_elapsed_time(),
        }
        
        self.request_logs.append(log_entry)
        
        if status == "ERROR":
            logger.error(f"请求异常：{json.dumps(log_entry)}")
        else:
            logger.info(f"请求开始：{json.dumps(log_entry)}")
    
    async def finalize_request(self, context: RequestContext, status: str = "COMPLETED"):
        """
        完成请求处理
        
        Args:
            context: 请求上下文
            status: 状态 (COMPLETED/ERROR)
        """
        log_entry = {
            "timestamp": time.time(),
            "method": context.request.method,
            "path": context.request.url.path,
            "user_id": context.user_id,
            "status": status,
            "elapsed_time": context.get_elapsed_time(),
        }
        
        # 更新日志
        for i, log in enumerate(self.request_logs):
            if log["timestamp"] == context.start_time:
                self.request_logs[i] = log_entry
                break
        
        if status == "ERROR":
            logger.error(f"请求错误：{json.dumps(log_entry)}")
        else:
            logger.info(f"请求完成：{json.dumps(log_entry)} - 耗时：{context.get_elapsed_time():.3f}s")
    
    def get_request_stats(self) -> Dict:
        """获取请求统计信息"""
        total_requests = len(self.request_logs)
        avg_time = sum(log.get("elapsed_time", 0) for log in self.request_logs) / max(total_requests, 1)
        
        return {
            "total_requests": total_requests,
            "average_response_time": round(avg_time, 3),
            "active_clients": len(self.rate_limiter.tokens),
        }


# 全局网管管理器实例
gateway_manager = GatewayManager()


def get_gateway_manager() -> GatewayManager:
    """获取网关管理器单例"""
    return gateway_manager
