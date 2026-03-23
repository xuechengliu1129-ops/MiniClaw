<template>
  <div class="memory-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🧠 记忆管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加记忆
          </el-button>
        </div>
      </template>
      
      <el-table :data="memories" style="width: 100%" v-loading="loading">
        <el-table-column prop="content" label="内容" show-overflow-tooltip />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)">
              {{ getLevelText(row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="importance" label="重要性" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.importance * 100" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column prop="access_count" label="访问次数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewMemory(row)">查看</el-button>
            <el-button size="small" type="danger" @click="deleteMemory(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const memories = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const getLevelText = (level) => {
  const levelMap = {
    user: '用户级',
    skill: '技能级',
    global: '全局级',
  }
  return levelMap[level] || level
}

const getLevelType = (level) => {
  const typeMap = {
    user: '',
    skill: 'warning',
    global: 'success',
  }
  return typeMap[level] || ''
}

const loadMemories = async () => {
  loading.value = true
  try {
    // TODO: 调用 API 加载记忆
    memories.value = []
  } catch (error) {
    ElMessage.error('加载记忆失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  ElMessage.info('添加记忆功能待实现')
}

const viewMemory = (row) => {
  ElMessage.info(`查看记忆：${row.id}`)
}

const deleteMemory = async (row) => {
  // TODO: 实现删除逻辑
  ElMessage.success('记忆已删除')
}

onMounted(() => {
  loadMemories()
})
</script>

<style scoped>
.memory-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
