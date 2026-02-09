/**
 * 用户管理组合式函数
 * @module composables/useUser
 * @description 封装用户信息获取、缓存等通用逻辑
 */

import { getStorageKey } from '@/config/index.js'
import authApi from '@/api/auth.js'

/**
 * 创建用户管理 mixin
 * @returns {Object} mixin 对象
 */
export function createUserMixin() {
  return {
    data() {
      return {
        /** @type {Object} 用户信息 */
        userInfo: {},
        /** @type {boolean} 是否已登录 */
        isLoggedIn: false
      }
    },

    computed: {
      /**
       * 判断当前用户是否为管理员
       * @returns {boolean}
       */
      isAdmin() {
        return this.userInfo && this.userInfo.role === 'admin'
      },
      /**
       * 显示的用户名
       * @returns {string}
       */
      displayName() {
        if (!this.isLoggedIn) return '未登录'
        return this.userInfo.name || '未设置昵称'
      },
      /**
       * 显示的角色信息
       * @returns {string}
       */
      displayRole() {
        if (!this.isLoggedIn) return '请点击登录'
        return this.userInfo.signature || '已登录'
      }
    },

    onShow() {
      this.checkLoginStatus()
    },

    methods: {
      /**
       * 检查登录状态并加载用户信息
       * @async
       */
      async checkLoginStatus() {
        const token = uni.getStorageSync(getStorageKey('access_token'))
        let userInfo = uni.getStorageSync(getStorageKey('user_info'))
        this.isLoggedIn = !!token

        if (this.isLoggedIn && !userInfo) {
          try {
            const res = await authApi.getProfile()
            if (res.code === 2000) {
              userInfo = {
                id: res.data.id,
                username: res.data.username,
                name: res.data.name,
                avatar: res.data.avatar || '',
                signature: res.data.signature || '',
                role: res.data.role || 'user'
              }
              uni.setStorageSync(getStorageKey('user_info'), userInfo)
            }
          } catch (error) {
            console.error('获取个人信息失败:', error)
          }
        }

        this.userInfo = userInfo || {}
      },

      /**
       * 更新本地用户信息
       * @param {Object} data - 用户信息
       */
      updateUserInfo(data) {
        this.userInfo = { ...this.userInfo, ...data }
        uni.setStorageSync(getStorageKey('user_info'), this.userInfo)
      },

      /**
       * 跳转到登录页
       */
      goToLogin() {
        uni.navigateTo({
          url: '/pages/login/index'
        })
      },

      /**
       * 跳转到个人详情页
       */
      goToProfileDetail() {
        if (this.isLoggedIn) {
          uni.navigateTo({
            url: '/pages/profile/detail'
          })
        } else {
          this.goToLogin()
        }
      }
    }
  }
}
