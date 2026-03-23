---
name: "feishu_notifier"
description: "发送消息到飞书群聊（支持文本和 Markdown 格式）"
author: "MiniClaw Team"
version: "1.0.0"
async_support: true
parameters:
  - name: "webhook_url"
    type: "str"
    required: true
    description: "飞书机器人 Webhook URL"
  - name: "message"
    type: "str"
    required: true
    description: "要发送的消息内容"
  - name: "msg_type"
    type: "str"
    required: false
    default: "text"
    description: "消息类型：text（文本）或 markdown"
  - name: "mentions"
    type: "list"
    required: false
    default: []
    description: "要@的用户 ID 列表"
---

# 飞书消息推送技能

## 功能说明

通过飞书机器人 Webhook 向群聊发送通知消息，支持文本和 Markdown 两种格式。

**适用场景**：
- 系统告警通知
- 任务完成提醒
- 定时报告推送
- 协作消息同步

## 使用示例

### 示例 1：发送文本消息

用户请求："发送一条飞书消息：测试成功"

执行步骤：
1. 接收参数：`{"webhook_url": "https://...", "message": "测试成功"}`
2. 构建消息体（文本格式）
3. POST 到飞书 Webhook
4. 返回结果：`{"success": true, "message": "发送成功"}`

### 示例 2：发送 Markdown 格式消息

```json
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
  "message": "# 每日报告\n\n✅ 完成任务：15 个\n⚠️ 发现告警：2 个\n📊 成功率：98%",
  "msg_type": "markdown"
}
```

响应：
```json
{
  "success": true,
  "message": "消息发送成功",
  "response": {
    "code": 0,
    "msg": "success"
  }
}
```

### 示例 3：@指定用户

```json
{
  "webhook_url": "https://...",
  "message": "紧急！需要立即处理",
  "msg_type": "text",
  "mentions": ["ou_123456", "ou_789012"]
}
```

## Markdown 语法支持

飞书支持的 Markdown 格式：

```markdown
# 一级标题
## 二级标题

**粗体** *斜体* ~~删除线~~

- 无序列表
- 项目 2

1. 有序列表
2. 项目 2

[链接](https://example.com)

> 引用内容

`行内代码`
```

## 异常处理

1. **Webhook URL 无效**: `InvalidWebhookUrl`
   - 原因：URL 格式错误或已过期
   - 解决：重新获取 Webhook URL

2. **发送超时**: `TimeoutError: 请求超时`
   - 原因：网络问题或飞书服务不可用
   - 解决：检查网络，稍后重试

3. **消息过长**: `MessageTooLong`
   - 原因：超过飞书限制（文本 4096 字符）
   - 解决：截断或分段发送

4. **@用户失败**: 用户 ID 不存在
   - 原因：使用了错误的 OpenID
   - 解决：确认用户 ID 正确

## 获取 Webhook URL

1. 打开飞书群聊 → 右上角菜单
2. 添加机器人 → 自定义机器人
3. 填写名称、头像
4. 复制 Webhook 地址（以 `https://open.feishu.cn/open-apis/bot/v2/hook/` 开头）

## 最佳实践

✅ **推荐**：
- 使用 Markdown 提升可读性
- 重要消息@相关人员
- 控制消息长度在合理范围
- 记录发送历史便于追溯

❌ **避免**：
- 发送敏感信息（密码、密钥）
- 频繁推送造成骚扰
- 超大消息（建议 <2000 字符）
- 无效链接