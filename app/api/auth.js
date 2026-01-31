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
 * 用户信息
 * @typedef {Object} UserProfile
 * @property {number} id - 用户ID
 * @property {string} username - 用户名
 * @property {string} name - 昵称
 * @property {string} email - 邮箱
 * @property {string} phone - 手机号
 * @property {string} avatar - 头像URL
 * @property {string} role - 角色
 * @property {string} signature - 个性签名
 */

/**
 * 更新用户信息参数
 * @typedef {Object} UpdateUserInfoParams
 * @property {string} name - 昵称
 * @property {string} email - 邮箱
 * @property {string} phone - 手机号
 * @property {string} signature - 个性签名
 */

/**
 * 更新头像参数
 * @typedef {Object} UpdateAvatarParams
 * @property {string} avatar - 头像文件路径
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
   * @returns {Promise<{code: number, msg: string, data: Object}>} 返回注册结果的Promise
   * @example
   * authApi.register({ username: 'test', password: '123456' })
   *   .then(res => console.log(res.msg))
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
   * @returns {Promise<{code: number, msg: string}>} 返回注销结果的Promise
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
      url: '/api/auth/profile/',
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
      url: '/api/auth/profile/',
      method: 'PUT',
      data: {
        name: data.name || '',
        email: data.email || '',
        phone: data.phone || '',
        signature: data.signature || ''
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
      url: '/api/auth/upload_avatar/',
      filePath: data.avatar,
      name: 'avatar'
    })
  }
}

export default authApi
