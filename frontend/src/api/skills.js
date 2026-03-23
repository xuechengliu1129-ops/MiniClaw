/**
 * Skills API 接口
 */
import request from './request'

/**
 * 获取所有技能列表
 */
export function listSkills() {
  return request({
    url: '/skills',
    method: 'get',
  })
}

/**
 * 创建新技能（生成 SKILL.md）
 */
export function createSkill(data) {
  return request({
    url: '/skills',
    method: 'post',
    data,
  })
}

/**
 * 删除技能
 */
export function deleteSkill(skillName) {
  return request({
    url: `/skills/${skillName}`,
    method: 'delete',
  })
}

// 默认导出（兼容 import skillsApi from '@/api/skills'）
export default {
  listSkills,
  createSkill,
  deleteSkill,
}