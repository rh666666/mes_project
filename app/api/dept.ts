/**
 * 部门管理相关 API 模块
 * @module api/dept
 */

import request, { type MesApiEnvelope } from './request'

/** 部门资源 */
export interface Dept {
  id: number
  code: string
  name: string
  description: string | null
  parent: number | null
  creator: number | null
  modifier: number | null
  dept: number | null
  create_datetime: string | null
  update_datetime: string | null
}

/** 创建部门 */
export interface CreateDeptParams {
  code: string
  name: string
  parent?: number | null
  description?: string | null
}

/** 更新部门 */
export interface UpdateDeptParams {
  code?: string
  name?: string
  parent?: number | null
  description?: string | null
}

/** 列表查询 */
export interface DeptListQuery {
  name?: string
  page?: number
  limit?: number
}

/**
 * 部门管理 API
 */
const deptApi = {
  /**
   * 获取部门分页列表
   * @param params - 筛选与分页
   */
  getDeptList(params: DeptListQuery = {}): Promise<MesApiEnvelope<Dept[]>> {
    return request({
      url: '/api/auth/depts/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<Dept[]>>
  },

  /**
   * 创建部门
   * @param data - 编码、名称等
   */
  createDept(data: CreateDeptParams): Promise<MesApiEnvelope<Dept>> {
    return request({
      url: '/api/auth/depts/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        parent: data.parent ?? null,
        description: data.description ?? null
      }
    }) as Promise<MesApiEnvelope<Dept>>
  },

  /**
   * 部门详情
   * @param id - 部门 ID
   */
  getDeptDetail(id: number): Promise<MesApiEnvelope<Dept>> {
    return request({
      url: `/api/auth/depts/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<Dept>>
  },

  /**
   * 更新部门
   * @param id - 部门 ID
   * @param data - 可部分字段
   */
  updateDept(id: number, data: UpdateDeptParams): Promise<MesApiEnvelope<Dept>> {
    return request({
      url: `/api/auth/depts/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        parent: data.parent !== undefined ? data.parent : null,
        description: data.description !== undefined ? data.description : null
      }
    }) as Promise<MesApiEnvelope<Dept>>
  },

  /**
   * 删除部门
   * @param id - 部门 ID
   */
  deleteDept(id: number): Promise<MesApiEnvelope<Dept>> {
    return request({
      url: `/api/auth/depts/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<Dept>>
  }
}

export default deptApi
