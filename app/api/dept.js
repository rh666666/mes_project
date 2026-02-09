/**
 * 部门管理相关API模块
 * @module api/dept
 */

import request from './request.js'

/**
 * 部门信息
 * @typedef {Object} Dept
 * @property {number} id - 部门ID
 * @property {string} code - 部门编码
 * @property {string} name - 部门名称
 * @property {string|null} description - 部门描述
 * @property {number|null} parent - 父级部门ID
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 * @property {number|null} dept - 数据归属部门
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 */

/**
 * 创建部门请求参数
 * @typedef {Object} CreateDeptParams
 * @property {string} code - 部门编码（必填）
 * @property {string} name - 部门名称（必填）
 * @property {number|null} [parent] - 父级部门ID（可选）
 * @property {string|null} [description] - 部门描述（可选）
 */

/**
 * 更新部门请求参数
 * @typedef {Object} UpdateDeptParams
 * @property {string} [code] - 部门编码
 * @property {string} [name] - 部门名称
 * @property {number|null} [parent] - 父级部门ID
 * @property {string|null} [description] - 部门描述
 */

/**
 * 部门列表响应
 * @typedef {Object} DeptListResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {number} page - 当前页码
 * @property {number} limit - 每页数量
 * @property {number} total - 总数量
 * @property {Dept[]} data - 部门列表
 */

/**
 * 部门详情响应
 * @typedef {Object} DeptDetailResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {Dept} data - 部门详细信息
 */

/**
 * 部门管理API对象
 * @namespace
 */
const deptApi = {
  /**
   * 获取部门列表
   * @param {Object} [params] - 查询参数
   * @param {string} [params.name] - 部门名称过滤
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<DeptListResponse>} 返回部门列表的Promise
   * @example
   * deptApi.getDeptList()
   *   .then(res => console.log(res.data))
   * @example
   * deptApi.getDeptList({ name: '研发' })
   *   .then(res => console.log(res.data))
   */
  getDeptList(params = {}) {
    return request({
      url: '/api/auth/depts/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建部门
   * @param {CreateDeptParams} data - 创建参数
   * @returns {Promise<DeptDetailResponse>} 返回创建结果的Promise
   * @example
   * deptApi.createDept({ code: 'DEV', name: '研发部', description: '技术研发部门' })
   *   .then(res => console.log(res.data))
   */
  createDept(data) {
    return request({
      url: '/api/auth/depts/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        parent: data.parent || null,
        description: data.description || null
      }
    })
  },

  /**
   * 获取部门详情
   * @param {number} id - 部门ID
   * @returns {Promise<DeptDetailResponse>} 返回部门详情的Promise
   * @example
   * deptApi.getDeptDetail(1)
   *   .then(res => console.log(res.data))
   */
  getDeptDetail(id) {
    return request({
      url: `/api/auth/depts/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新部门
   * @param {number} id - 部门ID
   * @param {UpdateDeptParams} data - 更新参数
   * @returns {Promise<DeptDetailResponse>} 返回更新结果的Promise
   * @example
   * deptApi.updateDept(1, { name: '新研发部', description: '更新后的描述' })
   *   .then(res => console.log(res.data))
   */
  updateDept(id, data) {
    return request({
      url: `/api/auth/depts/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        parent: data.parent !== undefined ? data.parent : null,
        description: data.description !== undefined ? data.description : null
      }
    })
  },

  /**
   * 删除部门
   * @param {number} id - 部门ID
   * @returns {Promise<DeptDetailResponse>} 返回删除结果的Promise
   * @example
   * deptApi.deleteDept(1)
   *   .then(res => console.log(res.msg))
   */
  deleteDept(id) {
    return request({
      url: `/api/auth/depts/${id}/`,
      method: 'DELETE'
    })
  }
}

export default deptApi