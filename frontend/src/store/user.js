import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 本地模式，固定用户信息
  const userInfo = ref({
    id: 1,
    username: 'local_user',
    roles: ['super_admin'],
    enabled: true,
  })
  
  /**
   * 初始化（无需登录）
   */
  function init() {
    console.log('✅ 本地模式已启动')
    return userInfo.value
  }
  
  /**
   * 获取用户信息
   */
  function getUserInfo() {
    return userInfo.value
  }
  
  /**
   * 检查是否已登录（始终返回 true）
   */
  function isLoggedIn() {
    return true
  }
  
  /**
   * 检查是否有指定角色（始终返回 true）
   */
  function hasRole(roleName) {
    return true
  }
  
  /**
   * 检查是否有指定权限（始终返回 true）
   */
  function hasPermission(permission) {
    return true
  }
  
  // 自动初始化
  init()
  
  return {
    userInfo,
    getUserInfo,
    isLoggedIn,
    hasRole,
    hasPermission,
  }
})