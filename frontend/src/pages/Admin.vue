<template>
  <div class="admin-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚙️ 权限管理</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="用户管理" name="users">
          <el-button type="primary" @click="showAddUserDialog" style="margin-bottom: 15px;">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>
          
          <el-table :data="users" style="width: 100%" v-loading="loading">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column label="角色" width="300">
              <template #default="{ row }">
                <el-tag
                  v-for="role in row.roles"
                  :key="role"
                  size="small"
                  style="margin-right: 5px;"
                >
                  {{ getRoleName(role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'danger'">
                  {{ row.enabled ? '已启用' : '已禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="editUser(row)">编辑</el-button>
                <el-button size="small" @click="resetPassword(row)">重置密码</el-button>
                <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="角色管理" name="roles">
          <el-table :data="roles" style="width: 100%">
            <el-table-column prop="name" label="角色名称" width="200" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column label="权限" min-width="300">
              <template #default="{ row }">
                <el-tag
                  v-for="permission in row.permissions"
                  :key="permission"
                  size="small"
                  style="margin-right: 5px;"
                >
                  {{ permission }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_system" type="warning">系统</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('users')
const loading = ref(false)
const users = ref([])
const roles = ref([])

const roleMap = {
  super_admin: '超级管理员',
  normal_user: '普通用户',
  skill_developer: '技能开发者',
  readonly_user: '只读用户',
}

const getRoleName = (role) => {
  return roleMap[role] || role
}

const loadUsers = async () => {
  loading.value = true
  try {
    // TODO: 调用 API 加载用户
    users.value = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@miniclaw.com',
        roles: ['super_admin'],
        enabled: true,
      },
      {
        id: 2,
        username: 'user1',
        email: 'user1@example.com',
        roles: ['normal_user'],
        enabled: true,
      },
    ]
  } catch (error) {
    ElMessage.error('加载用户失败')
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  // TODO: 调用 API 加载角色
  roles.value = [
    {
      name: 'super_admin',
      description: '系统超级管理员，拥有所有权限',
      permissions: ['api:access', 'skill:execute', 'memory:read', 'memory:write', 'model:config', 'admin:access'],
      is_system: true,
    },
    {
      name: 'normal_user',
      description: '普通用户，基础使用权限',
      permissions: ['api:access', 'skill:execute', 'memory:read', 'memory:write'],
      is_system: true,
    },
  ]
}

const showAddUserDialog = () => {
  ElMessage.info('添加用户功能待实现')
}

const editUser = (row) => {
  ElMessage.info(`编辑用户：${row.username}`)
}

const resetPassword = (row) => {
  ElMessage.info(`重置用户密码：${row.username}`)
}

const deleteUser = async (row) => {
  // TODO: 实现删除逻辑
  ElMessage.success('用户已删除')
}

onMounted(() => {
  loadUsers()
  loadRoles()
})
</script>

<style scoped>
.admin-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
