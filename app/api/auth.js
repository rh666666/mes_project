/**
 * 认证相关API模块
 * @module api/auth
 */

import request, { uploadFile } from './request.js'

/**
 * 登录请求参数
 * @typedef {Object} LoginParams
 * @property {string} username - 用户名
 * @property {string} password - 密码
 */

/**
 * 登录响应数据
 * @typedef {Object} LoginResponse
 * @property {number} code - 响应状态码
 * @property {string} msg - 响应消息
 * @property {Object} data - 响应数据
 * @property {string} data.access - 访问令牌
 * @property {string} data.refresh - 刷新令牌
 * @property {string} data.csrf_token - CSRF令牌
 */

/**
 * 注册请求参数
 * @typedef {Object} RegisterParams
 * @property {string} username - 用户名
 * @property {string} password - 密码
 */

/**
 * 注册返回的用户信息
 * @typedef {Object} RegisterUser
 * @property {number} id - 用户ID
 * @property {string} username - 用户名
 * @property {string} email - 邮箱
 * @property {string} name - 昵称
 */

/**
 * 用户信息
 * @typedef {Object} UserProfile
 * @property {number} id - 用户ID
 * @property {string} username - 用户名
 * @property {string} name - 昵称
 * @property {string} email - 邮箱
 * @property {string|null} phone - 手机号
 * @property {string|null} avatar - 头像URL
 * @property {string|null} role - 角色
 * @property {string|null} signature - 个性签名
 * @property {number|null} creator - 创建人
 * @property {number|null} modifier - 修改人
 * @property {string|null} create_datetime - 创建时间
 * @property {string|null} update_datetime - 修改时间
 * @property {number|null} dept - 数据归属部门
 */

/**
 * 更新用户信息参数
 * @typedef {Object} UpdateUserInfoParams
 * @property {string} name - 昵称
 * @property {string} email - 邮箱
 * @property {string} phone - 手机号
 * @property {string} [signature] - 个性签名
 * @property {string|null} [role] - 角色
 * @property {number|null} [dept] - 数据归属部门ID
 */

/**
 * 更新头像参数
 * @typedef {Object} UpdateAvatarParams
 * @property {string} avatar - 头像文件路径
 */

/**
 * Token刷新请求参数
 * @typedef {Object} TokenRefreshParams
 * @property {string} refresh - 刷新令牌
 */

/**
 * Token刷新响应数据
 * @typedef {Object} TokenRefreshResponse
 * @property {string} access - 新的访问令牌
 */

/**
 * Token验证请求参数
 * @typedef {Object} TokenVerifyParams
 * @property {string} token - 访问令牌
 */

/**
 * 认证API对象
 * @namespace
 */
const authApi = {
  /**
   * 用户登录
   * @param {LoginParams} data - 登录参数
   * @returns {Promise<LoginResponse>} 返回登录结果的Promise
   * @example
   * authApi.login({ username: 'test', password: '123456' })
   *   .then(res => console.log(res.data.access))
   */
  login(data) {
    return request({
      url: '/api/auth/login/',
      method: 'POST',
      data: {
        username: data.username,
        password: data.password
      }
    })
  },

  /**
   * 用户注册
   * @param {RegisterParams} data - 注册参数
   * @returns {Promise<{code: number, msg: string, data: {user: RegisterUser}}>} 返回注册结果的Promise
   * @example
   * authApi.register({ username: 'test', password: '123456' })
   *   .then(res => console.log(res.data.user.id))
   */
  register(data) {
    return request({
      url: '/api/auth/register/',
      method: 'POST',
      data: {
        username: data.username,
        password: data.password
      }
    })
  },

  /**
   * 用户注销
   * @returns {Promise<{code: number, msg: string, data: null}>} 返回注销结果的Promise
   * @example
   * authApi.logout().then(res => console.log(res.msg))
   */
  logout() {
    return request({
      url: '/api/auth/logout/',
      method: 'POST'
    })
  },

  /**
   * 获取用户个人信息
   * @returns {Promise<{code: number, msg: string, data: UserProfile}>} 返回用户信息的Promise
   * @example
   * authApi.getProfile().then(res => console.log(res.data.username))
   */
  getProfile() {
    return request({
      url: '/api/auth/users/me/',
      method: 'GET'
    })
  },

  /**
   * 更新用户基本信息（昵称、邮箱、手机号、个性签名）
   * @param {UpdateUserInfoParams} data - 更新参数
   * @returns {Promise<{code: number, msg: string, data: UserProfile}>} 返回更新结果的Promise
   * @example
   * authApi.updateUserInfo({ name: '新昵称', email: 'test@example.com', phone: '13800138000', signature: '这是我的签名' })
   *   .then(res => console.log(res.data.name))
   */
  updateUserInfo(data) {
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
    })
  },

  /**
   * 更新用户头像
   * @param {UpdateAvatarParams} data - 更新参数
   * @returns {Promise<{code: number, msg: string, data: UserProfile}>} 返回更新结果的Promise
   * @example
   * authApi.updateAvatar({ avatar: 'file://temp/avatar.jpg' })
   *   .then(res => console.log(res.data.avatar))
   */
  updateAvatar(data) {
    return uploadFile({
      url: '/api/auth/users/me/avatar/',
      filePath: data.avatar,
      name: 'avatar'
    })
  },

  /**
   * 刷新访问令牌
   * @param {TokenRefreshParams} data - 刷新参数
   * @returns {Promise<TokenRefreshResponse>} 返回新的访问令牌
   * @example
   * authApi.refreshToken({ refresh: 'eyJhbGciOiJIUzI1NiIs...' })
   *   .then(res => console.log(res.access))
   */
  refreshToken(data) {
    return request({
      url: '/api/auth/token/refresh/',
      method: 'POST',
      data: {
        refresh: data.refresh
      }
    })
  },

  /**
   * 验证令牌是否有效
   * @param {TokenVerifyParams} data - 验证参数
   * @returns {Promise<{}>} 返回验证结果
   * @example
   * authApi.verifyToken({ token: 'eyJhbGciOiJIUzI1NiIs...' })
   *   .then(() => console.log('Token有效'))
   */
  verifyToken(data) {
    return request({
      url: '/api/auth/token/verify/',
      method: 'POST',
      data: {
        token: data.token
      }
    })
  }
}

export default authApi
