---
name: "file_reader"
description: "读取本地文件内容（安全限制：仅允许读取 /tmp/miniclaw_files 目录）"
author: "MiniClaw Team"
version: "1.0.0"
async_support: true
parameters:
  - name: "file_path"
    type: "str"
    required: true
    description: "要读取的文件路径（相对于 /tmp/miniclaw_files）"
  - name: "encoding"
    type: "str"
    required: false
    default: "utf-8"
    description: "文件编码格式"
---

# 文件读取技能

## 功能说明

安全读取指定目录下的文件内容，适用于读取配置文件、日志文件、导出数据等场景。

**安全限制**：仅允许访问 `/tmp/miniclaw_files` 目录，防止任意文件访问风险。

## 使用示例

### 示例 1：读取文本文件

用户请求："帮我读取 example.txt 文件"

执行步骤：
1. 接收参数：`{"file_path": "example.txt", "encoding": "utf-8"}`
2. 构建完整路径：`/tmp/miniclaw_files/example.txt`
3. 安全检查：确认路径在允许范围内
4. 读取文件内容
5. 返回结果：`{"content": "文件内容...", "size": 123}`

### 示例 2：读取 JSON 配置

用户请求："读取 config.json 配置文件"

```json
{
  "file_path": "config.json",
  "encoding": "utf-8"
}
```

响应：
```json
{
  "file_path": "/tmp/miniclaw_files/config.json",
  "content": "{\"key\": \"value\"}",
  "size": 45
}
```

## 异常处理

1. **文件不存在**: `FileNotFoundError: 文件不存在：xxx`
   - 原因：指定路径下没有该文件
   - 解决：检查文件路径是否正确

2. **路径不安全**: `ValueError: 不允许访问该路径`
   - 原因：尝试访问禁止的目录（如 `/etc/passwd`）
   - 解决：只能使用相对于 `/tmp/miniclaw_files` 的路径

3. **权限不足**: `PermissionError: 没有读取权限`
   - 原因：文件权限设置问题
   - 解决：修改文件权限或联系管理员

4. **编码错误**: `UnicodeDecodeError: 无法解码文件`
   - 原因：文件编码与指定不符
   - 解决：尝试其他编码（如 gbk, latin-1）

## 最佳实践

✅ **推荐**：
- 明确指定文件编码（默认 utf-8）
- 确保文件在安全目录内
- 读取大文件前确认内存充足

❌ **避免**：
- 尝试访问系统文件
- 读取超大文件（>100MB）
- 依赖默认编码而不指定