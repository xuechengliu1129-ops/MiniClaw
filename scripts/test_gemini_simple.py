from google import genai

# 请替换为你的实际 API Key
API_KEY = "AIzaSyCHwwgZuPt3RUroNKB3sxc3BnpBMYZCyrU"
client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="""你是 ABB 机器人语音助手，你的职责是：
"""
)
print(response.text)