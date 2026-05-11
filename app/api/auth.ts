/**
 * 认证相关 API 模块
 * @module api/auth
 */

import request, { uploadFile, type MesApiEnvelope, type UploadFileOptions } from './request'

/** 登录请求体 */
export interface LoginParams {
  username: string
  password: string
}

/** 登录成功时 data 中的令牌字段 */
export interface LoginTokensData {
  access: string
  refresh: string
  csrf_token: string
}

/** 注册请求体 */
export interface RegisterParams {
  username: string
  password: string
}

/** 注册返回中的 user 片段 */
export interface RegisterUser {
  id: number
  username: string
  email: string
  name: string
}

/** 用户资料 */
export interface UserProfile {
  id: number
  username: string
  name: string
  email: string
  phone: string | null
  avatar: string | null
  role: string | null
  signature: string | null
  creator: number | null
  modifier: number | null
  create_datetime: string | null
  update_datetime: string | null
  dept: number | null
}

/** 用户列表项 */
export interface UserListItem {
  id: number
  username: string
  name: string
  email: string
  phone: string | null
  avatar: string | null
  role: string | null
  signature: string | null
  creator: number | null
  modifier: number | null
  create_datetime: string | null
  update_datetime: string | null
  dept: number | null
}

/** 管理员更新用户 */
export interface AdminUpdateUserParams {
  role?: string
  dept?: number
}

/** 更新当前用户资料 */
export interface UpdateUserInfoParams {
  name: string
  email: string
  phone: string
  signature?: string
  role?: string | null
  dept?: number | null
}

/** 更新头像 */
export interface UpdateAvatarParams {
  avatar: string
}

/** 刷新 access */
export interface TokenRefreshParams {
  refresh: string
}

/** 仅含新 access 的响应（与后端实际结构保持一致时可再收紧） */
export interface TokenRefreshData {
  access: string
}

/** 校验 token */
export interface TokenVerifyParams {
  token: string
}

export interface UserListQuery {
  search?: string
  role?: string
  dept?: number
  page?: number
  limit?: number
}

/**
 * 认证相关 API
 */
const authApi = {
  /**
   * 用户登录
   * @param data - 登录参数
   */
  login(data: LoginParams): Promise<MesApiEnvelope<LoginTokensData>> {
    return request({
      url: '/api/auth/login/',
      method: 'POST',
      data: {
        username: data.username,
        password: data.password
      }
    }) as Promise<MesApiEnvelope<LoginTokensData>>
  },

  /**
   * 用户注册
   * @param data - 注册参数
   */
  register(
    data: RegisterParams
  ): Promise<MesApiEnvelope<{ user: RegisterUser }>> {
    return request({
      url: '/api/auth/register/',
      method: 'POST',
      data: {
        username: data.username,
        password: data.password
      }
    }) as Promise<MesApiEnvelope<{ user: RegisterUser }>>
  },

  /**
   * 用户注销
   */
  logout(): Promise<MesApiEnvelope<null>> {
    return request({
      url: '/api/auth/logout/',
      method: 'POST'
    }) as Promise<MesApiEnvelope<null>>
  },

  /**
   * 获取当前登录用户资料
   */
  getProfile(): Promise<MesApiEnvelope<UserProfile>> {
    return request({
      url: '/api/auth/users/me/',
      method: 'GET'
    }) as Promise<MesApiEnvelope<UserProfile>>
  },

  /**
   * 更新用户基本信息
   * @param data - 昵称、邮箱等
   */
  updateUserInfo(data: UpdateUserInfoParams): Promise<MesApiEnvelope<UserProfile>> {
    return request({
      url: '/api/auth/users/me/',
      method: 'PUT',
      data: {
        name: data.name,
        email: data.email,
        phone: data.phone,
        signature: data.signature,
        role: data.role,
        dept: data.dept
      }
    }) as Promise<MesApiEnvelope<UserProfile>>
  },

  /**
   * 上传用户头像
   * @param data - 本地临时文件路径
   */
  updateAvatar(data: UpdateAvatarParams): Promise<MesApiEnvelope<UserProfile>> {
    const opts: UploadFileOptions = {
      url: '/api/auth/users/me/avatar/',
      filePath: data.avatar,
      name: 'avatar'
    }
    return uploadFile(opts) as Promise<MesApiEnvelope<UserProfile>>
  },

  /**
   * 刷新访问令牌
   * @param data - refresh token
   */
  refreshToken(data: TokenRefreshParams): Promise<MesApiEnvelope<TokenRefreshData>> {
    return request({
      url: '/api/auth/token/refresh/',
      method: 'POST',
      data: {
        refresh: data.refresh
      }
    }) as Promise<MesApiEnvelope<TokenRefreshData>>
  },

  /**
   * 验证访问令牌是否有效
   * @param data - access token
   */
  verifyToken(data: TokenVerifyParams): Promise<MesApiEnvelope<unknown>> {
    return request({
      url: '/api/auth/token/verify/',
      method: 'POST',
      data: {
        token: data.token
      }
    }) as Promise<MesApiEnvelope<unknown>>
  },

  /**
   * 用户列表（管理员）
   * @param params - 筛选与分页
   */
  getUserList(params: UserListQuery = {}): Promise<MesApiEnvelope<UserListItem[]>> {
    return request({
      url: '/api/auth/users/',
      method: 'GET',
      data: params as Record<string, unknown>
    }) as Promise<MesApiEnvelope<UserListItem[]>>
  },

  /**
   * 管理员更新指定用户
   * @param id - 用户 ID
   * @param data - 角色、部门等
   */
  adminUpdateUser(
    id: number,
    data: AdminUpdateUserParams
  ): Promise<MesApiEnvelope<UserProfile>> {
    return request({
      url: `/api/auth/users/${id}/admin-update/`,
      method: 'PUT',
      data: {
        role: data.role,
        dept: data.dept
      }
    }) as Promise<MesApiEnvelope<UserProfile>>
  }
}

export default authApi
