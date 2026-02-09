/**
 * 设备管理相关API模块
 * @module api/device
 */

import request from './request.js'

/**
 * 设备状态枚举
 * @readonly
 * @enum {string}
 */
export const DeviceStatus = {
  /** 空闲中 */
  IDLE: 'idle',
  /** 运行中 */
  RUNNING: 'running',
  /** 故障 */
  ERROR: 'error'
}

/**
 * 设备状态标签映射
 * @readonly
 * @type {Object.<string, string>}
 */
export const DeviceStatusLabel = {
  [DeviceStatus.IDLE]: '空闲中',
  [DeviceStatus.RUNNING]: '运行中',
  [DeviceStatus.ERROR]: '故障'
}

/**
 * 设备信息
 * @typedef {Object} Device
 * @property {number} id - 设备ID
 * @property {string} code - 设备编码
 * @property {string} name - 设备名称
 * @property {string} status - 设备状态 (idle/running/error)，只读
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 */

/**
 * 创建设备请求参数
 * @typedef {Object} CreateDeviceParams
 * @property {string} code - 设备编码（必填，唯一）
 * @property {string} name - 设备名称（必填）
 */

/**
 * 更新设备请求参数
 * @typedef {Object} UpdateDeviceParams
 * @property {string} [code] - 设备编码
 * @property {string} [name] - 设备名称
 */

/**
 * 设备列表响应
 * @typedef {Object} DeviceListResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {number} page - 当前页码
 * @property {number} limit - 每页数量
 * @property {number} total - 总数量
 * @property {Device[]} data - 设备列表
 */

/**
 * 设备详情响应
 * @typedef {Object} DeviceDetailResponse
 * @property {number} code - 响应码
 * @property {string} msg - 响应消息
 * @property {Device} data - 设备详细信息
 */

/**
 * 设备管理API对象
 * @namespace
 */
const deviceApi = {
  /**
   * 获取设备列表
   * @param {Object} [params] - 查询参数
   * @param {string} [params.name] - 设备名称过滤
   * @param {string} [params.status] - 设备状态过滤 (idle/running/error)
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @returns {Promise<DeviceListResponse>} 返回设备列表的Promise
   * @example
   * deviceApi.getDeviceList()
   *   .then(res => console.log(res.data))
   * @example
   * deviceApi.getDeviceList({ name: 'CNC', status: 'running' })
   *   .then(res => console.log(res.data))
   */
  getDeviceList(params = {}) {
    return request({
      url: '/api/mes/devices/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建设备
   * @param {CreateDeviceParams} data - 创建参数
   * @returns {Promise<DeviceDetailResponse>} 返回创建结果的Promise
   * @example
   * deviceApi.createDevice({ code: 'CNC-001', name: '数控机床' })
   *   .then(res => console.log(res.data))
   */
  createDevice(data) {
    return request({
      url: '/api/mes/devices/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name
      }
    })
  },

  /**
   * 获取设备详情
   * @param {number} id - 设备ID
   * @returns {Promise<DeviceDetailResponse>} 返回设备详情的Promise
   * @example
   * deviceApi.getDeviceDetail(1)
   *   .then(res => console.log(res.data))
   */
  getDeviceDetail(id) {
    return request({
      url: `/api/mes/devices/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新设备
   * @param {number} id - 设备ID
   * @param {UpdateDeviceParams} data - 更新参数
   * @returns {Promise<DeviceDetailResponse>} 返回更新结果的Promise
   * @example
   * deviceApi.updateDevice(1, { name: '新设备名' })
   *   .then(res => console.log(res.data))
   */
  updateDevice(id, data) {
    return request({
      url: `/api/mes/devices/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name
      }
    })
  },

  /**
   * 删除设备
   * @param {number} id - 设备ID
   * @returns {Promise<DeviceDetailResponse>} 返回删除结果的Promise
   * @example
   * deviceApi.deleteDevice(1)
   *   .then(res => console.log(res.msg))
   */
  deleteDevice(id) {
    return request({
      url: `/api/mes/devices/${id}/`,
      method: 'DELETE'
    })
  }
}

export default deviceApi
