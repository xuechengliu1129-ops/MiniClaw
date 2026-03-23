<template>
  <div id="app">
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon :size="24"><Grid /></el-icon>
            <span>MiniClaw</span>
          </div>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="header-menu"
          >
            <el-menu-item index="/">
              <el-icon><ChatDotRound /></el-icon>
              对话
            </el-menu-item>
            <el-menu-item index="/dashboard">
              <el-icon><DataAnalysis /></el-icon>
              仪表盘
            </el-menu-item>
            <el-menu-item index="/skills">
              <el-icon><Tools /></el-icon>
              技能管理
            </el-menu-item>
            <el-menu-item index="/models">
              <el-icon><Setting /></el-icon>
              模型配置
            </el-menu-item>
            <el-menu-item index="/memory">
              <el-icon><Collection /></el-icon>
              记忆管理
            </el-menu-item>
            <el-menu-item index="/feishu">
              <el-icon><Message /></el-icon>
              飞书集成
            </el-menu-item>
            <el-menu-item index="/gateway">
              <el-icon><Monitor /></el-icon>
              网关监控
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  width: 100%;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.main-container {
  height: 100%;
}

.app-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px;
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  margin-right: 40px;
}

.header-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.main-content {
  padding: 0;
  overflow: auto;
  background: #f5f7fa;
}
</style>
