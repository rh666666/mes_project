/**
 * 物料管理相关 API 模块
 * @module api/material
 */

import request, { type MesApiEnvelope } from './request'

/** 物料类型：原材料 / 产成品（与后端布尔字段对应） */
export const MaterialType = {
  RAW: false,
  PRODUCTION: true
} as const

/** 类型中文标签（键为布尔序列化后的字符串，与列表展示用法一致） */
export const MaterialTypeLabel: { false: string; true: string } = {
  false: '原材料',
  true: '产成品'
}

/** 类型展示色 */
export const MaterialTypeColor: { false: string; true: string } = {
  false: '#969799',
  true: '#07c160'
}

/** 物料资源 */
export interface Material {
  id: number
  code: string
  name: string
  description?: string
  unit_id?: number
  unit_name?: string
  is_production: boolean
  creator: number | null
  modifier: number | null
  create_datetime: string | null
  update_datetime: string | null
}

/** 创建物料 */
export interface CreateMaterialParams {
  code: string
  name: string
  description?: string
  unit_id?: number
  is_production?: boolean
}

/** 更新物料 */
export interface UpdateMaterialParams {
  code?: string
  name?: string
  description?: string
  unit_id?: number
  is_production?: boolean
}

/** 列表查询 */
export interface MaterialListQuery {
  name?: string
  code?: string
  page?: number
  limit?: number
}

/**
 * 物料管理 API
 */
const materialApi = {
  /**
   * 物料分页列表
   * @param params - 筛选与分页
   */
  getMaterialList(params: MaterialListQuery = {}): Promise<MesApiEnvelope<Material[]>> {
    return request({
      url: '/api/mes/materials/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<Material[]>>
  },

  /**
   * 创建物料
   * @param data - 编码、名称、单位等
   */
  createMaterial(data: CreateMaterialParams): Promise<MesApiEnvelope<Material>> {
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
    }) as Promise<MesApiEnvelope<Material>>
  },

  /**
   * 物料详情
   * @param id - 物料 ID
   */
  getMaterialDetail(id: number): Promise<MesApiEnvelope<Material>> {
    return request({
      url: `/api/mes/materials/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<Material>>
  },

  /**
   * 更新物料
   * @param id - 物料 ID
   * @param data - 可部分字段
   */
  updateMaterial(id: number, data: UpdateMaterialParams): Promise<MesApiEnvelope<Material>> {
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
    }) as Promise<MesApiEnvelope<Material>>
  },

  /**
   * 删除物料
   * @param id - 物料 ID
   */
  deleteMaterial(id: number): Promise<MesApiEnvelope<Material>> {
    return request({
      url: `/api/mes/materials/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<Material>>
  }
}

export default materialApi
