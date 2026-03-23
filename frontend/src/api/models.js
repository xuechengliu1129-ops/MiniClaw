import request from './request'

/**
 * 获取模型列表
 */
export function getModels() {
  return request({
    url: '/models',
    method: 'get',
  })
}

/**
 * 添加模型
 */
export function addModel(data) {
  return request({
    url: '/models',
    method: 'post',
    data,
  })
}

/**
 * 更新模型
 */
export function updateModel(id, data) {
  return request({
    url: `/models/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除模型
 */
export function deleteModel(id) {
  return request({
    url: `/models/${id}`,
    method: 'delete',
  })
}

/**
 * 设置默认模型
 */
export function setActiveModel(id) {
  return request({
    url: `/models/${id}/active`,
    method: 'post',
  })
}

/**
 * 测试模型连接
 */
export function testModel(id) {
  return request({
    url: `/models/${id}/test`,
    method: 'post',
  })
}
