<template>
  <div class="dashboard">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>📊 系统概览</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="技能总数" :value="stats.skills" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="记忆条数" :value="stats.memories" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="模型数量" :value="stats.models" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="今日请求" :value="stats.requests" />
        </el-col>
      </el-row>
    </el-card>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>🚀 快速开始</span>
          </template>
          <el-steps direction="vertical" :active="1">
            <el-step title="配置模型" description="在模型配置页面添加你的大模型" />
            <el-step title="启用技能" description="在技能管理页面启用需要的技能" />
            <el-step title="集成飞书" description="配置飞书机器人实现消息交互" />
            <el-step title="开始使用" description="通过聊天软件或 API 调用智能体" />
          </el-steps>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>📈 系统状态</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="服务状态">
              <el-tag type="success">运行中</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="版本">v0.1.0</el-descriptions-item>
            <el-descriptions-item label="运行时间">
              {{ stats.uptime }}
            </el-descriptions-item>
            <el-descriptions-item label="数据库">
              <el-tag type="success">已连接</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  skills: 0,
  memories: 0,
  models: 0,
  requests: 0,
  uptime: '0 小时 0 分钟',
})

// TODO: 加载真实数据
onMounted(() => {
  // 模拟数据
  stats.value = {
    skills: 5,
    memories: 128,
    models: 2,
    requests: 1024,
    uptime: '2 小时 15 分钟',
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.box-card {
  margin-bottom: 20px;
}
</style>
