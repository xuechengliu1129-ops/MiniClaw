<template>
  <div class="feishu-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📨 飞书集成</span>
        </div>
      </template>
      
      <el-form :model="config" label-width="150px">
        <el-form-item label="App ID">
          <el-input v-model="config.appId" placeholder="cli_xxxxxxxxxxxxx" />
        </el-form-item>
        
        <el-form-item label="App Secret">
          <el-input
            v-model="config.appSecret"
            type="password"
            show-password
            placeholder="请输入 App Secret"
          />
        </el-form-item>
        
        <el-form-item label="Verification Token">
          <el-input
            v-model="config.verificationToken"
            placeholder="验证 Token"
          />
        </el-form-item>
        
        <el-form-item label="Encrypt Key">
          <el-input
            v-model="config.encryptKey"
            placeholder="加密密钥（可选）"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
          <el-button @click="testConnection">测试连接</el-button>
        </el-form-item>
      </el-form>
      
      <el-divider />
      
      <el-descriptions title="机器人状态" :column="1" border>
        <el-descriptions-item label="连接状态">
          <el-tag :type="connected ? 'success' : 'danger'">
            {{ connected ? '已连接' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最后同步时间">
          {{ lastSyncTime || '从未同步' }}
        </el-descriptions-item>
        <el-descriptions-item label="消息统计">
          今日接收：{{ stats.messagesReceived }} | 今日发送：{{ stats.messagesSent }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>📖 配置说明</span>
      </template>
      <el-steps direction="vertical" :active="3">
        <el-step
          title="创建应用"
          description="登录飞书开放平台，创建企业自建应用"
        />
        <el-step
          title="获取凭证"
          description="复制 App ID、App Secret、Verification Token"
        />
        <el-step
          title="配置权限"
          description="添加机器人、消息收发等权限"
        />
        <el-step
          title="订阅事件"
          description="订阅接收消息事件，配置回调地址"
        />
      </el-steps>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const config = ref({
  appId: '',
  appSecret: '',
  verificationToken: '',
  encryptKey: '',
})

const connected = ref(false)
const lastSyncTime = ref(null)
const stats = ref({
  messagesReceived: 0,
  messagesSent: 0,
})

const saveConfig = () => {
  // TODO: 调用 API 保存配置
  ElMessage.success('配置已保存')
}

const testConnection = async () => {
  // TODO: 调用 API 测试连接
  ElMessage.info('正在测试连接...')
  setTimeout(() => {
    connected.value = true
    lastSyncTime.value = new Date().toLocaleString()
    ElMessage.success('连接成功')
  }, 1000)
}

onMounted(() => {
  // TODO: 加载已保存的配置
})
</script>

<style scoped>
.feishu-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
