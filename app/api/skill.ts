/**
 * 技能管理相关 API 模块
 * @module api/skill
 */

import request, { type MesApiEnvelope } from './request'

/** 技能类型字面量（与后端约定） */
export type SkillTypeValue = 'user' | 'device'

/** 技能类型常量 */
export const SkillType = {
  USER: 'user',
  DEVICE: 'device'
} as const satisfies Record<string, SkillTypeValue>

/** 技能类型中文标签 */
export const SkillTypeLabel: Record<SkillTypeValue, string> = {
  [SkillType.USER]: '用户技能',
  [SkillType.DEVICE]: '设备技能'
}

/** 技能类型展示色 */
export const SkillTypeColor: Record<SkillTypeValue, string> = {
  [SkillType.USER]: '#1989fa',
  [SkillType.DEVICE]: '#07c160'
}

/** 技能主数据 */
export interface Skill {
  id: number
  code: string
  name: string
  type: SkillTypeValue
  type_display: string
  creator: number | null
  modifier: number | null
  create_datetime: string | null
  update_datetime: string | null
}

/** 创建技能 */
export interface CreateSkillParams {
  code: string
  name: string
  type?: SkillTypeValue
}

/** 更新技能 */
export interface UpdateSkillParams {
  code?: string
  name?: string
  type?: SkillTypeValue
}

/** 用户技能关联 */
export interface UserSkill {
  id: number
  user: number
  user_name: string
  skill: number
  skill_code: string
  skill_name: string
  create_datetime: string
}

/** 设备技能关联 */
export interface DeviceSkill {
  id: number
  device: number
  device_name: string
  skill: number
  skill_code: string
  skill_name: string
  create_datetime: string
}

/** 列表查询（技能主数据） */
export interface SkillListQuery {
  name?: string
  code?: string
  type?: SkillTypeValue
  page?: number
  limit?: number
}

/**
 * 技能管理 API
 */
const skillApi = {
  /**
   * 技能分页列表
   * @param params - 筛选与分页
   */
  getSkillList(params: SkillListQuery = {}): Promise<MesApiEnvelope<Skill[]>> {
    return request({
      url: '/api/mes/skills/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<Skill[]>>
  },

  /**
   * 创建技能
   * @param data - 编码、名称、类型
   */
  createSkill(data: CreateSkillParams): Promise<MesApiEnvelope<Skill>> {
    return request({
      url: '/api/mes/skills/',
      method: 'POST',
      data: {
        code: data.code,
        name: data.name,
        type: data.type || SkillType.USER
      }
    }) as Promise<MesApiEnvelope<Skill>>
  },

  /**
   * 技能详情
   * @param id - 技能 ID
   */
  getSkillDetail(id: number): Promise<MesApiEnvelope<Skill>> {
    return request({
      url: `/api/mes/skills/${id}/`,
      method: 'GET'
    }) as Promise<MesApiEnvelope<Skill>>
  },

  /**
   * 更新技能
   * @param id - 技能 ID
   * @param data - 可部分字段
   */
  updateSkill(id: number, data: UpdateSkillParams): Promise<MesApiEnvelope<Skill>> {
    return request({
      url: `/api/mes/skills/${id}/`,
      method: 'PUT',
      data: {
        code: data.code,
        name: data.name,
        type: data.type
      }
    }) as Promise<MesApiEnvelope<Skill>>
  },

  /**
   * 删除技能
   * @param id - 技能 ID
   */
  deleteSkill(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/skills/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 用户技能关联列表
   * @param params - user/skill 筛选与分页
   */
  getUserSkillList(params: Record<string, unknown> = {}): Promise<MesApiEnvelope<UserSkill[]>> {
    return request({
      url: '/api/mes/skills/users/',
      method: 'GET',
      data: params
    }) as Promise<MesApiEnvelope<UserSkill[]>>
  },

  /**
   * 创建用户技能关联
   * @param data - user 与 skill ID
   */
  createUserSkill(data: { user: number; skill: number }): Promise<MesApiEnvelope<UserSkill>> {
    return request({
      url: '/api/mes/skills/users/',
      method: 'POST',
      data: {
        user: data.user,
        skill: data.skill
      }
    }) as Promise<MesApiEnvelope<UserSkill>>
  },

  /**
   * 删除用户技能关联
   * @param id - 关联记录 ID
   */
  deleteUserSkill(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/skills/users/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 设备技能关联列表
   * @param params - device/skill 筛选与分页
   */
  getDeviceSkillList(params: Record<string, unknown> = {}): Promise<MesApiEnvelope<DeviceSkill[]>> {
    return request({
      url: '/api/mes/skills/devices/',
      method: 'GET',
      data: params
    }) as Promise<MesApiEnvelope<DeviceSkill[]>>
  },

  /**
   * 创建设备技能关联
   * @param data - device 与 skill ID
   */
  createDeviceSkill(data: { device: number; skill: number }): Promise<MesApiEnvelope<DeviceSkill>> {
    return request({
      url: '/api/mes/skills/devices/',
      method: 'POST',
      data: {
        device: data.device,
        skill: data.skill
      }
    }) as Promise<MesApiEnvelope<DeviceSkill>>
  },

  /**
   * 删除设备技能关联
   * @param id - 关联记录 ID
   */
  deleteDeviceSkill(id: number): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: `/api/mes/skills/devices/${id}/`,
      method: 'DELETE'
    }) as Promise<MesApiEnvelope<unknown>>
  }
}

export default skillApi
