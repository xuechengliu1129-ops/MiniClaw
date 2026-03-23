<template>
  <div class="models-page">
    <el-card class="models-card">
      <template #header>
        <div class="card-header">
          <span>模型配置</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加模型
          </el-button>
        </div>
      </template>
      
      <el-table :data="models" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="name" label="模型名称" width="200" />
        <el-table-column prop="provider" label="提供商" width="120">
          <template #default="{ row }">
            <el-tag :type="getProviderType(row.provider)">
              {{ row.provider }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="endpoint" label="API 端点" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '已激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="温度" width="80" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="testModel(row)" :loading="row.testing">
              测试连接
            </el-button>
            <el-button
              size="small"
              :type="row.is_active ? 'warning' : 'primary'"
              @click="setActive(row)"
            >
              {{ row.is_active ? '停用' : '设为默认' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteModel(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加模型对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="添加模型"
      width="600px"
    >
      <el-form :model="newModel" label-width="120px">
        <el-form-item label="提供商" required>
          <el-select v-model="newModel.provider" placeholder="请选择" style="width: 100%" @change="handleProviderChange">
            <el-option label="Ollama (本地)" value="ollama" />
            <el-option label="Google Gemini" value="google" />
            <el-option label="NIO DeepSeek" value="nio" />
            <el-option label="OpenAI Compatible" value="openai" />
          </el-select>
        </el-form-item>
        
        <!-- NIO/OpenAI 配置 -->
        <template v-if="newModel.provider === 'nio' || newModel.provider === 'openai'">
          <el-alert 
            :title="newModel.provider === 'nio' ? 'NIO公司模型配置说明' : 'OpenAI 兼容 API 配置说明'" 
            type="info" 
            :closable="false"
            style="margin-bottom: 15px; padding: 10px;"
          >
            <p style="margin: 0 0 8px 0;"><strong>只需填写 2 个参数：</strong></p>
            <ol style="margin: 0; padding-left: 20px;">
              <li v-if="newModel.provider === 'nio'"><strong>模型名称</strong>：如 DeepSeek-V3.1（已预设）</li>
              <li v-else><strong>模型名称</strong>：如 gpt-3.5-turbo、gpt-4 等</li>
              <li><strong>API Key</strong>：从服务提供商获取</li>
            </ol>
            <p style="margin: 8px 0 0 0; color: #666;">
              <strong>Base URL（已预设）：</strong>
              <span v-if="newModel.provider === 'nio'">https://modelgateway.nioint.com/publicService/v1</span>
              <span v-else>用户自定义</span>
            </p>
          </el-alert>
          
          <el-form-item label="模型名称" required>
            <el-input 
              v-model="newModel.name" 
              :placeholder="newModel.provider === 'nio' ? 'DeepSeek-V3.1' : '例如：gpt-3.5-turbo'"
              clearable
            >
              <template #prefix>
                <span>🤖</span>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="API Key" required>
            <el-input 
              v-model="newModel.api_key" 
              type="password"
              placeholder="请输入 API Key"
              show-password
              clearable
            >
              <template #prefix>
                <span>🔑</span>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="Base URL" v-if="newModel.provider === 'openai'">
            <el-input 
              v-model="newModel.endpoint" 
              placeholder="https://api.openai.com/v1"
              clearable
            >
              <template #prefix>
                <span>🌐</span>
              </template>
            </el-input>
          </el-form-item>
        </template>
        
        <!-- Google Gemini 配置 -->
        <template v-else-if="newModel.provider === 'google'">
          <el-alert 
            title="Google Gemini 配置说明" 
            type="info" 
            :closable="false"
            style="margin-bottom: 15px; padding: 10px;"
          >
            <p style="margin: 0 0 8px 0;"><strong>只需填写 2 个参数：</strong></p>
            <ol style="margin: 0; padding-left: 20px;">
              <li><strong>模型名称</strong>：如 gemini-2.5-flash、gemini-2.0-flash-exp</li>
              <li><strong>API Key</strong>：从 <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a> 获取</li>
            </ol>
          </el-alert>
          
          <el-form-item label="模型名称" required>
            <el-input 
              v-model="newModel.name" 
              placeholder="例如：gemini-2.5-flash"
              clearable
            >
              <template #prefix>
                <span>🤖</span>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="API Key" required>
            <el-input 
              v-model="newModel.api_key" 
              type="password"
              placeholder="以 AIza 开头的 API Key"
              show-password
              clearable
            >
              <template #prefix>
                <span>🔑</span>
              </template>
            </el-input>
          </el-form-item>
        </template>
        
        <!-- Ollama 配置 -->
        <template v-else-if="newModel.provider === 'ollama'">
          <el-form-item label="模型名称" required>
            <el-input 
              v-model="newModel.name" 
              placeholder="例如：qwen2:0.5b"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="API 端点" required>
            <el-input 
              v-model="newModel.endpoint" 
              placeholder="http://localhost:11434"
              clearable
            />
          </el-form-item>
        </template>
        <el-form-item label="温度参数">
          <el-slider 
            v-model="newModel.temperature" 
            :min="0" 
            :max="2" 
            :step="0.1"
            style="width: 80%"
            :disabled="true"
          />
          <span style="margin-left: 10px; color: #999;">{{ newModel.temperature }}</span>
        </el-form-item>
        
        <el-form-item label="最大 Token">
          <el-input-number 
            v-model="newModel.max_tokens" 
            :min="100" 
            :max="32000"
            :step="100"
            :disabled="true"
          />
          <span style="margin-left: 10px; color: #999; font-size: 12px;">(自动设置)</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAdd" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getModels, addModel, updateModel, deleteModel as deleteModelApi, setActiveModel, testModel as testModelApi } from '@/api/models'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const newModel = ref({
  name: '',
  provider: 'ollama',
  endpoint: '',
  api_key: '',
  temperature: 0.7,
  max_tokens: 4096,
})

// 监听提供商变化，自动设置默认值
const handleProviderChange = () => {
  if (newModel.value.provider === 'nio') {
    // NIO公司模型的默认配置
    newModel.value.name = 'DeepSeek-V3.1'
    newModel.value.endpoint = 'https://modelgateway.nioint.com/publicService/v1'
    newModel.value.api_key = ''
  } else if (newModel.value.provider === 'openai') {
    // OpenAI 的默认配置
    newModel.value.name = 'gpt-3.5-turbo'
    newModel.value.endpoint = 'https://api.openai.com/v1'
    newModel.value.api_key = ''
  } else if (newModel.value.provider === 'google') {
    // Google Gemini 的默认配置
    newModel.value.name = 'gemini-2.0-flash-exp'
    newModel.value.endpoint = 'https://generativelanguage.googleapis.com'
    newModel.value.api_key = ''
  } else if (newModel.value.provider === 'ollama') {
    // Ollama 的默认配置
    newModel.value.name = ''
    newModel.value.endpoint = 'http://localhost:11434'
    newModel.value.api_key = ''
  }
}

const models = ref([])

const getProviderType = (provider) => {
  const types = {
    ollama: 'success',
    openai: 'primary',
    azure: 'warning',
    qwen: 'danger',
    ernie: 'info',
    custom: 'info',
  }
  return types[provider] || 'info'
}

// 加载模型列表
const loadModels = async () => {
  loading.value = true
  try {
    const data = await getModels()
    models.value = data || []
  } catch (error) {
    console.error('加载模型失败:', error)
    ElMessage.error('加载模型列表失败：' + (error.message || '请检查后端服务'))
    // 使用空数组
    models.value = []
  } finally {
    loading.value = false
  }
}

// 显示添加对话框
const showAddDialog = () => {
  newModel.value = {
    name: '',
    provider: 'ollama',
    endpoint: '',
    api_key: '',
    temperature: 0.7,
    max_tokens: 4096,
  }
  dialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
  // 根据提供商类型验证必填字段
  if (newModel.value.provider === 'google') {
    // Google Gemini: 只需要 name 和 api_key
    if (!newModel.value.name || !newModel.value.api_key) {
      ElMessage.warning('请填写模型名称和 API Key')
      return
    }
  } else if (newModel.value.provider === 'ollama') {
    // Ollama: 需要 name 和 endpoint
    if (!newModel.value.name || !newModel.value.endpoint) {
      ElMessage.warning('请填写模型名称和 API 端点')
      return
    }
  } else {
    // 其他提供商：需要 name 和 endpoint
    if (!newModel.value.name || !newModel.value.endpoint) {
      ElMessage.warning('请填写必填项')
      return
    }
  }
  
  // 🔍 调试：打印实际发送的数据
  console.log('📤 准备发送的模型数据:', JSON.parse(JSON.stringify(newModel.value)))
  
  saving.value = true
  try {
    await addModel(newModel.value)
    ElMessage.success('模型添加成功')
    dialogVisible.value = false
    await loadModels()
  } catch (error) {
    console.error('添加模型失败:', error)
    ElMessage.error('添加失败：' + (error.message || '请检查后端服务'))
  } finally {
    saving.value = false
  }
}

// 设为默认
const setActive = async (row) => {
  try {
    await setActiveModel(row.id)
    ElMessage.success(`已将 ${row.name} 设为默认模型`)
    await loadModels()
  } catch (error) {
    console.error('设置默认模型失败:', error)
    ElMessage.error('设置失败：' + (error.message || '请检查后端服务'))
  }
}

// 测试连接
const testModel = async (row) => {
  row.testing = true
  try {
    const result = await testModelApi(row.id)
    ElMessage.success(`连接测试成功：${row.name}\n响应：${result.message || 'OK'}`)
  } catch (error) {
    console.error('测试连接失败:', error)
    console.error('错误详情:', error.response?.data)
    
    // 显示详细错误信息
    let errorMsg = `连接测试失败：${error.message || '无法连接到模型服务'}`
    if (error.response?.data?.detail) {
      errorMsg += `\n\n详细信息：\n${error.response.data.detail}`
    }
    ElMessage.error(errorMsg)
  } finally {
    row.testing = false
  }
}

// 删除模型
const deleteModel = async (row) => {
  ElMessageBox.confirm(
    `确定要删除模型 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteModelApi(row.id)
      ElMessage.success('模型已删除')
      await loadModels()
    } catch (error) {
      console.error('删除模型失败:', error)
      ElMessage.error('删除失败：' + (error.message || '请检查后端服务'))
    }
  }).catch(() => {
    // 取消删除
  })
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.models-page {
  padding: 20px;
}

.models-card {
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
