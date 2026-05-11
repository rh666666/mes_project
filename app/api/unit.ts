/**
 * 单位管理相关 API 模块
 * @module api/unit
 */

import request, { type MesApiEnvelope } from './request'

/** 计量单位 */
export interface Unit {
  id: number
  code: string
  name: string
  description?: string
  creator: number | null
  modifier: number | null
  create_datetime: string | null
  update_datetime: string | null
}

/** 创建单位 */
export interface CreateUnitParams {
  code: string
  name: string
  description?: string
}

/** 更新单位 */
export interface UpdateUnitParams {
  code?: string
  name?: string
  description?: string
}

/** 列表查询 */
export interface UnitListQuery {
  name?: string
  code?: string
  page?: number
  limit?: number
}

/**
 * 单位管理 API
 */
const unitApi = {
  /**
   * 获取单位分页列表
   * @param params - 筛选与分页
   */
  getUnitList(params: UnitListQuery = {}): Promise<MesApiEnvelope<Unit[]>> {
    return request({
      url: '/api/mes/units/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<Unit[]>>
  },

  /**
   * 创建单位
   * @param data - 编码与名称
   */
  createUnit(data: CreateUnitParams): Promise<MesApiEnvelope<Unit>> {
    return request({
      url: '/api/mes/units/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<Unit>>
  },

  /**
   * 单位详情
   * @param id - 单位 ID
   */
  getUnitDetail(id: number): Promise<MesApiEnvelope<Unit>> {
    return request({
      url: `/api/mes/units/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<Unit>>
  },

  /**
   * 更新单位
   * @param id - 单位 ID
   * @param data - 可部分字段
   */
  updateUnit(id: number, data: UpdateUnitParams): Promise<MesApiEnvelope<Unit>> {
    return request({
      url: `/api/mes/units/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<Unit>>
  },

  /**
   * 删除单位
   * @param id - 单位 ID
   */
  deleteUnit(id: number): Promise<MesApiEnvelope<Unit>> {
    return request({
      url: `/api/mes/units/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<Unit>>
  }
}

export default unitApi
