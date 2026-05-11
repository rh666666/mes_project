/**
 * 设备管理相关 API 模块
 * @module api/device
 */

import request, { type MesApiEnvelope } from './request'

/** 设备状态 */
export type DeviceStatusValue = 'idle' | 'running' | 'error'

/** 设备状态常量 */
export const DeviceStatus = {
  IDLE: 'idle',
  RUNNING: 'running',
  ERROR: 'error'
} as const satisfies Record<string, DeviceStatusValue>

/** 状态中文标签 */
export const DeviceStatusLabel: Record<DeviceStatusValue, string> = {
  [DeviceStatus.IDLE]: '空闲中',
  [DeviceStatus.RUNNING]: '运行中',
  [DeviceStatus.ERROR]: '故障'
}

/** 设备资源 */
export interface Device {
  id: number
  code: string
  name: string
  status: DeviceStatusValue
  creator: number | null
  modifier: number | null
  create_datetime: string | null
  update_datetime: string | null
}

/** 创建设备 */
export interface CreateDeviceParams {
  code: string
  name: string
}

/** 更新设备 */
export interface UpdateDeviceParams {
  code?: string
  name?: string
}

/** 列表查询 */
export interface DeviceListQuery {
  name?: string
  status?: DeviceStatusValue
  page?: number
  limit?: number
}

/**
 * 设备管理 API
 */
const deviceApi = {
  /**
   * 设备分页列表
   * @param params - 筛选与分页
   */
  getDeviceList(params: DeviceListQuery = {}): Promise<MesApiEnvelope<Device[]>> {
    return request({
      url: '/api/mes/devices/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<Device[]>>
  },

  /**
   * 创建设备
   * @param data - 编码与名称
   */
  createDevice(data: CreateDeviceParams): Promise<MesApiEnvelope<Device>> {
    return request({
      url: '/api/mes/devices/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name
      }
    }) as Promise<MesApiEnvelope<Device>>
  },

  /**
   * 设备详情
   * @param id - 设备 ID
   */
  getDeviceDetail(id: number): Promise<MesApiEnvelope<Device>> {
    return request({
      url: `/api/mes/devices/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<Device>>
  },

  /**
   * 更新设备
   * @param id - 设备 ID
   * @param data - 可部分字段
   */
  updateDevice(id: number, data: UpdateDeviceParams): Promise<MesApiEnvelope<Device>> {
    return request({
      url: `/api/mes/devices/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name
      }
    }) as Promise<MesApiEnvelope<Device>>
  },

  /**
   * 删除设备
   * @param id - 设备 ID
   */
  deleteDevice(id: number): Promise<MesApiEnvelope<Device>> {
    return request({
      url: `/api/mes/devices/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<Device>>
  }
}

export default deviceApi
