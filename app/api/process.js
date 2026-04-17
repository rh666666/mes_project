/**
 * 工序管理相关API模块
 * @module api/process
 */

import request from './request.js'

/**
 * 工序信息
 * @typedef {Object} Process
 * @property {number} id - 工序ID
 * @property {string} code - 工序编码
 * @property {string} name - 工序名称
 * @property {string|null} description - 工序描述
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 */

/**
 * 工序技能需求信息
 * @typedef {Object} ProcessSkillRequired
 * @property {number} id - 关联ID
 * @property {number} process - 工序ID
 * @property {string} process_name - 工序名称
 * @property {number} skill - 技能ID
 * @property {string} skill_code - 技能编码
 * @property {string} skill_name - 技能名称
 * @property {string} create_datetime - 创建时间
 */

/**
 * 创建工序请求参数
 * @typedef {Object} CreateProcessParams
 * @property {string} code - 工序编码（必填，唯一）
 * @property {string} name - 工序名称（必填）
 * @property {string} [description] - 工序描述（可选）
 */

/**
 * 更新工序请求参数
 * @typedef {Object} UpdateProcessParams
 * @property {string} [code] - 工序编码
 * @property {string} [name] - 工序名称
 * @property {string} [description] - 工序描述
 */

/**
 * 创建工序技能需求请求参数
 * @typedef {Object} CreateProcessSkillParams
 * @property {number} process - 工序ID
 * @property {number} skill - 技能ID
 */

/**
 * 工序管理API对象
 * @namespace
 */
const processApi = {
  /**
   * 获取工序列表
   * @param {Object} [params] - 查询参数
   * @param {string} [params.name] - 工序名称过滤
   * @param {string} [params.code] - 工序编码过滤
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<Object>} 返回工序列表的Promise
   * @example
   * processApi.getProcessList()
   *   .then(res => console.log(res.data))
   * @example
   * processApi.getProcessList({ name: '焊接', code: 'HJ' })
   *   .then(res => console.log(res.data))
   */
  getProcessList(params = {}) {
    return request({
      url: '/api/mes/processes/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建工序
   * @param {CreateProcessParams} data - 创建参数
   * @returns {Promise<Object>} 返回创建结果的Promise
   * @example
   * processApi.createProcess({
   *   code: 'PROC001',
   *   name: '焊接工序',
   *   description: '产品焊接工序'
   * })
   *   .then(res => console.log(res.data))
   */
  createProcess(data) {
    return request({
      url: '/api/mes/processes/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    })
  },

  /**
   * 获取工序详情
   * @param {number} id - 工序ID
   * @returns {Promise<Object>} 返回工序详情的Promise
   * @example
   * processApi.getProcessDetail(1)
   *   .then(res => console.log(res.data))
   */
  getProcessDetail(id) {
    return request({
      url: `/api/mes/processes/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新工序
   * @param {number} id - 工序ID
   * @param {UpdateProcessParams} data - 更新参数
   * @returns {Promise<Object>} 返回更新结果的Promise
   * @example
   * processApi.updateProcess(1, { name: '新工序名' })
   *   .then(res => console.log(res.data))
   */
  updateProcess(id, data) {
    return request({
      url: `/api/mes/processes/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    })
  },

  /**
   * 删除工序
   * @param {number} id - 工序ID
   * @returns {Promise<Object>} 返回删除结果的Promise
   * @example
   * processApi.deleteProcess(1)
   *   .then(res => console.log(res.msg))
   */
  deleteProcess(id) {
    return request({
      url: `/api/mes/processes/${id}/`,
      method: 'DELETE'
    })
  },

  /**
   * 获取工序技能需求列表
   * @param {Object} [params] - 查询参数
   * @param {number} [params.process] - 工序ID过滤
   * @param {number} [params.skill] - 技能ID过滤
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<Object>} 返回工序技能需求列表的Promise
   * @example
   * processApi.getProcessSkillList({ process: 1 })
   *   .then(res => console.log(res.data))
   */
  getProcessSkillList(params = {}) {
    return request({
      url: '/api/mes/processes/skills/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建工序技能需求关联
   * @param {CreateProcessSkillParams} data - 创建参数
   * @returns {Promise<Object>} 返回创建结果的Promise
   * @example
   * processApi.createProcessSkill({ process: 1, skill: 2 })
   *   .then(res => console.log(res.data))
   */
  createProcessSkill(data) {
    return request({
      url: '/api/mes/processes/skills/',
      method: 'POST',
      data: {
        process: data.process,
        skill: data.skill
      }
    })
  },

  /**
   * 删除工序技能需求关联
   * @param {number} id - 工序技能需求关联ID
   * @returns {Promise<Object>} 返回删除结果的Promise
   * @example
   * processApi.deleteProcessSkill(1)
   *   .then(res => console.log(res.msg))
   */
  deleteProcessSkill(id) {
    return request({
      url: `/api/mes/processes/skills/${id}/`,
      method: 'DELETE'
    })
  }
}

export default processApi
