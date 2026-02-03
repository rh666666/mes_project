/**
 * HTTP请求模块
 * @module api/request
 */

import config, { getStorageKey, getCsrfOrigin, isDebug } from '@/config/index.js'

const BASE_URL = config.api.baseURL
const TIMEOUT = config.api.timeout
const CSRF_ORIGIN = config.api.csrfOrigin

/**
 * 请求配置选项
 * @typedef {Object} RequestOptions
 * @property {string} url - 请求地址
 * @property {string} [method='GET'] - 请求方法
 * @property {Object} [data] - 请求数据
 * @property {Object} [header] - 请求头
 * @property {number} [timeout] - 超时时间
 */

/**
 * 获取请求头
 * @param {Object} customHeader - 自定义请求头
 * @returns {Object} 合并后的请求头
 */
const getHeaders = (customHeader = {}) => {
  const token = uni.getStorageSync(getStorageKey('access_token'))
  const csrfToken = uni.getStorageSync(getStorageKey('csrf_token'))

  const header = {
    ...customHeader
  }

  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  if (csrfToken) {
    header['X-CSRFToken'] = csrfToken
  }

  // 添加Origin头用于CSRF验证
  if (CSRF_ORIGIN) {
    header['Origin'] = CSRF_ORIGIN
  }

  return header
}

/**
 * 发送HTTP请求
 * @param {RequestOptions} options - 请求配置选项
 * @returns {Promise<any>} 返回响应数据的Promise
 * @example
 * request({
 *   url: '/api/auth/login/',
 *   method: 'POST',
 *   data: { username: 'test', password: '123456' }
 * }).then(res => console.log(res))
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    const header = getHeaders({
      'Content-Type': 'application/json',
      ...options.header
    })

    if (isDebug()) {
      console.log(`[Request] ${options.method || 'GET'} ${options.url}`, options.data)
    }

    const requestTask = uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.method === 'POST' || options.method === 'PUT' ? JSON.stringify(options.data || {}) : options.data || {},
      header: header,
      timeout: options.timeout || TIMEOUT,
      success: (res) => {
        if (isDebug()) {
          console.log(`[Response] ${options.url}`, res.data)
        }

        // 检查是否为token无效 (HTTP 403 且 code 为 token_not_valid)
        const isTokenInvalid = res.statusCode === 403 &&
          res.data && res.data.code === 'token_not_valid'

        if (res.statusCode >= 200 && res.statusCode < 300 && !isTokenInvalid) {
          resolve(res.data)
        } else if (res.statusCode === 401 || isTokenInvalid) {
          // 401: 未授权, token_not_valid: token无效
          uni.removeStorageSync(getStorageKey('access_token'))
          uni.removeStorageSync(getStorageKey('refresh_token'))
          uni.removeStorageSync(getStorageKey('csrf_token'))
          uni.removeStorageSync(getStorageKey('user_info'))
          uni.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          })
          setTimeout(() => {
            uni.redirectTo({
              url: '/pages/login/index'
            })
          }, 1500)
          reject(res.data)
        } else {
          reject(res.data)
        }
      },
      fail: (err) => {
        if (isDebug()) {
          console.error(`[Request Error] ${options.url}`, err)
        }

        uni.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        reject(err)
      }
    })

    return requestTask
  })
}

/**
 * 上传文件
 * @param {Object} options - 上传配置选项
 * @param {string} options.url - 上传地址
 * @param {string} options.filePath - 文件路径
 * @param {string} [options.name='file'] - 文件字段名
 * @param {Object} [options.formData] - 附加的表单数据
 * @param {string} [options.method='POST'] - 请求方法
 * @returns {Promise<any>} 返回响应数据的Promise
 * @example
 * uploadFile({
 *   url: '/api/auth/profile/',
 *   filePath: 'temp/avatar.jpg',
 *   name: 'avatar',
 *   method: 'PATCH'
 * }).then(res => console.log(res))
 */
const uploadFile = (options) => {
  return new Promise((resolve, reject) => {
    const header = getHeaders()

    if (isDebug()) {
      console.log(`[Upload] ${options.method || 'POST'} ${options.url}`, options.filePath)
    }

    const uploadTask = uni.uploadFile({
      url: `${BASE_URL}${options.url}`,
      filePath: options.filePath,
      name: options.name || 'file',
      formData: options.formData || {},
      header: header,
      timeout: options.timeout || TIMEOUT,
      success: (res) => {
        let data = res.data
        try {
          data = JSON.parse(res.data)
        } catch (e) {
          // 如果不是JSON格式，保持原样
        }

        if (isDebug()) {
          console.log(`[Upload Response] ${options.url}`, data)
        }

        // 检查是否为token无效 (HTTP 403 且 code 为 token_not_valid)
        const isTokenInvalid = res.statusCode === 403 &&
          data && data.code === 'token_not_valid'

        if (res.statusCode >= 200 && res.statusCode < 300 && !isTokenInvalid) {
          resolve(data)
        } else if (res.statusCode === 401 || isTokenInvalid) {
          // 401: 未授权, token_not_valid: token无效
          uni.removeStorageSync(getStorageKey('access_token'))
          uni.removeStorageSync(getStorageKey('refresh_token'))
          uni.removeStorageSync(getStorageKey('csrf_token'))
          uni.removeStorageSync(getStorageKey('user_info'))
          uni.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          })
          setTimeout(() => {
            uni.redirectTo({
              url: '/pages/login/index'
            })
          }, 1500)
          reject(data)
        } else {
          reject(data)
        }
      },
      fail: (err) => {
        if (isDebug()) {
          console.error(`[Upload Error] ${options.url}`, err)
        }

        uni.showToast({
          title: '文件上传失败',
          icon: 'none'
        })
        reject(err)
      }
    })

    return uploadTask
  })
}

export { uploadFile }
export default request
