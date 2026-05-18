/**
 * 质检任务单 API 模块
 * @module api/quality-check-order
 */

import request, { type MesApiEnvelope } from './request'

/** 列表查询参数（QualityCheckOrderListRequestSerializer） */
export interface QualityCheckOrderListParams {
  page?: number
  limit?: number
  production_order?: number
  type?: string
}

/** 质检任务单资源（QualityCheckOrderSerializer） */
export interface QualityCheckOrder {
  id: number
  code: string
  type: string
  type_display?: string
  status: string
  status_display?: string
  production_order: number | null
  production_order_code?: string
  product: number | null
  product_code?: string
  product_name?: string
  quantity: number
  qualified_quantity: number
  unqualified_quantity: number
  create_datetime?: string | null
  update_datetime?: string | null
}

/** 提交质检结果请求体（QualityCheckOrderSubmitResultRequestSerializer） */
export interface QualityCheckOrderSubmitResultBody {
  qualified_quantity: number
  unqualified_quantity: number
}

/**
 * 质检任务单 API
 */
const qualityCheckOrderApi = {
  /**
   * 质检任务单分页列表
   * @param params - 筛选与分页
   */
  getQualityCheckOrderList(
    params: QualityCheckOrderListParams = {}
  ): Promise<MesApiEnvelope<QualityCheckOrder[]>> {
    return request({
      url: '/api/mes/quality-check-orders/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<QualityCheckOrder[]>>
  },

  /**
   * 质检任务单详情
   * @param id - 质检任务单 ID
   */
  getQualityCheckOrderDetail(id: number): Promise<MesApiEnvelope<QualityCheckOrder>> {
    return request({
      url: `/api/mes/quality-check-orders/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<QualityCheckOrder>>
  },

  /**
   * 提交质检结果
   * @param id - 质检任务单 ID
   * @param data - 合格品与不合格品数量
   */
  submitQualityCheckResult(
    id: number,
    data: QualityCheckOrderSubmitResultBody
  ): Promise<MesApiEnvelope<QualityCheckOrder>> {
    return request({
      url: `/api/mes/quality-check-orders/${id}/submit_result/`,
      method: 'POST',
      data
    }) as Promise<MesApiEnvelope<QualityCheckOrder>>
  }
}

export default qualityCheckOrderApi
