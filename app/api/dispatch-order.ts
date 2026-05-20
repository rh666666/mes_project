/**
 * 工序派工单 API 模块
 * @module api/dispatch-order
 *
 * OpenAPI：`/api/mes/dispatch-orders/`。权限与后端一致。
 */

import request, { type MesApiEnvelope } from './request'

/** 工序派工单状态（DispatchOrder.Status） */
export type DispatchOrderStatus =
  | 'pending'
  | 'dispatched'
  | 'grabbed'
  | 'in_progress'
  | 'paused'
  | 'waiting_previous'
  | 'cancelled'
  | 'completed'
  | 'obsolete'

/** 列表查询参数（DispatchOrderListRequestSerializer） */
export interface DispatchOrderListParams {
  page?: number
  limit?: number
  production_order?: number
  process?: number
  status?: DispatchOrderStatus | string
  /** 为 true 时仅返回当前用户接单的工单（管理员亦生效） */
  mine?: boolean
}

/** 管理员派工请求体 POST .../dispatch/ */
export interface DispatchOrderDispatchBody {
  operator?: number
  device?: number
}

/** 员工抢单请求体 POST .../grab/ */
export interface DispatchOrderGrabBody {
  /** 抢单数量；不传则抢剩余可生产数量 */
  quantity?: number
}

/** 拆分请求体 POST .../split/ */
export interface DispatchOrderSplitBody {
  split_quantity: number
}

/** 工序派工单资源（DispatchOrderSerializer） */
export interface DispatchOrder {
  id: number
  code: string
  production_order: number | null
  production_order_code?: string
  process: number | null
  process_code?: string
  process_name?: string
  sequence: number
  operator: number | null
  operator_name?: string
  device: number | null
  device_code?: string
  quantity: number
  completed_quantity: number
  status: DispatchOrderStatus
  status_display?: string
  is_reachable?: boolean
  parent: number | null
  parent_code?: string
  is_parent: boolean
  is_child: boolean
  children_count?: number
  create_datetime?: string | null
  update_datetime?: string | null
}

/** 拆分成功时 DetailResponse.data */
export interface DispatchOrderSplitResultData {
  parent_order: DispatchOrder
  child_order: DispatchOrder
}

/** 派工单上报工请求体（ProductionReportCreateRequestSerializer，POST .../report/） */
export interface DispatchOrderReportBody {
  dispatch_order_id: number
  quantity: number
  /** Django Duration，常用 HH:MM:SS 字符串 */
  work_time: string
}

/**
 * 工序派工单 API
 */
const dispatchOrderApi = {
  /**
   * 工序派工单分页列表
   * @param params - 筛选与分页
   */
  getDispatchOrderList(
    params: DispatchOrderListParams = {}
  ): Promise<MesApiEnvelope<DispatchOrder[]>> {
    return request({
      url: '/api/mes/dispatch-orders/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<DispatchOrder[]>>
  },

  /**
   * 工序派工单详情
   * @param id - 派工单 ID
   */
  getDispatchOrderDetail(id: number): Promise<MesApiEnvelope<DispatchOrder>> {
    return request({
      url: `/api/mes/dispatch-orders/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<DispatchOrder>>
  },

  /**
   * 管理员派工（仅待抢单等后端允许的状态）
   * @param id - 派工单 ID
   * @param data - 操作员与设备
   */
  dispatchDispatchOrder(
    id: number,
    data: DispatchOrderDispatchBody = {}
  ): Promise<MesApiEnvelope<DispatchOrder>> {
    const payload: Record<string, unknown> = {}
    if (data.operator !== undefined && data.operator !== null) {
      payload.operator = data.operator
    }
    if (data.device !== undefined && data.device !== null) {
      payload.device = data.device
    }
    return request({
      url: `/api/mes/dispatch-orders/${id}/dispatch/`,
      method: 'POST',
      data: payload
    }) as Promise<MesApiEnvelope<DispatchOrder>>
  },

  /**
   * 员工抢单
   * @param id - 派工单 ID
   * @param data - 可选抢单数量（小于剩余数量时后端拆分子工单）
   */
  grabDispatchOrder(
    id: number,
    data: DispatchOrderGrabBody = {}
  ): Promise<MesApiEnvelope<DispatchOrder>> {
    const payload: Record<string, unknown> = {}
    if (data.quantity !== undefined && data.quantity !== null) {
      payload.quantity = data.quantity
    }
    return request({
      url: `/api/mes/dispatch-orders/${id}/grab/`,
      method: 'POST',
      data: payload
    }) as Promise<MesApiEnvelope<DispatchOrder>>
  },

  /**
   * 开始生产
   * @param id - 派工单 ID
   */
  startDispatchOrder(id: number): Promise<MesApiEnvelope<DispatchOrder>> {
    return request({
      url: `/api/mes/dispatch-orders/${id}/start/`,
      method: 'POST',
      data: {}
    }) as Promise<MesApiEnvelope<DispatchOrder>>
  },

  /**
   * 暂停生产
   * @param id - 派工单 ID
   */
  pauseDispatchOrder(id: number): Promise<MesApiEnvelope<DispatchOrder>> {
    return request({
      url: `/api/mes/dispatch-orders/${id}/pause/`,
      method: 'POST',
      data: {}
    }) as Promise<MesApiEnvelope<DispatchOrder>>
  },

  /**
   * 拆分派工单（管理员）
   * @param id - 派工单 ID
   * @param data - 拆分数量
   */
  splitDispatchOrder(
    id: number,
    data: DispatchOrderSplitBody
  ): Promise<MesApiEnvelope<DispatchOrderSplitResultData>> {
    return request({
      url: `/api/mes/dispatch-orders/${id}/split/`,
      method: 'POST',
      data: {
        split_quantity: data.split_quantity
      }
    }) as Promise<MesApiEnvelope<DispatchOrderSplitResultData>>
  },

  /**
   * 生产报工（员工）
   * @param id - 派工单 ID（与 body.dispatch_order_id 一致）
   * @param data - 报工数量与工时
   */
  reportDispatchOrder(
    id: number,
    data: DispatchOrderReportBody
  ): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/dispatch-orders/${id}/report/`,
      method: 'POST',
      data: {
        dispatch_order_id: data.dispatch_order_id,
        quantity: data.quantity,
        work_time: data.work_time
      }
    }) as Promise<MesApiEnvelope<unknown>>
  }
}

export default dispatchOrderApi
