/**
 * 物料清单（BOM）管理相关 API 模块
 * @module api/bom
 */

import request, { type MesApiEnvelope } from './request'

/** BOM 头 */
export interface BillOfMaterial {
  id: number
  material: number | null
  material_code: string
  material_name: string
  version: string
  is_active: boolean
  description: string | null
  details_count: number
  create_datetime: string | null
  update_datetime: string | null
  creator: number | null
  modifier: number | null
}

/** BOM 明细行 */
export interface BomDetail {
  id: number
  bom: number | null
  bom_code: string
  material: number | null
  material_code: string
  material_name: string
  sub_bom: number | null
  sub_bom_version?: string | null
  quantity: number
  create_datetime: string | null
}

/** BOM 列表查询 */
export interface GetBomListParams {
  page?: number
  limit?: number
  material?: number
  version?: string
  /** 模糊搜索物料编码、名称或 BOM 版本 */
  search?: string
}

/** 创建 BOM */
export interface CreateBomParams {
  material: number
  version: string
  is_active?: boolean
  description?: string
}

/** 更新 BOM */
export interface UpdateBomParams {
  material?: number
  version?: string
  is_active?: boolean
  description?: string
}

/** BOM 明细列表查询 */
export interface GetBomDetailListParams {
  page?: number
  limit?: number
  bom?: number
  material?: number
}

/** 创建 BOM 明细 */
export interface CreateBomDetailParams {
  bom: number
  material: number
  quantity: number
  sub_bom?: number
}

/** BOM ID（接口路径兼容字符串） */
export type BomId = number | string

/**
 * BOM 管理 API
 */
const bomApi = {
  /**
   * BOM 分页列表
   * @param params - 筛选与分页
   */
  getBomList(params: GetBomListParams = {}): Promise<MesApiEnvelope<BillOfMaterial[]>> {
    return request({
      url: '/api/mes/boms/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<BillOfMaterial[]>>
  },

  /**
   * 创建 BOM
   * @param data - 物料、版本等
   */
  createBom(data: CreateBomParams): Promise<MesApiEnvelope<BillOfMaterial>> {
    return request({
      url: '/api/mes/boms/',
      method: 'POST',
      data: {
        material: data.material,
        version: data.version,
        is_active: data.is_active,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<BillOfMaterial>>
  },

  /**
   * BOM 详情
   * @param id - BOM ID
   */
  getBomDetail(id: BomId): Promise<MesApiEnvelope<BillOfMaterial>> {
    return request({
      url: `/api/mes/boms/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<BillOfMaterial>>
  },

  /**
   * 更新 BOM
   * @param id - BOM ID
   * @param data - 可部分字段
   */
  updateBom(id: BomId, data: UpdateBomParams): Promise<MesApiEnvelope<BillOfMaterial>> {
    return request({
      url: `/api/mes/boms/${id}/`,
      method: 'PUT',
      data: {
        material: data.material,
        version: data.version,
        is_active: data.is_active,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<BillOfMaterial>>
  },

  /**
   * 删除 BOM
   * @param id - BOM ID
   */
  deleteBom(id: BomId): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/boms/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * BOM 明细分页列表
   * @param params - bom/material 筛选与分页
   */
  getBomDetailList(params: GetBomDetailListParams = {}): Promise<MesApiEnvelope<BomDetail[]>> {
    return request({
      url: '/api/mes/boms/details/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<BomDetail[]>>
  },

  /**
   * 创建 BOM 明细行
   * @param data - bom、子物料、数量等
   */
  createBomDetail(data: CreateBomDetailParams): Promise<MesApiEnvelope<BomDetail>> {
    return request({
      url: '/api/mes/boms/details/',
      method: 'POST',
      data: {
        bom: data.bom,
        material: data.material,
        sub_bom: data.sub_bom,
        quantity: data.quantity
      }
    }) as Promise<MesApiEnvelope<BomDetail>>
  },

  /**
   * 删除 BOM 明细行
   * @param id - 明细 ID
   */
  deleteBomDetail(id: BomId): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/boms/details/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  }
}

export default bomApi
