/**
 * 工序管理相关 API 模块
 * @module api/process
 */

import request, { type MesApiEnvelope } from './request'

/** 工序资源 */
export interface Process {
  id: number
  code: string
  name: string
  description: string | null
  creator: number | null
  modifier: number | null
  create_datetime: string | null
  update_datetime: string | null
}

/** 工序技能需求 */
export interface ProcessSkillRequired {
  id: number
  process: number
  process_name: string
  skill: number
  skill_code: string
  skill_name: string
  create_datetime: string
}

/** 创建工序 */
export interface CreateProcessParams {
  code: string
  name: string
  description?: string
}

/** 更新工序 */
export interface UpdateProcessParams {
  code?: string
  name?: string
  description?: string
}

/** 创建工序技能需求 */
export interface CreateProcessSkillParams {
  process: number
  skill: number
}

/**
 * 工序管理 API
 */
const processApi = {
  /**
   * 工序分页列表
   * @param params - name/code 筛选与分页
   */
  getProcessList(params: Record<string, unknown> = {}): Promise<MesApiEnvelope<Process[]>> {
    return request({
      url: '/api/mes/processes/',
      method: 'GET',
      data: params
    }) as Promise<MesApiEnvelope<Process[]>>
  },

  /**
   * 创建工序
   * @param data - 编码与名称
   */
  createProcess(data: CreateProcessParams): Promise<MesApiEnvelope<Process>> {
    return request({
      url: '/api/mes/processes/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<Process>>
  },

  /**
   * 工序详情
   * @param id - 工序 ID
   */
  getProcessDetail(id: number): Promise<MesApiEnvelope<Process>> {
    return request({
      url: `/api/mes/processes/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<Process>>
  },

  /**
   * 更新工序
   * @param id - 工序 ID
   * @param data - 可部分字段
   */
  updateProcess(id: number, data: UpdateProcessParams): Promise<MesApiEnvelope<Process>> {
    return request({
      url: `/api/mes/processes/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        description: data.description
      }
    }) as Promise<MesApiEnvelope<Process>>
  },

  /**
   * 删除工序
   * @param id - 工序 ID
   */
  deleteProcess(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/processes/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 工序技能需求列表
   * @param params - process/skill 筛选与分页
   */
  getProcessSkillList(params: Record<string, unknown> = {}): Promise<MesApiEnvelope<ProcessSkillRequired[]>> {
    return request({
      url: '/api/mes/processes/skills/',
      method: 'GET',
      data: params
    }) as Promise<MesApiEnvelope<ProcessSkillRequired[]>>
  },

  /**
   * 创建工序技能需求
   * @param data - 工序与技能 ID
   */
  createProcessSkill(data: CreateProcessSkillParams): Promise<MesApiEnvelope<ProcessSkillRequired>> {
    return request({
      url: '/api/mes/processes/skills/',
      method: 'POST',
      data: {
        process: data.process,
        skill: data.skill
      }
    }) as Promise<MesApiEnvelope<ProcessSkillRequired>>
  },

  /**
   * 删除工序技能需求
   * @param id - 关联记录 ID
   */
  deleteProcessSkill(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/processes/skills/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  }
}

export default processApi
