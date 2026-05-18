/**
 * 格式化工具函数库
 * @module utils/format
 */

import { getApiBaseURL } from '@/config/index.js'

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @param {string} format - 格式模板
 * @returns {string}
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/** 列表/详情中接口日期时间字段的默认展示格式：年-月-日 时:分:秒（24 小时制，本地时区） */
export const DATETIME_DISPLAY_FORMAT = 'YYYY-MM-DD HH:mm:ss'

/**
 * 将接口返回的日期时间格式化为 {@link DATETIME_DISPLAY_FORMAT}（等价于 `YYYY-MM-DD HH:mm:ss`）
 * @param {string|number|Date|null|undefined} value - ISO 字符串、时间戳或 Date；空值返回占位符
 * @param {string} [emptyPlaceholder='-'] - 无值或非法日期时的展示文案
 * @returns {string}
 */
export function formatDateTime(value, emptyPlaceholder = '-') {
  if (value === null || value === undefined || value === '') {
    return emptyPlaceholder
  }
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) {
    return emptyPlaceholder
  }
  const y = d.getFullYear()
  const mo = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  const s = String(d.getSeconds()).padStart(2, '0')
  return `${y}-${mo}-${day} ${h}:${mi}:${s}`
}

/**
 * 将 Django Duration 或 HH:MM:SS 字符串格式化为可读中文时长
 * @param {string|null|undefined} value - 如 `01:30:00`、`2 01:30:00.123456`
 * @param {string} [emptyPlaceholder='-'] - 无值或非法时的展示文案
 * @returns {string}
 */
export function formatDuration(value, emptyPlaceholder = '-') {
  if (value === null || value === undefined || value === '') {
    return emptyPlaceholder
  }
  const raw = String(value).trim()
  if (!raw) {
    return emptyPlaceholder
  }

  let days = 0
  let timePart = raw
  const dayMatch = raw.match(/^(\d+)\s+(.+)$/)
  if (dayMatch) {
    days = parseInt(dayMatch[1], 10)
    timePart = dayMatch[2]
  }

  const segments = timePart.split(':')
  if (segments.length < 2 || segments.length > 3) {
    return emptyPlaceholder
  }

  const hours = parseInt(segments[0], 10)
  const minutes = parseInt(segments[1], 10)
  const secondsPart = segments[2] != null ? segments[2].split('.')[0] : '0'
  const seconds = parseInt(secondsPart, 10)

  if ([hours, minutes, seconds, days].some((n) => Number.isNaN(n) || n < 0)) {
    return emptyPlaceholder
  }

  const totalHours = days * 24 + hours
  const parts = []
  if (totalHours > 0) {
    parts.push(`${totalHours}小时`)
  }
  if (minutes > 0) {
    parts.push(`${minutes}分`)
  }
  if (seconds > 0 || parts.length === 0) {
    parts.push(`${seconds}秒`)
  }
  return parts.join('')
}

/**
 * 获取完整头像URL
 * @param {string} avatar - 头像路径
 * @returns {string}
 */
export function getFullAvatarUrl(avatar) {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  return getApiBaseURL() + avatar
}

/**
 * 格式化数字（添加千分位）
 * @param {number} num - 数字
 * @returns {string}
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 截断文本
 * @param {string} text - 文本
 * @param {number} maxLength - 最大长度
 * @param {string} suffix - 后缀
 * @returns {string}
 */
export function truncateText(text, maxLength = 100, suffix = '...') {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + suffix
}

/**
 * 获取用户名字首字母
 * @param {string} name - 用户名
 * @returns {string}
 */
export function getUserInitial(name) {
  if (!name) return 'U'
  return name.charAt(0).toUpperCase()
}
