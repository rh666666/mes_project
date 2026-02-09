/**
 * API端点常量
 * @module constants/api
 */

/**
 * API基础URL配置
 * @readonly
 */
export const API_BASE_URL = {
  development: 'http://localhost:8000',
  production: 'https://api.example.com'
}

/**
 * 认证相关API端点
 * @readonly
 */
export const AUTH_API = {
  LOGIN: '/api/auth/login/',
  REGISTER: '/api/auth/register/',
  LOGOUT: '/api/auth/logout/',
  PROFILE: '/api/auth/users/me/',
  REFRESH_TOKEN: '/api/auth/token/refresh/',
  VERIFY_TOKEN: '/api/auth/token/verify/',
  USERS: '/api/auth/users/',
  ADMIN_UPDATE: (id) => `/api/auth/users/${id}/admin-update/`,
  AVATAR: '/api/auth/users/me/avatar/'
}

/**
 * 部门相关API端点
 * @readonly
 */
export const DEPT_API = {
  LIST: '/api/auth/depts/',
  DETAIL: (id) => `/api/auth/depts/${id}/`
}

/**
 * 设备相关API端点
 * @readonly
 */
export const DEVICE_API = {
  LIST: '/api/mes/devices/',
  DETAIL: (id) => `/api/mes/devices/${id}/`
}
