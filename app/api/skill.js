/**
 * 技能管理相关API模块
 * @module api/skill
 */

import request from './request.js'

/**
 * 技能类型枚举
 * @readonly
 * @enum {string}
 */
export const SkillType = {
  /** 用户技能 */
  USER: 'user',
  /** 设备技能 */
  DEVICE: 'device'
}

/**
 * 技能类型标签映射
 * @readonly
 * @type {Object.<string, string>}
 */
export const SkillTypeLabel = {
  [SkillType.USER]: '用户技能',
  [SkillType.DEVICE]: '设备技能'
}

/**
 * 技能类型颜色映射
 * @readonly
 * @type {Object.<string, string>}
 */
export const SkillTypeColor = {
  [SkillType.USER]: '#1989fa',
  [SkillType.DEVICE]: '#07c160'
}

/**
 * 技能信息
 * @typedef {Object} Skill
 * @property {number} id - 技能ID
 * @property {string} code - 技能编码
 * @property {string} name - 技能名称
 * @property {string} type - 技能类型 (user/device)
 * @property {string} type_display - 技能类型显示名称
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 */

/**
 * 创建技能请求参数
 * @typedef {Object} CreateSkillParams
 * @property {string} code - 技能编码（必填，唯一）
 * @property {string} name - 技能名称（必填）
 * @property {string} [type] - 技能类型（可选，默认为 user）
 */

/**
 * 更新技能请求参数
 * @typedef {Object} UpdateSkillParams
 * @property {string} [code] - 技能编码
 * @property {string} [name] - 技能名称
 * @property {string} [type] - 技能类型
 */

/**
 * 用户技能关联信息
 * @typedef {Object} UserSkill
 * @property {number} id - 关联ID
 * @property {number} user - 用户ID
 * @property {string} user_name - 用户名称
 * @property {number} skill - 技能ID
 * @property {string} skill_code - 技能编码
 * @property {string} skill_name - 技能名称
 * @property {string} create_datetime - 创建时间
 */

/**
 * 设备技能关联信息
 * @typedef {Object} DeviceSkill
 * @property {number} id - 关联ID
 * @property {number} device - 设备ID
 * @property {string} device_name - 设备名称
 * @property {number} skill - 技能ID
 * @property {string} skill_code - 技能编码
 * @property {string} skill_name - 技能名称
 * @property {string} create_datetime - 创建时间
 */

/**
 * 技能管理API对象
 * @namespace
 */
const skillApi = {
  /**
   * 获取技能列表
   * @param {Object} [params] - 查询参数
   * @param {string} [params.name] - 技能名称过滤
   * @param {string} [params.code] - 技能编码过滤
   * @param {string} [params.type] - 技能类型过滤 (user/device)
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<Object>} 返回技能列表的Promise
   * @example
   * skillApi.getSkillList()
   *   .then(res => console.log(res.data))
   * @example
   * skillApi.getSkillList({ name: '焊接', type: 'user' })
   *   .then(res => console.log(res.data))
   */
  getSkillList(params = {}) {
    return request({
      url: '/api/mes/skills/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建技能
   * @param {CreateSkillParams} data - 创建参数
   * @returns {Promise<Object>} 返回创建结果的Promise
   * @example
   * skillApi.createSkill({ code: 'SK001', name: '焊接技能', type: 'user' })
   *   .then(res => console.log(res.data))
   */
  createSkill(data) {
    return request({
      url: '/api/mes/skills/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        type: data.type || SkillType.USER
      }
    })
  },

  /**
   * 获取技能详情
   * @param {number} id - 技能ID
   * @returns {Promise<Object>} 返回技能详情的Promise
   * @example
   * skillApi.getSkillDetail(1)
   *   .then(res => console.log(res.data))
   */
  getSkillDetail(id) {
    return request({
      url: `/api/mes/skills/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新技能
   * @param {number} id - 技能ID
   * @param {UpdateSkillParams} data - 更新参数
   * @returns {Promise<Object>} 返回更新结果的Promise
   * @example
   * skillApi.updateSkill(1, { name: '新技能名' })
   *   .then(res => console.log(res.data))
   */
  updateSkill(id, data) {
    return request({
      url: `/api/mes/skills/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        type: data.type
      }
    })
  },

  /**
   * 删除技能
   * @param {number} id - 技能ID
   * @returns {Promise<Object>} 返回删除结果的Promise
   * @example
   * skillApi.deleteSkill(1)
   *   .then(res => console.log(res.msg))
   */
  deleteSkill(id) {
    return request({
      url: `/api/mes/skills/${id}/`,
      method: 'DELETE'
    })
  },

  /**
   * 获取用户技能列表
   * @param {Object} [params] - 查询参数
   * @param {number} [params.user] - 用户ID过滤
   * @param {number} [params.skill] - 技能ID过滤
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<Object>} 返回用户技能列表的Promise
   */
  getUserSkillList(params = {}) {
    return request({
      url: '/api/mes/skills/users/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建用户技能关联
   * @param {Object} data - 创建参数
   * @param {number} data.user - 用户ID
   * @param {number} data.skill - 技能ID
   * @returns {Promise<Object>} 返回创建结果的Promise
   */
  createUserSkill(data) {
    return request({
      url: '/api/mes/skills/users/',
      method: 'POST',
      data: {
        user: data.user,
        skill: data.skill
      }
    })
  },

  /**
   * 删除用户技能关联
   * @param {number} id - 用户技能关联ID
   * @returns {Promise<Object>} 返回删除结果的Promise
   */
  deleteUserSkill(id) {
    return request({
      url: `/api/mes/skills/users/${id}/`,
      method: 'DELETE'
    })
  },

  /**
   * 获取设备技能列表
   * @param {Object} [params] - 查询参数
   * @param {number} [params.device] - 设备ID过滤
   * @param {number} [params.skill] - 技能ID过滤
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<Object>} 返回设备技能列表的Promise
   */
  getDeviceSkillList(params = {}) {
    return request({
      url: '/api/mes/skills/devices/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建设备技能关联
   * @param {Object} data - 创建参数
   * @param {number} data.device - 设备ID
   * @param {number} data.skill - 技能ID
   * @returns {Promise<Object>} 返回创建结果的Promise
   */
  createDeviceSkill(data) {
    return request({
      url: '/api/mes/skills/devices/',
      method: 'POST',
      data: {
        device: data.device,
        skill: data.skill
      }
    })
  },

  /**
   * 删除设备技能关联
   * @param {number} id - 设备技能关联ID
   * @returns {Promise<Object>} 返回删除结果的Promise
   */
  deleteDeviceSkill(id) {
    return request({
      url: `/api/mes/skills/devices/${id}/`,
      method: 'DELETE'
    })
  }
}

export default skillApi
