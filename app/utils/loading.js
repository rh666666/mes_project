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

/**
 * 等待若干动画帧，便于 DOM 更新结束后再弹出 Toast
 * @param {number} [frames=2] - 帧数
 * @returns {Promise<void>}
 */
export function waitAnimationFrames(frames = 2) {
  const count = typeof frames === 'number' && frames > 0 ? Math.floor(frames) : 2
  return new Promise((resolve) => {
    let done = 0
    const tick = () => {
      done += 1
      if (done >= count) {
        resolve()
        return
      }
      if (typeof requestAnimationFrame === 'function') {
        requestAnimationFrame(tick)
      } else {
        setTimeout(tick, 16)
      }
    }
    tick()
  })
}

/**
 * 延迟展示 toast，避免与弹层关闭、页面重绘同一时刻冲突（uni-app H5 易出现 nodeValue 报错）
 * @param {UniApp.ShowToastOptions} options - toast 参数
 * @param {number} [delayMs=200] - 延迟毫秒数
 * @returns {void}
 */
export function showToastDeferred(options, delayMs = 200) {
  hideAppLoading()
  const delay = typeof delayMs === 'number' ? delayMs : 200
  setTimeout(() => {
    uni.hideToast()
    uni.showToast(options)
  }, delay)
}
