<template>
  <div class="chat-page">
    <el-container class="chat-container">
      <!-- 左侧边栏 - 会话列表 -->
      <el-aside width="280px" class="chat-sidebar">
        <div class="sidebar-header">
          <el-button type="primary" @click="newChat" style="width: 100%">
            <el-icon><Plus /></el-icon>
            新建对话
          </el-button>
        </div>
        
        <el-scrollbar class="chat-list">
          <div
            v-for="session in chatSessions"
            :key="session.id"
            class="chat-item"
            :class="{ active: currentSessionId === session.id }"
            @click="selectSession(session.id)"
          >
            <div class="chat-title">{{ session.title }}</div>
            <div class="chat-time">{{ session.lastTime }}</div>
          </div>
        </el-scrollbar>
      </el-aside>
      
      <!-- 主聊天区域 -->
      <el-main class="chat-main">
        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesContainer">
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="message"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar
                :icon="message.role === 'user' ? 'User' : 'Cpu'"
                :size="40"
              />
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              <div class="message-time">{{ message.time }}</div>
            </div>
          </div>
          
          <!-- 加载中 -->
          <div v-if="loading" class="message assistant">
            <div class="message-avatar">
              <el-avatar :icon="'Cpu'" :size="40" />
            </div>
            <div class="message-content">
              <el-skeleton :rows="2" animated />
            </div>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息... (按 Enter 发送，Shift+Enter 换行)"
            :disabled="loading"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="input-actions">
            <div class="input-tips">
              <el-tooltip content="支持调用已启用的技能">
                <el-tag size="small" type="info">/技能名 调用技能</el-tag>
              </el-tooltip>
              <el-tooltip :content="`当前模型：${currentModel}`">
                <el-tag size="small" type="success">{{ currentModel }}</el-tag>
              </el-tooltip>
            </div>
            <el-button
              type="primary"
              :loading="loading"
              @click="sendMessage"
            >
              发送
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { sendMessage as sendChatMessage, getSessions, getSessionHistory, createSession } from '@/api/chat'
import { getModels } from '@/api/models'

const currentSessionId = ref(null)
const loading = ref(false)
const inputMessage = ref('')
const messagesContainer = ref(null)
const currentModel = ref('未配置')
const currentModelInfo = ref(null) // 存储完整的模型信息（包括 provider）

// 会话列表
const chatSessions = ref([])

// 消息列表
const messages = ref([])

// 加载会话列表
const loadSessions = async () => {
  try {
    const sessions = await getSessions()
    chatSessions.value = sessions || []
    if (chatSessions.value.length > 0 && !currentSessionId.value) {
      selectSession(chatSessions.value[0].id)
    }
  } catch (error) {
    console.error('加载会话失败:', error)
    // 如果 API 失败，使用本地模拟数据
    chatSessions.value = [
      { id: 1, title: '新建对话', lastTime: '刚刚' },
    ]
  }
}

// 新建对话
const newChat = async () => {
  try {
    const newSession = await createSession('新对话')
    chatSessions.value.unshift(newSession)
    currentSessionId.value = newSession.id
    messages.value = [{
      role: 'assistant',
      content: '你好！我是 MiniClaw 智能助手，有什么可以帮你的吗？',
      time: new Date().toLocaleTimeString(),
    }]
    ElMessage.success('新对话已创建')
  } catch (error) {
    // API 失败时使用本地逻辑
    const newId = Math.max(...chatSessions.value.map(s => s.id || 0), 0) + 1
    chatSessions.value.unshift({
      id: newId,
      title: '新对话',
      lastTime: '刚刚',
    })
    currentSessionId.value = newId
    messages.value = [{
      role: 'assistant',
      content: '你好！我是 MiniClaw 智能助手，有什么可以帮你的吗？',
      time: new Date().toLocaleTimeString(),
    }]
  }
}

// 选择会话
const selectSession = async (id) => {
  currentSessionId.value = id
  loading.value = true
  
  try {
    const history = await getSessionHistory(id)
    messages.value = history || [{
      role: 'assistant',
      content: '你好！我是 MiniClaw 智能助手，有什么可以帮你的吗？',
      time: new Date().toLocaleTimeString(),
    }]
  } catch (error) {
    console.error('加载历史消息失败:', error)
    messages.value = [{
      role: 'assistant',
      content: '你好！我是 MiniClaw 智能助手，有什么可以帮你的吗？',
      time: new Date().toLocaleTimeString(),
    }]
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }
  
  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString(),
  }
  
  messages.value.push(userMessage)
  const userMessageContent = inputMessage.value
  inputMessage.value = ''
  loading.value = true
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  try {
    // 调用真实 API，传入模型配置信息
    const response = await sendChatMessage({
      message: userMessageContent,
      session_id: currentSessionId.value,
      provider: currentModelInfo.value?.provider || 'ollama',
      model_name: currentModelInfo.value?.name || currentModel.value || 'qwen2:7b',
      api_key: currentModelInfo.value?.api_key || null,
    })
      
    const aiReply = {
      role: 'assistant',
      content: response.response || response.content || response.message || '收到消息',
      time: new Date().toLocaleTimeString(),
    }
    messages.value.push(aiReply)
    
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送失败：' + (error.message || '请检查后端服务'))
    
    // 添加错误提示消息
    messages.value.push({
      role: 'assistant',
      content: `❌ 请求失败：${error.message || '请检查后端服务是否启动'}`,
      time: new Date().toLocaleTimeString(),
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 格式化消息（支持简单 Markdown）
const formatMessage = (content) => {
  if (!content) return ''
  
  // 换行符转<br>
  return content
    .replace(/\n/g, '<br>')
    .replace(/`([^`]+)`/g, '<code style="background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 3px;">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

// 加载模型配置
const loadModels = async () => {
  try {
    const models = await getModels()
    // 查找激活的模型
    const activeModel = models?.find(m => m.status === 'active' || m.is_active)
    
    if (activeModel) {
      currentModel.value = activeModel.name
      currentModelInfo.value = activeModel // 存储完整信息
    } else if (models && models.length > 0) {
      currentModel.value = models[0].name
      currentModelInfo.value = models[0] // 存储第一个模型的信息
    }
  } catch (error) {
    console.error('加载模型失败:', error)
    currentModel.value = '未配置'
    currentModelInfo.value = null
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

onMounted(() => {
  loadSessions()
  loadModels()
  scrollToBottom()
})
</script>

<style scoped>
.chat-page {
  height: 100vh;
  overflow: hidden;
}

.chat-container {
  height: 100%;
}

.chat-sidebar {
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.chat-list {
  flex: 1;
}

.chat-item {
  padding: 15px 20px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.chat-item:hover {
  background: #e6f7ff;
}

.chat-item.active {
  background: #1890ff;
  color: white;
}

.chat-title {
  font-size: 14px;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-time {
  font-size: 12px;
  opacity: 0.6;
}

.chat-main {
  padding: 0;
  display: flex;
  flex-direction: column;
  background: white;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  margin: 0 15px;
}

.message.user .message-content {
  margin: 0 15px 0 0;
}

.message-text {
  padding: 12px 16px;
  border-radius: 8px;
  background: #f0f2f5;
  line-height: 1.6;
}

.message.user .message-text {
  background: #1890ff;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.input-area {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.input-tips {
  display: flex;
  gap: 10px;
}
</style>
