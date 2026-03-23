import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截器（本地模式，无需 Token）
request.interceptors.request.use(
  (config) => {
    // 本地模式，不需要认证头
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const responseData = response.data
    
    // 兼容两种响应格式：
    // 1. { code: 200, message: "xxx", data: {...} }
    // 2. {...} (FastAPI 直接返回数据)
    if (responseData.code !== undefined && responseData.data !== undefined) {
      // 格式 1：统一封装格式
      const { code, message, data } = responseData
      if (code === 200 || code === 0) {
        return data
      } else {
        ElMessage.error(message || '请求失败')
        return Promise.reject(new Error(message || '请求失败'))
      }
    } else {
      // 格式 2：FastAPI 直接返回数据
      return responseData
    }
  },
  (error) => {
    // 处理 HTTP 错误
    if (error.response) {
      switch (error.response.status) {
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 429:
          ElMessage.error('请求过于频繁')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request
