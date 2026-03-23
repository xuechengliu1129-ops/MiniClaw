"""
测试登录 API
"""
import sys
import os

# 添加 backend 目录到路径
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from core.auth import get_auth_manager

# 获取认证管理器
auth_mgr = get_auth_manager()

if not auth_mgr:
    print("❌ 认证管理器未初始化")
    sys.exit(1)

print("✅ 认证管理器已初始化")

# 测试创建用户（如果不存在）
try:
    # 尝试创建测试用户
    from datetime import datetime
    
    test_user = auth_mgr.create_user(
        username="admin",
        password="admin123",
        email="admin@miniclaw.com",
        roles=["super_admin"],
    )
    print(f"✅ 创建测试用户成功：{test_user.username}")
except Exception as e:
    print(f"⚠️ 创建用户可能已存在：{e}")
    test_user = auth_mgr.authenticate("admin", "admin123")
    if test_user:
        print(f"✅ 测试用户已存在：{test_user.username}")
    else:
        print("❌ 测试用户不存在且无法创建")
        sys.exit(1)

# 测试登录
user = auth_mgr.authenticate("admin", "admin123")
if user:
    print(f"✅ 登录成功：{user.username}")
    
    # 生成 Token
    token = auth_mgr.create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "roles": user.roles,
        }
    )
    print(f"🎫 生成的 Token: {token[:50]}...")
    
    # 验证 Token
    token_data = auth_mgr.decode_access_token(token)
    if token_data:
        print(f"✅ Token 验证成功：{token_data}")
    else:
        print("❌ Token 验证失败")
else:
    print("❌ 登录失败")

print("\n📝 测试账号信息:")
print("  用户名：admin")
print("  密码：admin123")
print("  角色：super_admin")