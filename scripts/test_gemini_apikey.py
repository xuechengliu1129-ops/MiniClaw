"""
Google Gemini API Key 测试脚本
"""
import requests

# 你的 API Key
API_KEY = "AIzaSyCHwwgZuPt3RUroNKB3sxc3BnpBMYZCyrU"
MODEL = "gemini-2.0-flash-exp"

# 构建 URL
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# 请求数据
data = {
    "contents": [
        {
            "parts": [
                {"text": "Hello, are you working?"}
            ]
        }
    ]
}

print(f"🔍 正在测试 API Key: {API_KEY[:10]}...")
print(f"📡 请求 URL: {url}")
print(f"📝 请求数据：{data}\n")

try:
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API Key 有效！")
        print(f"📊 响应状态码：{response.status_code}")
        if 'candidates' in result:
            content = result['candidates'][0]['content']['parts'][0]['text']
            print(f"💬 AI 回复：{content[:100]}...")
    else:
        print(f"❌ API Key 无效！")
        print(f"📊 响应状态码：{response.status_code}")
        print(f"📝 错误信息：{response.text}")
        
except Exception as e:
    print(f"❌ 请求失败：{e}")
    print("\n可能的原因：")
    print("1. 网络连接问题")
    print("2. 无法访问 Google 服务")
    print("3. API Key 格式错误")
