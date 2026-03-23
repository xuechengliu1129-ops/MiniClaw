"""
RBAC 权限管理模块
"""
from typing import List, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import jwt
from passlib.context import CryptContext


class RoleType(str, Enum):
    """角色类型枚举"""
    SUPER_ADMIN = "super_admin"  # 超级管理员
    NORMAL_USER = "normal_user"  # 普通用户
    SKILL_DEVELOPER = "skill_developer"  # 技能开发者
    READONLY_USER = "readonly_user"  # 只读用户


class PermissionType(str, Enum):
    """权限类型枚举"""
    API_ACCESS = "api:access"  # API 访问权限
    SKILL_EXECUTE = "skill:execute"  # 技能执行权限
    MEMORY_READ = "memory:read"  # 记忆读取权限
    MEMORY_WRITE = "memory:write"  # 记忆写入权限
    MODEL_CONFIG = "model:config"  # 模型配置权限
    ADMIN_ACCESS = "admin:access"  # 管理后台权限


class User(BaseModel):
    """用户模型"""
    id: int = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(default=None, description="邮箱")
    phone: Optional[str] = Field(default=None, description="手机号")
    password_hash: str = Field(..., description="密码哈希")
    feishu_open_id: Optional[str] = Field(default=None, description="飞书 Open ID")
    feishu_union_id: Optional[str] = Field(default=None, description="飞书 Union ID")
    roles: List[str] = Field(default_factory=list, description="角色列表")
    enabled: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class Role(BaseModel):
    """角色模型"""
    name: str = Field(..., description="角色名称")
    description: str = Field(..., description="角色描述")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    is_system: bool = Field(default=False, description="是否为系统角色（不可删除）")


class TokenData(BaseModel):
    """Token 数据"""
    user_id: int
    username: str
    roles: List[str]
    exp: datetime


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthManager:
    """认证授权管理器"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", token_expire_minutes: int = 30):
        """
        初始化认证管理器
        
        Args:
            secret_key: JWT 密钥
            algorithm: JWT 算法
            token_expire_minutes: Token 过期时间（分钟）
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
        self.users: dict[int, User] = {}
        self.roles: dict[str, Role] = {}
        self._init_system_roles()
    
    def _init_system_roles(self):
        """初始化系统角色"""
        # 超级管理员
        self.roles[RoleType.SUPER_ADMIN.value] = Role(
            name=RoleType.SUPER_ADMIN.value,
            description="系统超级管理员，拥有所有权限",
            permissions=[
                PermissionType.API_ACCESS.value,
                PermissionType.SKILL_EXECUTE.value,
                PermissionType.MEMORY_READ.value,
                PermissionType.MEMORY_WRITE.value,
                PermissionType.MODEL_CONFIG.value,
                PermissionType.ADMIN_ACCESS.value,
            ],
            is_system=True,
        )
        
        # 普通用户
        self.roles[RoleType.NORMAL_USER.value] = Role(
            name=RoleType.NORMAL_USER.value,
            description="普通用户，基础使用权限",
            permissions=[
                PermissionType.API_ACCESS.value,
                PermissionType.SKILL_EXECUTE.value,
                PermissionType.MEMORY_READ.value,
                PermissionType.MEMORY_WRITE.value,
            ],
            is_system=True,
        )
        
        # 技能开发者
        self.roles[RoleType.SKILL_DEVELOPER.value] = Role(
            name=RoleType.SKILL_DEVELOPER.value,
            description="技能开发者，可开发和管理技能",
            permissions=[
                PermissionType.API_ACCESS.value,
                PermissionType.SKILL_EXECUTE.value,
                PermissionType.MEMORY_READ.value,
                PermissionType.MODEL_CONFIG.value,
            ],
            is_system=True,
        )
        
        # 只读用户
        self.roles[RoleType.READONLY_USER.value] = Role(
            name=RoleType.READONLY_USER.value,
            description="只读用户，仅可查看权限",
            permissions=[
                PermissionType.API_ACCESS.value,
                PermissionType.MEMORY_READ.value,
            ],
            is_system=True,
        )
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except:
            return False
    
    def create_access_token(self, user: User) -> str:
        """
        创建访问令牌
        
        Args:
            user: 用户对象
            
        Returns:
            str: JWT Token
        """
        from datetime import timedelta
        
        expire = datetime.now() + timedelta(minutes=self.token_expire_minutes)
        
        to_encode = {
            "user_id": user.id,
            "username": user.username,
            "roles": user.roles,
            "exp": expire,
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Optional[TokenData]:
        """
        解码访问令牌
        
        Args:
            token: JWT Token
            
        Returns:
            Optional[TokenData]: Token 数据或 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenData(
                user_id=payload["user_id"],
                username=payload["username"],
                roles=payload["roles"],
                exp=datetime.fromtimestamp(payload["exp"]),
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def add_user(self, user: User):
        """添加用户"""
        self.users[user.id] = user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户"""
        return self.users.get(user_id)
    
    def has_permission(self, user: User, permission: str) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            user: 用户对象
            permission: 权限标识
            
        Returns:
            bool: 是否有权限
        """
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role and permission in role.permissions:
                return True
        return False
    
    def has_role(self, user: User, role_name: str) -> bool:
        """检查用户是否有指定角色"""
        return role_name in user.roles
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """获取用户所有权限"""
        permissions = set()
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                permissions.update(role.permissions)
        return permissions


# 全局认证管理器实例（需要时初始化）
auth_manager: Optional[AuthManager] = None


def init_auth_manager(secret_key: str, algorithm: str = "HS256", token_expire_minutes: int = 30):
    """初始化认证管理器"""
    global auth_manager
    auth_manager = AuthManager(secret_key, algorithm, token_expire_minutes)


def get_auth_manager() -> Optional[AuthManager]:
    """获取认证管理器实例"""
    return auth_manager


"""
JWT 认证工具函数
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from loguru import logger

from . import get_auth_manager, TokenData


# HTTP Bearer Token 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    JWT Token 认证依赖注入
    
    Args:
        credentials: HTTP Bearer Token
        
    Returns:
        dict: 用户信息 {id, username, roles}
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # 获取认证管理器
    auth_mgr = get_auth_manager()
    if not auth_mgr:
        logger.error("认证管理器未初始化")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化",
        )
    
    # 解码 Token
    token_data = auth_mgr.decode_access_token(token)
    
    if not token_data:
        logger.warning(f"Token 无效或已过期")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 返回用户信息
    user_info = {
        "id": token_data.user_id,
        "username": token_data.username,
        "roles": token_data.roles,
    }
    
    logger.debug(f"用户认证成功：{user_info['username']}")
    return user_info


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    可选的 JWT Token 认证（某些接口允许匿名访问）
    
    Args:
        credentials: HTTP Bearer Token
        
    Returns:
        Optional[dict]: 用户信息或 None
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
