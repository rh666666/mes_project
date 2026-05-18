/**
 * 全局 Loading 配对工具（支持嵌套 show/hide）
 * @module utils/loading
 */

/** @type {number} 当前 loading 嵌套深度 */
let loadingDepth = 0

/**
 * 显示全局 loading（嵌套时仅最外层触发 uni.showLoading）
 * @param {string|{title?: string}} [titleOrOptions='加载中...'] - 提示文案或 uni.showLoading 风格参数
 * @returns {void}
 */
export function showAppLoading(titleOrOptions = '加载中...') {
  let title = '加载中...'
  if (typeof titleOrOptions === 'string') {
    title = titleOrOptions
  } else if (titleOrOptions && typeof titleOrOptions === 'object' && titleOrOptions.title) {
    title = titleOrOptions.title
  }

  if (loadingDepth === 0) {
    uni.showLoading({ title, mask: true })
  }
  loadingDepth += 1
}

/**
 * 关闭一层 loading（深度归零时触发 uni.hideLoading）
 * @returns {void}
 */
export function hideAppLoading() {
  if (loadingDepth <= 0) {
    loadingDepth = 0
    return
  }
  loadingDepth -= 1
  if (loadingDepth === 0) {
    uni.hideLoading()
  }
}

/**
 * 在 async 任务外包装 loading，确保配对
 * @param {() => Promise<*>} task - 异步任务
 * @param {string} [title='加载中...'] - 提示文案
 * @returns {Promise<*>}
 */
export async function withAppLoading(task, title = '加载中...') {
  showAppLoading(title)
  try {
    return await task()
  } finally {
    hideAppLoading()
  }
}

/**
 * 先关闭 loading 再弹出 toast（避免与 uni.showLoading 冲突）
 * @param {UniApp.ShowToastOptions} options - toast 参数
 * @returns {void}
 */
export function showToastAfterLoading(options) {
  hideAppLoading()
  uni.showToast(options)
}
