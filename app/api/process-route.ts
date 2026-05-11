/**
 * 工艺路线管理相关 API 模块
 * @module api/process-route
 */

import request, { type MesApiEnvelope } from './request'

/** 工艺路线资源 */
export interface ProcessRoute {
  id: number
  material: number
  material_code: string
  material_name: string
  version: string
  description: string | null
  create_datetime: string | null
  update_datetime: string | null
  creator: number | null
  modifier: number | null
}

/** 创建工艺路线 */
export interface CreateProcessRouteParams {
  material: number
  version: string
  description?: string
}

/** 更新工艺路线 */
export interface UpdateProcessRouteParams {
  version?: string
  description?: string
}

/** 工艺路线图节点（列表或详情返回） */
export interface ProcessRouteGraphNode {
  id: number
  node_key: string
  process_route: number
  process: number
  process_code: string
  process_name: string
  process_bom: number | null
}

/** 工艺路线图边 */
export interface ProcessRouteGraphEdge {
  id: number
  process_route: number
  from_node_key: string
  to_node_key: string
  priority: number
}

/** 保存图时的节点输入 */
export interface ProcessRouteGraphNodeInput {
  node_key: string
  process: number
  process_bom: number | null
}

/** 保存图时的边输入 */
export interface ProcessRouteGraphEdgeInput {
  from_node_key: string
  to_node_key: string
  priority?: number
}

/** 整图保存请求体 */
export interface SaveProcessRouteGraphParams {
  process_route: number
  nodes: ProcessRouteGraphNodeInput[]
  edges: ProcessRouteGraphEdgeInput[]
}

/**
 * 工艺路线管理 API
 */
const processRouteApi = {
  /**
   * 工艺路线分页列表
   * @param params - material 等筛选与分页
   */
  getProcessRouteList(params: Record<string, unknown> = {}): Promise<MesApiEnvelope<ProcessRoute[]>> {
    return request({
      url: '/api/mes/process-routes/',
      method: 'GET',
      data: params
    }) as Promise<MesApiEnvelope<ProcessRoute[]>>
  },

  /**
   * 创建工艺路线
   * @param data - 物料、版本等
   */
  createProcessRoute(data: CreateProcessRouteParams): Promise<MesApiEnvelope<ProcessRoute>> {
    return request({
      url: '/api/mes/process-routes/',
      method: 'POST',
      data: {
        material: data.material,
        version: data.version,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<ProcessRoute>>
  },

  /**
   * 工艺路线详情
   * @param id - 工艺路线 ID
   */
  getProcessRouteDetail(id: number): Promise<MesApiEnvelope<ProcessRoute>> {
    return request({
      url: `/api/mes/process-routes/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<ProcessRoute>>
  },

  /**
   * 更新工艺路线
   * @param id - 工艺路线 ID
   * @param data - 可部分字段
   */
  updateProcessRoute(
    id: number,
    data: UpdateProcessRouteParams
  ): Promise<MesApiEnvelope<ProcessRoute>> {
    return request({
      url: `/api/mes/process-routes/${id}/`,
      method: 'PUT',
      data: {
        version: data.version,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<ProcessRoute>>
  },

  /**
   * 删除工艺路线
   * @param id - 工艺路线 ID
   */
  deleteProcessRoute(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/process-routes/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 获取工艺路线图（节点与边）
   * @param processRouteId - 工艺路线 ID
   */
  getProcessRouteGraph(processRouteId: number): Promise<
    MesApiEnvelope<{ nodes: ProcessRouteGraphNode[]; edges: ProcessRouteGraphEdge[] }>
  > {
    return request({
      url: '/api/mes/process-routes/details/',
      method: 'GET',
      data: {
        process_route: processRouteId
      }
    }) as Promise<
      MesApiEnvelope<{ nodes: ProcessRouteGraphNode[]; edges: ProcessRouteGraphEdge[] }>
    >
  },

  /**
   * 保存工艺路线图（整图覆盖）
   * @param data - 路线 ID、节点与边列表
   */
  saveProcessRouteGraph(data: SaveProcessRouteGraphParams): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: '/api/mes/process-routes/details/',
      method: 'POST',
      data: {
        process_route: data.process_route,
        nodes: data.nodes,
        edges: data.edges
      }
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 删除工艺路线图节点（兼容旧接口）
   * @param id - 节点 ID
   */
  deleteProcessRouteGraphNode(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/process-routes/details/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  }
}

export default processRouteApi
