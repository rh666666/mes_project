/**
 * 通用工具函数库
 * @module utils/common
 */

/**
 * 列表接口单次请求的 limit 上限（与后端各 ListRequestSerializer 的 max_value 一致）
 * @type {number}
 */
export const API_LIST_LIMIT_MAX = 100

/**
 * 将分页 limit 约束在 [1, {@link API_LIST_LIMIT_MAX}] 范围内
 * @param {number} [limit] - 期望每页条数
 * @returns {number}
 */
export function clampApiListLimit(limit) {
  const n = Number(limit)
  if (!Number.isFinite(n) || n < 1) {
    return API_LIST_LIMIT_MAX
  }
  return Math.min(Math.floor(n), API_LIST_LIMIT_MAX)
}

/**
 * 派工单剩余可生产数量（计划数量减已完成）
 * @param {{ quantity?: number, completed_quantity?: number }|null|undefined} order - 派工单或列表行
 * @returns {number}
 */
export function getDispatchRemainingQuantity(order) {
  const qty = Number(order?.quantity) || 0
  const completed = Number(order?.completed_quantity) || 0
  return Math.max(0, qty - completed)
}

/**
 * 按标准分页响应（code / data 数组 / total）批量请求直至拉取全量数据。
 * 单页 limit 不超过 {@link API_LIST_LIMIT_MAX}，防止单次请求过大。
 *
 * @param {function(Object): Promise<{code:number, data?:Array, total?:number, msg?:string}>} fetchPage
 *   入参为合并后的查询对象（含 page、limit 及业务筛选字段），须返回与项目列表接口一致的 Promise
 * @param {Object} [baseParams={}] - 除 page、limit 外的固定查询参数
 * @param {Object} [options={}] - 选项
 * @param {number} [options.pageSize] - 每页条数，默认 {@link API_LIST_LIMIT_MAX}
 * @param {number} [options.successCode] - 业务成功码，默认 2000
 * @param {number} [options.maxPages] - 最多请求页数，防止异常接口死循环，默认 500
 * @returns {Promise<Array>} 合并后的 data 列表
 * @throws {Error} 某一页 code 非成功或超出 maxPages 时抛出
 */
export async function fetchAllPagesWithPagedApi(fetchPage, baseParams = {}, options = {}) {
  const successCode = options.successCode ?? 2000
  const maxPages = options.maxPages ?? 500
  const pageSize = clampApiListLimit(options.pageSize ?? API_LIST_LIMIT_MAX)

  const merged = { ...baseParams }
  const all = []
  let page = 1

  while (page <= maxPages) {
    const res = await fetchPage({
      ...merged,
      page,
      limit: pageSize
    })

    if (!res || res.code !== successCode) {
      const err = new Error((res && res.msg) || '分页请求失败')
      err.raw = res
      throw err
    }

    const chunk = Array.isArray(res.data) ? res.data : []
    all.push(...chunk)

    const total = res.total
    if (chunk.length === 0) {
      break
    }
    if (typeof total === 'number') {
      if (all.length >= total) {
        break
      }
    } else if (chunk.length < pageSize) {
      break
    }
    page += 1
  }

  if (page > maxPages) {
    const err = new Error('分页拉取超过 maxPages 上限，已中止')
    err.partialData = all
    throw err
  }

  return all
}

/**
 * 防抖函数
 * @param {Function} fn - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function}
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 要执行的函数
 * @param {number} interval - 间隔时间（毫秒）
 * @returns {Function}
 */
export function throttle(fn, interval = 300) {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

/**
 * 深拷贝
 * @param {any} obj - 要拷贝的对象
 * @returns {any}
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const copy = {}
    Object.keys(obj).forEach(key => {
      copy[key] = deepClone(obj[key])
    })
    return copy
  }
  return obj
}

/**
 * 判断是否为空值
 * @param {any} value - 要判断的值
 * @returns {boolean}
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 获取对象属性值（支持嵌套路径）
 * @param {Object} obj - 对象
 * @param {string} path - 属性路径，如 'user.name'
 * @param {any} defaultValue - 默认值
 * @returns {any}
 */
export function get(obj, path, defaultValue) {
  const keys = path.split('.')
  let result = obj
  for (const key of keys) {
    if (result === null || result === undefined) {
      return defaultValue
    }
    result = result[key]
  }
  return result !== undefined ? result : defaultValue
}
