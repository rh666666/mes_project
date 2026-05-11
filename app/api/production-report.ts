/**
 * 生产报工 API 模块
 * @module api/production-report
 *
 * 新建报工亦可使用 `dispatch-order` 的 `reportDispatchOrder`。
 */

import request, { type MesApiEnvelope } from './request'

/** 列表查询参数（ProductionReportListRequestSerializer） */
export interface ProductionReportListParams {
  page?: number
  limit?: number
  dispatch_order?: number
}

/** 生产报工资源（ProductionReportSerializer） */
export interface ProductionReport {
  id: number
  code: string
  dispatch_order: number | null
  dispatch_order_code?: string
  process_name?: string
  quantity: number
  work_time?: string | null
  report_date?: string | null
  create_datetime?: string | null
}

/**
 * 生产报工 API
 */
const productionReportApi = {
  /**
   * 生产报工分页列表
   * @param params - 筛选与分页
   */
  getProductionReportList(
    params: ProductionReportListParams = {}
  ): Promise<MesApiEnvelope<ProductionReport[]>> {
    return request({
      url: '/api/mes/production-reports/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<ProductionReport[]>>
  },

  /**
   * 生产报工详情
   * @param id - 报工记录 ID
   */
  getProductionReportDetail(id: number): Promise<MesApiEnvelope<ProductionReport>> {
    return request({
      url: `/api/mes/production-reports/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<ProductionReport>>
  }
}

export default productionReportApi
