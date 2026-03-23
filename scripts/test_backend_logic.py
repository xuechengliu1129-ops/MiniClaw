"""
模拟后端测试连接逻辑
"""
import sys
import asyncio
sys.path.insert(0, '/Users/xuecheng.liu/code/MiniClaw/backend')

# 设置环境变量
import os
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./miniclaw.db'

from google import genai

async def test_gemini_connection():
    """测试 Google Gemini 连接"""
    
    # 从数据库获取 API Key
    import sqlite3
    conn = sqlite3.connect('backend/miniclaw.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, provider, api_key FROM model_configs WHERE id = 14')
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("❌ 模型配置不存在")
        return
    
    model_id, model_name, provider, api_key = row
    
    print("=" * 60)
    print("🔍 模拟后端测试连接逻辑")
    print("=" * 60)
    print(f"\n模型 ID: {model_id}")
    print(f"模型名称：{model_name}")
    print(f"提供商：{provider}")
    print(f"API Key: {api_key[:10]}... (长度：{len(api_key)})\n")
    
    if provider not in ["google", "gemini"]:
        print(f"❌ 不是 Google Gemini 提供商")
        return
    
    if not api_key or api_key == "***":
        print(f"❌ API Key 为空或掩码")
        return
    
    try:
        print("📡 正在创建客户端...")
        client = genai.Client(api_key=api_key)
        
        print(f"📡 正在调用模型 {model_name}...")
        test_prompt = "Hi, please respond with 'OK' if you are working."
        
        response = client.models.generate_content(
            model=model_name,
            contents=test_prompt,
        )
        
        if response and response.text:
            print(f"\n✅ 连接测试成功！")
            print(f"回复内容：{response.text[:100]}...")
        else:
            print(f"\n⚠️ 返回空响应")
            
    except Exception as e:
        print(f"\n❌ 测试失败！")
        print(f"错误信息：{str(e)}")
        print(f"错误类型：{type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_gemini_connection())
