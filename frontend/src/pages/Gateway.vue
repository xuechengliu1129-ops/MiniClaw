<template>
  <div class="gateway-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🌐 网关监控</span>
          <el-button @click="refreshStats" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="总请求数" :value="stats.totalRequests" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="平均响应时间 (ms)" :value="stats.avgResponseTime" :precision="2" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="活跃客户端" :value="stats.activeClients" />
        </el-col>
      </el-row>
      
      <el-divider />
      
      <h3>请求日志</h3>
      <el-table :data="logs" style="width: 100%" max-height="400" v-loading="loading">
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="getMethodType(row.method)">
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" show-overflow-tooltip />
        <el-table-column prop="user_id" label="用户 ID" width="100" />
        <el-table-column prop="elapsed_time" label="耗时 (ms)" width="100">
          <template #default="{ row }">
            <el-tag :type="getTimeType(row.elapsed_time)">
              {{ (row.elapsed_time * 1000).toFixed(0) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'COMPLETED' ? 'success' : 'danger'" size="small">
              {{ row.status === 'COMPLETED' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const stats = ref({
  totalRequests: 0,
  avgResponseTime: 0,
  activeClients: 0,
})

const logs = ref([])

const getMethodType = (method) => {
  const typeMap = {
    GET: '',
    POST: 'success',
    PUT: 'warning',
    DELETE: 'danger',
  }
  return typeMap[method] || ''
}

const getTimeType = (time) => {
  if (time < 0.1) return 'success'
  if (time < 0.5) return 'warning'
  return 'danger'
}

const loadStats = async () => {
  loading.value = true
  try {
    // TODO: 调用 API 加载统计数据
    stats.value = {
      totalRequests: 1024,
      avgResponseTime: 0.125,
      activeClients: 45,
    }
    
    // 模拟日志数据
    logs.value = [
      {
        timestamp: '2025-01-15 10:30:00',
        method: 'GET',
        path: '/api/v1/skills',
        user_id: 1,
        elapsed_time: 0.089,
        status: 'COMPLETED',
      },
      {
        timestamp: '2025-01-15 10:29:55',
        method: 'POST',
        path: '/api/v1/skills/web_search/execute',
        user_id: 1,
        elapsed_time: 0.234,
        status: 'COMPLETED',
      },
    ]
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

const refreshStats = () => {
  loadStats()
  ElMessage.success('统计已刷新')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.gateway-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
