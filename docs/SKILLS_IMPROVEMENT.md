# Skills 功能改进文档

## 📋 改进内容

### 1. 前端界面改进

#### ✅ 分类展示 Skills
- **系统 Skills**: 显示系统内置的技能（作者为 System、DeepAgent、Admin）
- **自定义 Skills**: 显示用户创建的技能，带有删除按钮
- **类型标识**: 使用不同颜色的标签区分系统和自定义技能

#### ✅ 新增功能
- 删除技能功能（带确认对话框）
- 实时统计技能总数
- 更清晰的界面布局

### 2. 后端 API 改进

#### ✅ 新增删除接口
```http
DELETE /api/v1/skills/{skill_name}
```

**功能**:
- 验证技能名称格式
- 检查技能目录是否存在
- 删除整个技能文件夹（包括 SKILL.md）
- 返回删除结果

#### ✅ 增强列表接口
```http
GET /api/v1/skills
```

**新增字段**:
- `is_system`: Boolean 值，标识是否为系统技能

### 3. 文件操作

#### 创建技能流程
1. 验证技能名称（仅允许字母、数字、下划线）
2. 在 `backend/core/skills/custom_skills/` 创建目录
3. 生成 SKILL.md 文件（包含 YAML frontmatter 和 Markdown 内容）
4. 后台触发热重载（可选）

#### 删除技能流程
1. 验证技能名称
2. 检查目录是否存在
3. 使用 `shutil.rmtree()` 删除整个文件夹
4. 记录日志

## 🎯 使用方法

### 创建技能

1. 访问前端 Skills 页面
2. 填写表单：
   - 技能名称（必填）：如 `file_reader`
   - 技能描述（必填）：详细描述功能
   - 作者（可选）：你的昵称
3. 点击"创建 SKILL.md"按钮
4. 系统会自动：
   - 创建目录：`backend/core/skills/custom_skills/file_reader/`
   - 生成文件：`SKILL.md`

### 查看技能

- **系统 Skills**: 自动显示在"系统 Skills"分类下
- **自定义 Skills**: 显示在"自定义 Skills"分类下，可删除

### 删除技能

1. 在"自定义 Skills"列表中找到目标技能
2. 点击右侧的"删除"按钮
3. 确认删除操作
4. 系统会：
   - 删除对应的文件夹
   - 从列表中移除

## 📁 目录结构示例

```
backend/core/skills/custom_skills/
├── file_reader/           # 已存在的技能
│   └── SKILL.md
├── feishu_notifier/      # 已存在的技能
│   └── SKILL.md
└── test_skill_001/       # 新创建的技能
    └── SKILL.md
```

## 🔧 API 测试

### 创建技能
```bash
curl -X POST http://localhost:8000/api/v1/skills \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_skill",
    "description": "测试技能",
    "author": "Test User",
    "version": "1.0.0"
  }'
```

### 获取技能列表
```bash
curl -X GET http://localhost:8000/api/v1/skills
```

### 删除技能
```bash
curl -X DELETE http://localhost:8000/api/v1/skills/test_skill
```

## 🚀 运行测试脚本

```bash
cd /Users/xuecheng.liu/code/MiniClaw/backend
conda activate MiniClaw
python test_skills_api.py
```

## ⚠️ 注意事项

1. **重启后端服务**: 创建或删除技能后，需要重启后端服务才能生效
2. **技能命名规范**: 
   - 只能包含字母、数字和下划线
   - 不能使用特殊字符或空格
3. **删除不可恢复**: 删除技能会永久删除对应的文件夹和文件
4. **系统技能保护**: 系统内置技能不允许删除（前端不显示删除按钮）

## 📝 SKILL.md 文件示例

```markdown
---
name: "my_skill"
description: "我的技能描述"
author: "Your Name"
version: "1.0.0"
async_support: true
parameters: []
created_at: "2026-03-23T14:00:00"
---

# 我的技能描述

## 功能说明

详细描述技能的功能...

## 使用示例

请参考技能实现。
```

## 🎨 界面截图说明

### 创建技能区域
- 表单输入：名称、描述、作者
- 创建按钮和重置按钮

### 系统 Skills 区域
- 表格展示：名称、描述、版本、作者、类型
- 类型标签：灰色"系统"

### 自定义 Skills 区域
- 表格展示：名称、描述、版本、作者、类型、操作
- 类型标签：绿色"自定义"
- 操作列：红色"删除"按钮

## 💡 未来优化方向

1. **热重载**: 实现无需重启后端服务即可加载新技能
2. **编辑功能**: 支持在线编辑 SKILL.md 文件
3. **导入导出**: 支持技能的导入和导出
4. **技能测试**: 提供技能功能测试界面
5. **版本管理**: 支持技能版本升级和历史记录
