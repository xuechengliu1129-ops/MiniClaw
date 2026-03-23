<template>
  <div class="skills-page">
    <h1>🛠️ 技能管理（DeepAgent）</h1>
    
    <div class="info-box">
      <p><strong>核心理念：</strong>只需编写 SKILL.md 文档，DeepAgent 自动识别和执行</p>
      <p><strong>目录位置：</strong><code>backend/core/skills/custom_skills/</code></p>
    </div>
    
    <!-- 创建新技能 -->
    <div class="create-skill-section">
      <h2>➕ 创建新技能（生成 SKILL.md）</h2>
      <el-form :model="newSkill" label-width="120px">
        <el-form-item label="技能名称" required>
          <el-input v-model="newSkill.name" placeholder="例如：file_reader, weather_query" />
        </el-form-item>
        
        <el-form-item label="技能描述" required>
          <el-input v-model="newSkill.description" type="textarea" :rows="3" 
                    placeholder="详细描述技能的功能和使用方法" />
        </el-form-item>
        
        <el-form-item label="作者">
          <el-input v-model="newSkill.author" placeholder="你的昵称" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleCreateSkill" :loading="creating">
            创建 SKILL.md
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 技能列表 -->
    <div class="skills-list-section">
      <h2>📦 已加载的技能 ({{ totalSkills }})</h2>
      
      <!-- 系统 Skills -->
      <div v-if="systemSkills.length > 0" class="skill-category">
        <h3>🔧 系统 Skills</h3>
        <el-table :data="systemSkills" stripe style="margin-bottom: 20px;">
          <el-table-column prop="name" label="名称" width="200" />
          <el-table-column prop="description" label="描述" min-width="300" />
          <el-table-column prop="version" label="版本" width="100" />
          <el-table-column prop="author" label="作者" width="150" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag type="info">系统</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 自定义 Skills -->
      <div v-if="customSkills.length > 0" class="skill-category">
        <h3>🎨 自定义 Skills</h3>
        <el-table :data="customSkills" stripe>
          <el-table-column prop="name" label="名称" width="200" />
          <el-table-column prop="description" label="描述" min-width="300" />
          <el-table-column prop="version" label="版本" width="100" />
          <el-table-column prop="author" label="作者" width="150" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag type="success">自定义</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button 
                size="small" 
                type="danger" 
                @click="handleDeleteSkill(row)"
                :loading="row.deleting"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <el-alert 
        v-if="totalSkills === 0"
        title="暂无技能"
        description="请创建新技能或重启后端服务以加载 Skills"
        type="info"
        show-icon
      />
      
      <div class="refresh-tip" style="margin-top: 15px;">
        <el-tag type="warning">提示</el-tag>
        <span style="margin-left: 10px;">
          新建或修改 SKILL.md 后需要重启后端服务才能生效
        </span>
      </div>
    </div>
    
    <!-- 使用指南 -->
    <div class="guide-section">
      <h2>📖 如何使用</h2>
      <ol>
        <li>填写表单创建技能（自动生成 SKILL.md）</li>
        <li>重启后端服务（或手动触发热重载）</li>
        <li>在聊天中直接使用："帮我读取 xxx 文件"</li>
        <li>DeepAgent 会自动调用对应的技能</li>
      </ol>
      
      <h3>示例 SKILL.md 结构</h3>
      <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px;">
---
name: "my_skill"
description: "我的技能描述"
author: "Your Name"
async_support: true
parameters:
  - name: "param1"
    type: "str"
    required: true
---

# 功能说明

详细描述...

# 使用示例

示例代码...
      </pre>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import skillsApi from '@/api/skills'

const newSkill = reactive({
  name: '',
  description: '',
  author: 'Local User',
})

const creating = ref(false)
const allSkills = ref([])

// 计算属性：分类展示 Skills
const systemSkills = computed(() => {
  // 系统技能通常是内置的，作者不是 "Local User" 或自定义作者
  const systemAuthors = ['System', 'DeepAgent', 'Admin']
  return allSkills.value.filter(skill => 
    systemAuthors.includes(skill.author) || skill.is_system === true
  )
})

const customSkills = computed(() => {
  // 自定义技能是用户创建的
  const systemAuthors = ['System', 'DeepAgent', 'Admin']
  return allSkills.value.filter(skill => 
    !systemAuthors.includes(skill.author) && skill.is_system !== true
  )
})

const totalSkills = computed(() => allSkills.value.length)

// 加载技能列表
const loadSkills = async () => {
  try {
    const data = await skillsApi.listSkills()
    allSkills.value = data || []
  } catch (error) {
    console.error('加载技能列表失败:', error)
    ElMessage.error('加载技能列表失败')
  }
}

// 创建技能
const handleCreateSkill = async () => {
  if (!newSkill.name || !newSkill.description) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  try {
    creating.value = true
    
    await skillsApi.createSkill({
      name: newSkill.name,
      description: newSkill.description,
      author: newSkill.author,
      version: '1.0.0',
      parameters: [],
    })
    
    ElMessage.success(`技能 ${newSkill.name} 创建成功！请重启后端服务。`)
    resetForm()
    loadSkills()
    
  } catch (error) {
    console.error('创建技能失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建技能失败')
  } finally {
    creating.value = false
  }
}

// 删除技能
const handleDeleteSkill = async (skill) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除技能 "${skill.name}" 吗？这将删除对应的 SKILL.md 文件且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    skill.deleting = true
    
    await skillsApi.deleteSkill(skill.name)
    
    ElMessage.success(`技能 ${skill.name} 已删除`)
    loadSkills()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除技能失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除技能失败')
    }
  } finally {
    skill.deleting = false
  }
}

// 重置表单
const resetForm = () => {
  newSkill.name = ''
  newSkill.description = ''
  newSkill.author = 'Local User'
}

onMounted(() => {
  loadSkills()
})
</script>

<style scoped>
.skills-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

h2 {
  color: #555;
  font-size: 18px;
  margin: 20px 0 15px;
}

h3 {
  color: #666;
  font-size: 16px;
  margin: 15px 0 10px;
}

.info-box {
  background: #e6f7ff;
  border: 1px solid #b3e0ff;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
}

.info-box p {
  margin: 5px 0;
}

.info-box code {
  background: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.create-skill-section,
.skills-list-section,
.guide-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.skill-category {
  margin-bottom: 30px;
}

.refresh-tip {
  display: flex;
  align-items: center;
  color: #666;
}

.guide-section ol {
  line-height: 2;
  color: #555;
}

.guide-section h3 {
  margin-top: 20px;
  color: #333;
}
</style>