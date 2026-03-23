"""
快速测试 Gemini API
直接运行此脚本验证 API Key 和模型名称
"""
from google import genai

API_KEY = "AIzaSyCHwwgZuPt3RUroNKB3sxc3BnpBMYZCyrU"

print("🔍 测试 gemini-2.5-flash...")
try:
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="你好，请用中文回复'测试成功'"
    )
    print(f"✅ 成功！回复：{response.text}")
except Exception as e:
    print(f"❌ 失败：{e}")