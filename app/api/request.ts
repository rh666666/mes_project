/**
 * HTTP 请求模块
 * @module api/request
 */

import config, { getStorageKey, isDebug } from '@/config/index.js'

const BASE_URL = config.api.baseURL
const TIMEOUT = config.api.timeout
const CSRF_ORIGIN = config.api.csrfOrigin

/**
 * MES API 通用响应外壳（与后端 StandardResponse / 分页列表约定对齐）
 */
export interface MesApiEnvelope<T = unknown> {
  code: number
  msg: string
  data?: T
  page?: number
  limit?: number
  total?: number
}

/** uni.request 返回体中与鉴权相关的最小形状（用于判断 token 失效） */
interface AuthRelatedPayload {
  code?: string | number
  msg?: string
}

/** 请求配置选项 */
export interface RequestOptions {
  /** 请求路径（不含 baseURL） */
  url: string
  /** HTTP 方法 */
  method?: string
  /** 请求体或查询参数 */
  data?: Record<string, unknown>
  /** 额外请求头 */
  header?: Record<string, string>
  /** 超时毫秒 */
  timeout?: number
}

/** 上传文件配置 */
export interface UploadFileOptions {
  /** 上传路径（不含 baseURL） */
  url: string
  /** 本地临时文件路径 */
  filePath: string
  /** 表单字段名 */
  name?: string
  formData?: Record<string, unknown>
  method?: string
  timeout?: number
}

/**
 * 组装鉴权与 CSRF 相关请求头。
 * @param customHeader - 调用方自定义头
 * @returns 合并后的请求头
 */
const getHeaders = (customHeader: Record<string, string> = {}): Record<string, string> => {
  const token = uni.getStorageSync(getStorageKey('access_token'))
  const csrfToken = uni.getStorageSync(getStorageKey('csrf_token'))

  const header: Record<string, string> = {
    ...customHeader
  }

  if (token) {
    header.Authorization = `Bearer ${token}`
  }

  if (csrfToken) {
    header['X-CSRFToken'] = csrfToken
  }

  if (CSRF_ORIGIN) {
    header.Origin = CSRF_ORIGIN
  }

  return header
}

/**
 * 发送 HTTP 请求并解析 JSON 响应。
 * @param options - 请求配置
 * @returns Promise，resolve 为后端返回的 JSON；401/token 失效时清理登录态并跳转登录页
 */
const request = (options: RequestOptions): Promise<unknown> => {
  return new Promise((resolve, reject) => {
    const header = getHeaders({
      'Content-Type': 'application/json',
      ...options.header
    })

    if (isDebug()) {
      console.log(`[Request] ${options.method || 'GET'} ${options.url}`, options.data)
    }

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: (options.method || 'GET') as UniNamespace.RequestOptions['method'],
      data:
        options.method === 'POST' || options.method === 'PUT'
          ? JSON.stringify(options.data || {})
          : options.data || {},
      header,
      timeout: options.timeout || TIMEOUT,
      success: (res) => {
        if (isDebug()) {
          console.log(`[Response] ${options.url}`, res.data)
        }

        const body = res.data as AuthRelatedPayload | undefined
        const isTokenInvalid =
          res.statusCode === 403 && body && body.code === 'token_not_valid'

        if (res.statusCode >= 200 && res.statusCode < 300 && !isTokenInvalid) {
          resolve(res.data)
        } else if (res.statusCode === 401 || isTokenInvalid) {
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
  })
}

/**
 * 上传文件（multipart），默认 POST。
 * @param options - 上传配置
 * @returns Promise，resolve 为解析后的 JSON（若非 JSON 则保持原始字符串）
 */
const uploadFile = (options: UploadFileOptions): Promise<unknown> => {
  return new Promise((resolve, reject) => {
    const header = getHeaders()

    if (isDebug()) {
      console.log(`[Upload] ${options.method || 'POST'} ${options.url}`, options.filePath)
    }

    uni.uploadFile({
      url: `${BASE_URL}${options.url}`,
      filePath: options.filePath,
      name: options.name || 'file',
      formData: options.formData || {},
      header,
      timeout: options.timeout || TIMEOUT,
      success: (res) => {
        let data: unknown = res.data
        try {
          data = JSON.parse(res.data as string) as unknown
        } catch {
          // 非 JSON 时保持字符串
        }

        if (isDebug()) {
          console.log(`[Upload Response] ${options.url}`, data)
        }

        const body = data as AuthRelatedPayload | undefined
        const isTokenInvalid =
          res.statusCode === 403 && body && body.code === 'token_not_valid'

        if (res.statusCode >= 200 && res.statusCode < 300 && !isTokenInvalid) {
          resolve(data)
        } else if (res.statusCode === 401 || isTokenInvalid) {
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
  })
}

export { uploadFile }
export default request
