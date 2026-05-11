/**
 * 生产任务单管理相关 API 模块
 * @module api/production-order
 */

import request, { type MesApiEnvelope } from './request'

/** 列表查询 */
export interface ProductionOrderListParams {
  page?: number
  limit?: number
  product?: number
  status?: string
}

/** 创建生产任务单 */
export interface CreateProductionOrderParams {
  product: number
  quantity: number
  process_route: number
  description?: string
}

/** 更新生产任务单（字段均可选） */
export interface UpdateProductionOrderParams {
  product?: number
  quantity?: number
  process_route?: number
  description?: string
}

/**
 * 生产任务单 API
 */
const productionOrderApi = {
  /**
   * 生产任务单分页列表
   * @param params - 筛选与分页
   */
  getProductionOrderList(
    params: ProductionOrderListParams = {}
  ): Promise<MesApiEnvelope<unknown[]>> {
    return request({
      url: '/api/mes/production-orders/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<unknown[]>>
  },

  /**
   * 生产任务单详情
   * @param id - 任务单 ID
   */
  getProductionOrderDetail(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/production-orders/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 创建生产任务单
   * @param data - 产品、数量、工艺路线等
   */
  createProductionOrder(data: CreateProductionOrderParams): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: '/api/mes/production-orders/',
      method: 'POST',
      data: {
        product: data.product,
        quantity: data.quantity,
        process_route: data.process_route,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 更新生产任务单（仅未下发等后端允许的状态）
   * @param id - 任务单 ID
   * @param data - 可部分字段
   */
  updateProductionOrder(
    id: number,
    data: UpdateProductionOrderParams
  ): Promise<MesApiEnvelope<unknown>> {
    const payload: Record<string, unknown> = {}
    if (data.product !== undefined) payload.product = data.product
    if (data.quantity !== undefined) payload.quantity = data.quantity
    if (data.process_route !== undefined) payload.process_route = data.process_route
    if (data.description !== undefined) payload.description = data.description
    return request({
      url: `/api/mes/production-orders/${id}/`,
      method: 'PUT',
      data: payload
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 删除生产任务单
   * @param id - 任务单 ID
   */
  deleteProductionOrder(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/production-orders/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 下发生产任务单
   * @param id - 任务单 ID
   */
  publishProductionOrder(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/production-orders/${id}/publish/`,
      method: 'POST',
      data: {}
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 取消生产任务单
   * @param id - 任务单 ID
   */
  cancelProductionOrder(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/production-orders/${id}/cancel/`,
      method: 'POST',
      data: {}
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 原材料需求
   * @param id - 任务单 ID
   */
  getMaterialRequirements(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/production-orders/${id}/material_requirements/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<unknown>>
  }
}

export default productionOrderApi
