/**
 * 物料管理相关API模块
 * @module api/material
 */

import request from './request.js'

/**
 * 物料类型枚举
 * @readonly
 * @enum {boolean}
 */
export const MaterialType = {
  /** 原材料 */
  RAW: false,
  /** 产成品 */
  PRODUCTION: true
}

/**
 * 物料类型标签映射
 * @readonly
 * @type {Object.<boolean, string>}
 */
export const MaterialTypeLabel = {
  [MaterialType.RAW]: '原材料',
  [MaterialType.PRODUCTION]: '产成品'
}

/**
 * 物料类型颜色映射
 * @readonly
 * @type {Object.<boolean, string>}
 */
export const MaterialTypeColor = {
  [MaterialType.RAW]: '#969799',
  [MaterialType.PRODUCTION]: '#07c160'
}

/**
 * 物料信息
 * @typedef {Object} Material
 * @property {number} id - 物料ID
 * @property {string} code - 物料编码
 * @property {string} name - 物料名称
 * @property {string} [description] - 物料描述
 * @property {number} [unit_id] - 单位ID
 * @property {string} [unit_name] - 单位名称
 * @property {boolean} is_production - 是否为产成品
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 */

/**
 * 创建物料请求参数
 * @typedef {Object} CreateMaterialParams
 * @property {string} code - 物料编码（必填，唯一）
 * @property {string} name - 物料名称（必填）
 * @property {string} [description] - 物料描述（可选）
 * @property {number} [unit_id] - 单位ID（可选）
 * @property {boolean} [is_production] - 是否为产成品（可选，默认为false）
 */

/**
 * 更新物料请求参数
 * @typedef {Object} UpdateMaterialParams
 * @property {string} [code] - 物料编码
 * @property {string} [name] - 物料名称
 * @property {string} [description] - 物料描述
 * @property {number} [unit_id] - 单位ID
 * @property {boolean} [is_production] - 是否为产成品
 */

/**
 * 物料列表响应
 * @typedef {Object} MaterialListResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {number} page - 当前页码
 * @property {number} limit - 每页数量
 * @property {number} total - 总数量
 * @property {Material[]} data - 物料列表
 */

/**
 * 物料详情响应
 * @typedef {Object} MaterialDetailResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {Material} data - 物料详细信息
 */

/**
 * 物料管理API对象
 * @namespace
 */
const materialApi = {
  /**
   * 获取物料列表
   * @param {Object} [params] - 查询参数
   * @param {string} [params.name] - 物料名称过滤
   * @param {string} [params.code] - 物料编码过滤
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<MaterialListResponse>} 返回物料列表的Promise
   * @example
   * materialApi.getMaterialList()
   *   .then(res => console.log(res.data))
   * @example
   * materialApi.getMaterialList({ name: '螺丝', code: 'SC' })
   *   .then(res => console.log(res.data))
   */
  getMaterialList(params = {}) {
    return request({
      url: '/api/mes/materials/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建物料
   * @param {CreateMaterialParams} data - 创建参数
   * @returns {Promise<MaterialDetailResponse>} 返回创建结果的Promise
   * @example
   * materialApi.createMaterial({
   *   code: 'MAT001',
   *   name: '测试物料',
   *   description: '测试用的物料',
   *   unit_id: 1,
   *   is_production: false
   * })
   *   .then(res => console.log(res.data))
   */
  createMaterial(data) {
    return request({
      url: '/api/mes/materials/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        description: data.description,
        unit_id: data.unit_id,
        is_production: data.is_production ?? false
      }
    })
  },

  /**
   * 获取物料详情
   * @param {number} id - 物料ID
   * @returns {Promise<MaterialDetailResponse>} 返回物料详情的Promise
   * @example
   * materialApi.getMaterialDetail(1)
   *   .then(res => console.log(res.data))
   */
  getMaterialDetail(id) {
    return request({
      url: `/api/mes/materials/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新物料
   * @param {number} id - 物料ID
   * @param {UpdateMaterialParams} data - 更新参数
   * @returns {Promise<MaterialDetailResponse>} 返回更新结果的Promise
   * @example
   * materialApi.updateMaterial(1, { name: '新物料名', unit_id: 2 })
   *   .then(res => console.log(res.data))
   */
  updateMaterial(id, data) {
    return request({
      url: `/api/mes/materials/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        description: data.description,
        unit_id: data.unit_id,
        is_production: data.is_production
      }
    })
  },

  /**
   * 删除物料
   * @param {number} id - 物料ID
   * @returns {Promise<MaterialDetailResponse>} 返回删除结果的Promise
   * @example
   * materialApi.deleteMaterial(1)
   *   .then(res => console.log(res.msg))
   */
  deleteMaterial(id) {
    return request({
      url: `/api/mes/materials/${id}/`,
      method: 'DELETE'
    })
  }
}

export default materialApi
