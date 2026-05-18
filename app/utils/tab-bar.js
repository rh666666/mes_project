/**
 * 原生 TabBar 按角色显隐（uni.setTabBarItem visible）
 * @module utils/tab-bar
 * @see https://uniapp.dcloud.net.cn/api/ui/tabbar.html#settabbaritem
 */

import { getStorageKey } from '@/config/index.js'

/** 「管理」在 pages.json tabBar.list 中的下标（首页 0、管理 1、我的 2） */
export const TAB_INDEX_MANAGE = 1

/** tabBar 页面路径（与 pages.json tabBar.list.pagePath 一致） */
const TAB_BAR_PAGE_PATHS = [
  'pages/index/index',
  'pages/manage/index',
  'pages/profile/index'
]

/**
 * 判断是否为管理员
 * @param {Object|null|undefined} userInfo - 用户信息
 * @returns {boolean}
 */
export function isAdminUser(userInfo) {
  return !!(userInfo && userInfo.role === 'admin')
}

/**
 * 读取本地用户信息
 * @returns {Object}
 */
export function getStoredUserInfo() {
  return uni.getStorageSync(getStorageKey('user_info')) || {}
}

/**
 * 当前页面是否为 tabBar 页（setTabBarItem 仅能在 tabBar 页调用）
 * @returns {boolean}
 */
export function isCurrentTabBarPage() {
  const pages = getCurrentPages()
  if (!pages.length) {
    return false
  }
  const page = pages[pages.length - 1]
  const route = (page.route || page.$page?.fullPath || '').replace(/^\//, '')
  return TAB_BAR_PAGE_PATHS.some(
    (path) => route === path || route.endsWith(path)
  )
}

/**
 * 按角色设置「管理」Tab 是否可见
 * 非 tabBar 页调用时静默跳过（登录页、子页面等），待进入 tabBar 页时由 onShow 同步
 * @param {Object|null|undefined} [userInfo] - 用户信息，缺省则从本地存储读取
 * @returns {void}
 */
export function applyTabBarByRole(userInfo) {
  if (!isCurrentTabBarPage()) {
    return
  }

  const info = userInfo !== undefined ? userInfo : getStoredUserInfo()
  const showManage = isAdminUser(info)

  uni.setTabBarItem({
    index: TAB_INDEX_MANAGE,
    visible: showManage
  })
}
