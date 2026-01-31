/**
 * Promise适配器模块
 * @module uni.promisify.adaptor
 * @description 为uni-app的API调用添加Promise支持，使回调式API可以使用async/await语法
 */

/**
 * 添加拦截器，将uni-app的回调式API转换为Promise
 * @description 拦截所有uni-app API调用，如果返回值是thenable对象，则转换为标准Promise
 * @example
 * // 转换前
 * uni.request({
 *   url: 'https://api.example.com',
 *   success: (res) => console.log(res),
 *   fail: (err) => console.error(err)
 * })
 *
 * // 转换后
 * const res = await uni.request({ url: 'https://api.example.com' })
 */
uni.addInterceptor({
  /**
   * 拦截返回值
   * @param {*} res - 原始返回值
   * @returns {Promise|*} 如果是thenable对象则返回Promise，否则返回原始值
   */
  returnValue (res) {
    if (!(!!res && (typeof res === "object" || typeof res === "function") && typeof res.then === "function")) {
      return res;
    }
    return new Promise((resolve, reject) => {
      res.then((res) => {
        if (!res) return resolve(res) 
        return res[0] ? reject(res[0]) : resolve(res[1])
      });
    });
  },
});
