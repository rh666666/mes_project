/**
 * 存储键名常量
 * @module constants/storage
 */

/**
 * 存储键名前缀
 * @readonly
 */
export const STORAGE_PREFIX = {
  development: 'mes_dev_',
  production: 'mes_'
}

/**
 * 存储键名
 * @readonly
 */
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  CSRF_TOKEN: 'csrf_token',
  USER_INFO: 'user_info',
  REMEMBER_USERNAME: 'remember_username'
}

/**
 * 页面路径常量
 * @readonly
 */
export const PAGES = {
  LOGIN: '/pages/login/index',
  REGISTER: '/pages/register/index',
  INDEX: '/pages/index/index',
  PROFILE: '/pages/profile/index',
  PROFILE_DETAIL: '/pages/profile/detail',
  USER_MANAGEMENT: '/pages/admin/user-management',
  DEPT_MANAGEMENT: '/pages/admin/dept-management',
  DEVICE_MANAGEMENT: '/pages/admin/device-management',
  USER_EDIT: (id) => `/pages/admin/user/edit?id=${id}`,
  DEPT_EDIT: (id) => id ? `/pages/admin/dept/edit?id=${id}` : '/pages/admin/dept/edit',
  DEVICE_EDIT: (id) => id ? `/pages/admin/device/edit?id=${id}` : '/pages/admin/device/edit'
}
