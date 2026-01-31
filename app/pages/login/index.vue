<template>
  <view class="page">
    <AuthContainer>
      <LoginForm
        :loading="isLoading"
        @submit="onLoginSubmit"
        @forgot-password="onForgotPassword"
        @register="goToRegister"
        ref="loginForm"
      />
    </AuthContainer>
  </view>
</template>

<script>
import AuthContainer from '@/components/auth/AuthContainer.vue'
import LoginForm from '@/components/auth/LoginForm.vue'
import authApi from '@/api/auth.js'
import { getStorageKey } from '@/config/index.js'

export default {
  components: {
    AuthContainer,
    LoginForm
  },

  data() {
    return {
      isLoading: false
    }
  },

  methods: {
    async onLoginSubmit(formData) {
      this.isLoading = true

      try {
        const res = await authApi.login({
          username: formData.username,
          password: formData.password
        })

        if (res.code === 2000) {
          uni.setStorageSync(getStorageKey('access_token'), res.data.access)
          uni.setStorageSync(getStorageKey('refresh_token'), res.data.refresh)
          uni.setStorageSync(getStorageKey('csrf_token'), res.data.csrf_token)

          // 获取完整个人信息
          try {
            const profileRes = await authApi.getProfile()
            if (profileRes.code === 2000) {
              uni.setStorageSync(getStorageKey('user_info'), {
                id: profileRes.data.id,
                username: profileRes.data.username,
                name: profileRes.data.name,
                avatar: profileRes.data.avatar,
                signature: profileRes.data.signature
              })
            }
          } catch (profileError) {
            console.error('获取个人信息失败:', profileError)
            // 即使获取个人信息失败，也使用基本信息
            uni.setStorageSync(getStorageKey('user_info'), {
              username: formData.username
            })
          }

          uni.showToast({
            title: '登录成功',
            icon: 'success'
          })

          if (formData.remember) {
            uni.setStorageSync('remember_username', formData.username)
          } else {
            uni.removeStorageSync('remember_username')
          }

          setTimeout(() => {
            const pages = getCurrentPages()
            if (pages.length > 1) {
              uni.navigateBack()
            } else {
              uni.switchTab({
                url: '/pages/index/index'
              })
            }
          }, 1500)
        } else {
          uni.showToast({
            title: res.msg || '登录失败',
            icon: 'none'
          })
        }
      } catch (error) {
        uni.showToast({
          title: error.msg || '网络错误，请稍后重试',
          icon: 'none'
        })
        console.error('登录错误:', error)
      } finally {
        this.isLoading = false
      }
    },

    onForgotPassword() {
      uni.showToast({
        title: '忘记密码功能开发中',
        icon: 'none'
      })
    },

    goToRegister() {
      uni.navigateTo({
        url: '/pages/register/index'
      })
    }
  },

  onLoad(options) {
    if (options.username && options.password && this.$refs.loginForm) {
      const username = decodeURIComponent(options.username)
      const password = decodeURIComponent(options.password)
      this.$refs.loginForm.formData.username = username
      this.$refs.loginForm.formData.password = password
      this.$refs.loginForm.formData.remember = false
    } else {
      const rememberedUsername = uni.getStorageSync('remember_username')
      if (rememberedUsername && this.$refs.loginForm) {
        this.$refs.loginForm.formData.username = rememberedUsername
        this.$refs.loginForm.formData.remember = true
      }
    }
  }
}
</script>

<style lang="scss">
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: $uni-md-background;
  box-sizing: border-box;
}
</style>
