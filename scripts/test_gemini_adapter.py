"""
测试 Google Gemini 适配器 - 使用数据库中的真实 API Key
"""
import sys
sys.path.insert(0, '/Users/xuecheng.liu/code/MiniClaw/backend')

from google import genai

# 使用数据库中的真实 API Key
API_KEY = "AIzaSyCHwwgZuPt3RUroNKB3sxc3BnpBMYZCyrU"
MODEL = "gemini-2.5-flash"

print("=" * 60)
print("🔍 测试 Google Gemini 适配器")
print("=" * 60)
print(f"\nAPI Key: {API_KEY[:10]}... (长度：{len(API_KEY)})")
print(f"模型：{MODEL}\n")

try:
    # 创建客户端
    client = genai.Client(api_key=API_KEY)
    
    # 发送测试请求
    print("📡 正在发送测试请求...")
    response = client.models.generate_content(
        model=MODEL,
        contents="Hi, please respond with 'OK, I am working!' in English."
    )
    
    print("\n✅ 成功！")
    print(f"回复内容：{response.text}")
    
except Exception as e:
    print(f"\n❌ 失败！")
    print(f"错误信息：{str(e)}")
    print(f"\n错误类型：{type(e).__name__}")
    
    # 详细诊断
    if "400" in str(e):
        print("\n💡 可能是 API Key 格式问题或无效")
    elif "404" in str(e):
        print(f"\n💡 模型 '{MODEL}' 可能不存在或不可用")
        print("   尝试使用 'gemini-2.0-flash' 或 'gemini-1.5-pro'")
    elif "INVALID_ARGUMENT" in str(e):
        print("\n💡 请求参数有问题，检查：")
        print("   1. API Key 是否正确")
        print("   2. 模型名称是否正确")
        print("   3. 请求格式是否符合要求")
