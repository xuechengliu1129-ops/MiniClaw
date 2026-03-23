import request from './request'

/**
 * 发送聊天消息
 */
export function sendMessage(data) {
  return request({
    url: '/chat/completions',
    method: 'post',
    data,
  })
}

/**
 * 获取会话列表
 */
export function getSessions() {
  return request({
    url: '/chat/sessions',
    method: 'get',
  })
}

/**
 * 获取会话历史消息
 */
export function getSessionHistory(sessionId) {
  return request({
    url: `/chat/sessions/${sessionId}/history`,
    method: 'get',
  })
}

/**
 * 创建新会话
 */
export function createSession(title) {
  return request({
    url: '/chat/sessions',
    method: 'post',
    data: { title },
  })
}

/**
 * 删除会话
 */
export function deleteSession(sessionId) {
  return request({
    url: `/chat/sessions/${sessionId}`,
    method: 'delete',
  })
}
