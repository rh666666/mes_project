/**
 * 应用入口文件
 * @file main.js
 * @description uni-app应用的入口文件，负责初始化Vue实例
 */

import App from './App'

// #ifndef VUE3
import Vue from 'vue'
import './uni.promisify.adaptor'
Vue.config.productionTip = false
App.mpType = 'app'
const app = new Vue({
  ...App
})
app.$mount()
// #endif

// #ifdef VUE3
import { createSSRApp } from 'vue'

/**
 * 创建Vue3应用实例
 * @returns {{app: VueApp}} 返回应用实例对象
 */
export function createApp() {
  const app = createSSRApp(App)
  return {
    app
  }
}
// #endif
