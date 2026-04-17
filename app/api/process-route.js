/**
 * 工艺路线管理相关API模块
 * @module api/process-route
 *
 * 开发说明：
 * 1. 根据后端API文档中的Schema定义类型
 * 2. 每个接口函数必须添加JSDoc注释
 * 3. 请求参数和响应数据与API文档保持一致
 *
 * API文档参考：
 * - 工艺路线接口：/paths/_api_mes_process-routes_.json
 * - 工艺路线详情接口：/paths/_api_mes_process-routes_details_.json
 * - 模型定义：/components/schemas/ProcessRoute.json
 * - 模型定义：/components/schemas/ProcessRouteDetail.json
 */

import request from './request.js'

/**
 * 工艺路线信息
 * @typedef {Object} ProcessRoute
 * @property {number} id - 工艺路线ID
 * @property {number} material - 物料ID
 * @property {string} material_code - 物料编码
 * @property {string} material_name - 物料名称
 * @property {string} version - 版本
 * @property {string|null} description - 描述
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 *
 * 参考：/components/schemas/ProcessRoute.json
 */

/**
 * 创建工艺路线请求参数
 * @typedef {Object} CreateProcessRouteParams
 * @property {number} material - 物料ID（必填）
 * @property {string} version - 版本（必填，最大长度50）
 * @property {string} [description] - 描述（可选，最大长度255）
 *
 * 参考：/components/schemas/ProcessRouteCreateRequestRequest.json
 */

/**
 * 更新工艺路线请求参数
 * @typedef {Object} UpdateProcessRouteParams
 * @property {string} [version] - 版本（最大长度50）
 * @property {string} [description] - 描述（最大长度255）
 *
 * 参考：/components/schemas/ProcessRouteUpdateRequestRequest.json
 */

/**
 * 工艺路线图节点
 * @typedef {Object} ProcessRouteGraphNode
 * @property {number} id - 节点ID
 * @property {string} node_key - 节点唯一键
 * @property {number} process_route - 工艺路线ID
 * @property {number} process - 工序ID
 * @property {string} process_code - 工序编码
 * @property {string} process_name - 工序名称
 * @property {number|null} process_bom - 工序BOM ID
 */

/**
 * 工艺路线图边
 * @typedef {Object} ProcessRouteGraphEdge
 * @property {number} id - 边ID
 * @property {number} process_route - 工艺路线ID
 * @property {string} from_node_key - 起始节点键
 * @property {string} to_node_key - 目标节点键
 * @property {number} priority - 优先级
 */

/**
 * 保存工艺路线图请求参数
 * @typedef {Object} SaveProcessRouteGraphParams
 * @property {number} process_route - 工艺路线ID
 * @property {Array<{node_key:string, process:number, process_bom:number|null}>} nodes - 节点列表
 * @property {Array<{from_node_key:string, to_node_key:string, priority?:number}>} edges - 边列表
 */

/**
 * 工艺路线管理API对象
 * @namespace
 */
const processRouteApi = {
  /**
   * 获取工艺路线列表
   * @param {Object} [params] - 查询参数
   * @param {number} [params.page] - 页码
   * @param {number} [params.limit] - 每页数量
   * @param {number} [params.material] - 物料ID过滤
   * @returns {Promise<Object>} 返回工艺路线列表的Promise
   *
   * 接口信息：
   * - 路径：/api/mes/process-routes/
   * - 方法：GET
   * - 参考：/paths/_api_mes_process-routes_.json
   *
   * @example
   * processRouteApi.getProcessRouteList()
   *   .then(res => console.log(res.data))
   * @example
   * processRouteApi.getProcessRouteList({ material: 1, page: 1, limit: 10 })
   *   .then(res => console.log(res.data))
   */
  getProcessRouteList(params = {}) {
    return request({
      url: '/api/mes/process-routes/',
      method: 'GET',
      data: params
    })
  },

  /**
   * 创建工艺路线
   * @param {CreateProcessRouteParams} data - 创建参数
   * @returns {Promise<Object>} 返回创建结果的Promise
   *
   * 接口信息：
   * - 路径：/api/mes/process-routes/
   * - 方法：POST
   * - 参考：/paths/_api_mes_process-routes_.json
   *
   * @example
   * processRouteApi.createProcessRoute({
   *   material: 1,
   *   version: 'V1.0',
   *   description: '标准工艺路线'
   * })
   *   .then(res => console.log(res.data))
   */
  createProcessRoute(data) {
    return request({
      url: '/api/mes/process-routes/',
      method: 'POST',
      data: {
        material: data.material,
        version: data.version,
        description: data.description
      }
    })
  },

  /**
   * 获取工艺路线详情
   * @param {number} id - 工艺路线ID
   * @returns {Promise<Object>} 返回工艺路线详情的Promise
   *
   * 接口信息：
   * - 路径：/api/mes/process-routes/{id}/
   * - 方法：GET
   * - 参考：/paths/_api_mes_process-routes_%7Bid%7D_.json
   *
   * @example
   * processRouteApi.getProcessRouteDetail(1)
   *   .then(res => console.log(res.data))
   */
  getProcessRouteDetail(id) {
    return request({
      url: `/api/mes/process-routes/${id}/`,
      method: 'GET'
    })
  },

  /**
   * 更新工艺路线
   * @param {number} id - 工艺路线ID
   * @param {UpdateProcessRouteParams} data - 更新参数
   * @returns {Promise<Object>} 返回更新结果的Promise
   *
   * 接口信息：
   * - 路径：/api/mes/process-routes/{id}/
   * - 方法：PUT
   * - 参考：/paths/_api_mes_process-routes_%7Bid%7D_.json
   *
   * @example
   * processRouteApi.updateProcessRoute(1, { version: 'V2.0', description: '更新描述' })
   *   .then(res => console.log(res.data))
   */
  updateProcessRoute(id, data) {
    return request({
      url: `/api/mes/process-routes/${id}/`,
      method: 'PUT',
      data: {
        version: data.version,
        description: data.description
      }
    })
  },

  /**
   * 删除工艺路线
   * @param {number} id - 工艺路线ID
   * @returns {Promise<Object>} 返回删除结果的Promise
   *
   * 接口信息：
   * - 路径：/api/mes/process-routes/{id}/
   * - 方法：DELETE
   * - 参考：/paths/_api_mes_process-routes_%7Bid%7D_.json
   *
   * @example
   * processRouteApi.deleteProcessRoute(1)
   *   .then(res => console.log(res.msg))
   */
  deleteProcessRoute(id) {
    return request({
      url: `/api/mes/process-routes/${id}/`,
      method: 'DELETE'
    })
  },

  /**
   * 获取工艺路线图
   * @param {number} processRouteId - 工艺路线ID
   * @returns {Promise<Object>} 返回图结构数据 Promise
   */
  getProcessRouteGraph(processRouteId) {
    return request({
      url: '/api/mes/process-routes/details/',
      method: 'GET',
      data: {
        process_route: processRouteId
      }
    })
  },

  /**
   * 保存工艺路线图（整图覆盖）
   * @param {SaveProcessRouteGraphParams} data - 保存参数
   * @returns {Promise<Object>} 返回保存结果 Promise
   */
  saveProcessRouteGraph(data) {
    return request({
      url: '/api/mes/process-routes/details/',
      method: 'POST',
      data: {
        process_route: data.process_route,
        nodes: data.nodes,
        edges: data.edges
      }
    })
  },

  /**
   * 删除工艺路线图节点（兼容旧接口）
   * @param {number} id - 节点ID
   * @returns {Promise<Object>} 返回删除结果的Promise
   */
  deleteProcessRouteGraphNode(id) {
    return request({
      url: `/api/mes/process-routes/details/${id}/`,
      method: 'DELETE'
    })
  }
}

export default processRouteApi
