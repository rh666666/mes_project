/**
 * 物料清单（BOM）管理相关 API 模块
 * @module api/bom
 *
 * API 文档参考：
 * - 物料清单接口：/paths/_api_mes_boms_.json
 * - 物料清单详情接口：/paths/_api_mes_boms_details_.json
 * - 模型定义：/components/schemas/BillOfMaterial.json
 * - 模型定义：/components/schemas/BOMDetail.json
 */
import request from './request.js'

/**
 * 物料清单信息
 * @typedef {Object} BillOfMaterial
 * @property {number} id - BOM ID
 * @property {number|null} material - 物料 ID
 * @property {string} material_code - 物料编码
 * @property {string} material_name - 物料名称
 * @property {string} version - 版本
 * @property {boolean} is_active - 是否启用
 * @property {string|null} description - 描述
 * @property {number} details_count - 详情数量
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 */

/**
 * 物料清单详情信息
 * @typedef {Object} BomDetail
 * @property {number} id - 详情 ID
 * @property {number|null} bom - BOM ID
 * @property {string} bom_code - BOM 编码
 * @property {number|null} material - 子物料 ID
 * @property {string} material_code - 子物料编码
 * @property {string} material_name - 子物料名称
 * @property {number|null} sub_bom - 子 BOM ID
 * @property {number} quantity - 数量
 * @property {string|null} create_datetime - 创建时间
 */

/**
 * 获取 BOM 列表查询参数
 * @typedef {Object} GetBomListParams
 * @property {number} [page] - 页码
 * @property {number} [limit] - 每页数量
 * @property {number} [material] - 按物料 ID 过滤
 * @property {string} [version] - 按版本过滤
 */

/**
 * 创建 BOM 参数
 * @typedef {Object} CreateBomParams
 * @property {number} material - 物料 ID（必填）
 * @property {string} version - 版本（必填）
 * @property {boolean} [is_active=true] - 是否启用
 * @property {string} [description] - 描述
 */

/**
 * 更新 BOM 参数
 * @typedef {Object} UpdateBomParams
 * @property {number} [material] - 物料 ID
 * @property {string} [version] - 版本
 * @property {boolean} [is_active] - 是否启用
 * @property {string} [description] - 描述
 */

/**
 * 获取 BOM 详情列表查询参数
 * @typedef {Object} GetBomDetailListParams
 * @property {number} [page] - 页码
 * @property {number} [limit] - 每页数量
 * @property {number} [bom] - 按 BOM ID 过滤
 * @property {number} [material] - 按物料 ID 过滤
 */

/**
 * 创建 BOM 详情参数
 * @typedef {Object} CreateBomDetailParams
 * @property {number} bom - BOM ID（必填）
 * @property {number} material - 物料 ID（必填）
 * @property {number} quantity - 数量（必填，>=1）
 * @property {number} [sub_bom] - 子 BOM ID
 */

/**
 * BOM 管理 API
 * @namespace
 */
const bomApi = {
  /**
   * 获取 BOM 列表
   * @param {GetBomListParams} [params={}] - 查询参数
   * @returns {Promise<Object>} 返回 BOM 列表结果
   */
  getBomList(params = {}) {
    return request({
      url: '/api/mes/boms/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建 BOM
   * @param {CreateBomParams} data - 创建参数
   * @returns {Promise<Object>} 返回创建结果
   */
  createBom(data) {
    return request({
      url: '/api/mes/boms/',
      method: 'POST',
      data: {
        material: data.material,
        version: data.version,
        is_active: data.is_active,
        description: data.description
      }
    })
  },

  /**
   * 获取 BOM 详情
   * @param {number|string} id - BOM ID
   * @returns {Promise<Object>} 返回详情结果
   */
  getBomDetail(id) {
    return request({
      url: `/api/mes/boms/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新 BOM
   * @param {number|string} id - BOM ID
   * @param {UpdateBomParams} data - 更新参数
   * @returns {Promise<Object>} 返回更新结果
   */
  updateBom(id, data) {
    return request({
      url: `/api/mes/boms/${id}/`,
      method: 'PUT',
      data: {
        material: data.material,
        version: data.version,
        is_active: data.is_active,
        description: data.description
      }
    })
  },

  /**
   * 删除 BOM
   * @param {number|string} id - BOM ID
   * @returns {Promise<Object>} 返回删除结果
   */
  deleteBom(id) {
    return request({
      url: `/api/mes/boms/${id}/`,
      method: 'DELETE'
    })
  },

  /**
   * 获取 BOM 详情列表
   * @param {GetBomDetailListParams} [params={}] - 查询参数
   * @returns {Promise<Object>} 返回详情列表结果
   */
  getBomDetailList(params = {}) {
    return request({
      url: '/api/mes/boms/details/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建 BOM 详情
   * @param {CreateBomDetailParams} data - 创建参数
   * @returns {Promise<Object>} 返回创建结果
   */
  createBomDetail(data) {
    return request({
      url: '/api/mes/boms/details/',
      method: 'POST',
      data: {
        bom: data.bom,
        material: data.material,
        sub_bom: data.sub_bom,
        quantity: data.quantity
      }
    })
  },

  /**
   * 删除 BOM 详情
   * @param {number|string} id - 详情 ID
   * @returns {Promise<Object>} 返回删除结果
   */
  deleteBomDetail(id) {
    return request({
      url: `/api/mes/boms/details/${id}/`,
      method: 'DELETE'
    })
  }
}

export default bomApi
