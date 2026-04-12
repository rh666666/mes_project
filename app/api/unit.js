/**
 * 单位管理相关API模块
 * @module api/unit
 */

import request from './request.js'

/**
 * 单位信息
 * @typedef {Object} Unit
 * @property {number} id - 单位ID
 * @property {string} code - 单位编码
 * @property {string} name - 单位名称
 * @property {string} [description] - 单位描述
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 */

/**
 * 创建单位请求参数
 * @typedef {Object} CreateUnitParams
 * @property {string} code - 单位编码（必填，唯一）
 * @property {string} name - 单位名称（必填）
 * @property {string} [description] - 单位描述（可选）
 */

/**
 * 更新单位请求参数
 * @typedef {Object} UpdateUnitParams
 * @property {string} [code] - 单位编码
 * @property {string} [name] - 单位名称
 * @property {string} [description] - 单位描述
 */

/**
 * 单位列表响应
 * @typedef {Object} UnitListResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {number} page - 当前页码
 * @property {number} limit - 每页数量
 * @property {number} total - 总数量
 * @property {Unit[]} data - 单位列表
 */

/**
 * 单位详情响应
 * @typedef {Object} UnitDetailResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {Unit} data - 单位详细信息
 */

/**
 * 单位管理API对象
 * @namespace
 */
const unitApi = {
  /**
   * 获取单位列表
   * @param {Object} [params] - 查询参数
   * @param {string} [params.name] - 单位名称过滤
   * @param {string} [params.code] - 单位编码过滤
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<UnitListResponse>} 返回单位列表的Promise
   * @example
   * unitApi.getUnitList()
   *   .then(res => console.log(res.data))
   * @example
   * unitApi.getUnitList({ name: '厘米', code: 'cm' })
   *   .then(res => console.log(res.data))
   */
  getUnitList(params = {}) {
    return request({
      url: '/api/mes/units/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建单位
   * @param {CreateUnitParams} data - 创建参数
   * @returns {Promise<UnitDetailResponse>} 返回创建结果的Promise
   * @example
   * unitApi.createUnit({ code: 'cm', name: '厘米', description: '基本长度单位-厘米' })
   *   .then(res => console.log(res.data))
   */
  createUnit(data) {
    return request({
      url: '/api/mes/units/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    })
  },

  /**
   * 获取单位详情
   * @param {number} id - 单位ID
   * @returns {Promise<UnitDetailResponse>} 返回单位详情的Promise
   * @example
   * unitApi.getUnitDetail(1)
   *   .then(res => console.log(res.data))
   */
  getUnitDetail(id) {
    return request({
      url: `/api/mes/units/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新单位
   * @param {number} id - 单位ID
   * @param {UpdateUnitParams} data - 更新参数
   * @returns {Promise<UnitDetailResponse>} 返回更新结果的Promise
   * @example
   * unitApi.updateUnit(1, { name: '新单位名' })
   *   .then(res => console.log(res.data))
   */
  updateUnit(id, data) {
    return request({
      url: `/api/mes/units/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    })
  },

  /**
   * 删除单位
   * @param {number} id - 单位ID
   * @returns {Promise<UnitDetailResponse>} 返回删除结果的Promise
   * @example
   * unitApi.deleteUnit(1)
   *   .then(res => console.log(res.msg))
   */
  deleteUnit(id) {
    return request({
      url: `/api/mes/units/${id}/`,
      method: 'DELETE'
    })
  }
}

export default unitApi
