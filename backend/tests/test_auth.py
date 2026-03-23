"""
认证授权模块单元测试
"""
import pytest
from backend.core.auth import (
    AuthManager,
    User,
    Role,
    RoleType,
    PermissionType,
)


class TestAuthManager:
    """测试认证管理器"""
    
    def test_hash_password(self):
        manager = AuthManager(secret_key="test-secret")
        password = "my_secure_password"
        
        hashed = manager.hash_password(password)
        
        assert hashed != password  # 哈希值不应等于原密码
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        manager = AuthManager(secret_key="test-secret")
        password = "my_secure_password"
        hashed = manager.hash_password(password)
        
        assert manager.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        manager = AuthManager(secret_key="test-secret")
        password = "my_secure_password"
        hashed = manager.hash_password(password)
        
        assert manager.verify_password("wrong_password", hashed) is False
    
    def test_create_access_token(self):
        manager = AuthManager(secret_key="test-secret", token_expire_minutes=30)
        user = User(
            id=1,
            username="testuser",
            password_hash="hashed",
            roles=[RoleType.NORMAL_USER.value],
        )
        
        token = manager.create_access_token(user)
        
        assert token is not None
        assert len(token) > 0
    
    def test_decode_access_token_valid(self):
        manager = AuthManager(secret_key="test-secret", token_expire_minutes=30)
        user = User(
            id=1,
            username="testuser",
            password_hash="hashed",
            roles=[RoleType.NORMAL_USER.value],
        )
        
        token = manager.create_access_token(user)
        decoded = manager.decode_access_token(token)
        
        assert decoded is not None
        assert decoded.user_id == 1
        assert decoded.username == "testuser"
        assert RoleType.NORMAL_USER.value in decoded.roles
    
    def test_decode_access_token_expired(self):
        manager = AuthManager(secret_key="test-secret", token_expire_minutes=-1)  # 已过期
        user = User(
            id=1,
            username="testuser",
            password_hash="hashed",
            roles=[RoleType.NORMAL_USER.value],
        )
        
        token = manager.create_access_token(user)
        decoded = manager.decode_access_token(token)
        
        assert decoded is None  # 过期应返回 None
    
    def test_has_permission_superuser(self):
        manager = AuthManager(secret_key="test-secret")
        user = User(
            id=1,
            username="admin",
            password_hash="hashed",
            roles=[RoleType.SUPER_ADMIN.value],
        )
        
        assert manager.has_permission(user, PermissionType.ADMIN_ACCESS.value) is True
        assert manager.has_permission(user, PermissionType.SKILL_EXECUTE.value) is True
    
    def test_has_permission_normal_user(self):
        manager = AuthManager(secret_key="test-secret")
        user = User(
            id=1,
            username="user",
            password_hash="hashed",
            roles=[RoleType.NORMAL_USER.value],
        )
        
        assert manager.has_permission(user, PermissionType.SKILL_EXECUTE.value) is True
        assert manager.has_permission(user, PermissionType.ADMIN_ACCESS.value) is False
    
    def test_has_permission_readonly_user(self):
        manager = AuthManager(secret_key="test-secret")
        user = User(
            id=1,
            username="readonly",
            password_hash="hashed",
            roles=[RoleType.READONLY_USER.value],
        )
        
        assert manager.has_permission(user, PermissionType.MEMORY_READ.value) is True
        assert manager.has_permission(user, PermissionType.MEMORY_WRITE.value) is False
    
    def test_get_user_permissions(self):
        manager = AuthManager(secret_key="test-secret")
        user = User(
            id=1,
            username="user",
            password_hash="hashed",
            roles=[RoleType.NORMAL_USER.value],
        )
        
        permissions = manager.get_user_permissions(user)
        
        assert PermissionType.API_ACCESS.value in permissions
        assert PermissionType.SKILL_EXECUTE.value in permissions
        assert PermissionType.MEMORY_READ.value in permissions
        assert PermissionType.MEMORY_WRITE.value in permissions
        assert PermissionType.ADMIN_ACCESS.value not in permissions
