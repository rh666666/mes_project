<template>
  <view class="page">
    <view class="auth-container">
      <wd-form ref="form" :model="formData">
        <view class="input-group">
          <wd-input
            v-model="formData.username"
            placeholder="请输入账号"
            :rules="usernameRules"
            clearable
            custom-class="auth-input"
          />

          <wd-input
            v-model="formData.password"
            placeholder="请输入密码"
            type="password"
            show-password
            :rules="passwordRules"
            clearable
            custom-class="auth-input"
          />
        </view>

        <view class="form-options">
          <wd-checkbox v-model="formData.remember" custom-class="remember-checkbox">记住我</wd-checkbox>
          <text class="forgot-link" @click="onForgotPassword">忘记密码？</text>
        </view>

        <wd-button
          type="primary"
          size="large"
          block
          round
          :loading="isLoading"
          custom-class="auth-button"
          @click="handleSubmit"
        >
          登录
        </wd-button>

        <view class="form-footer">
          <text class="footer-text">还没有账号？</text>
          <text class="register-link" @click="goToRegister">立即注册</text>
        </view>
      </wd-form>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth.js'
import { getStorageKey } from '@/config/index.js'

/**
 * 登录页面
 * @description 用户登录页面
 */
export default {
  data() {
    return {
      formData: {
        username: '',
        password: '',
        remember: false
      },
      isLoading: false,
      usernameRules: [
        { required: true, message: '请输入账号' }
      ],
      passwordRules: [
        { required: true, message: '请输入密码' },
        { min: 6, message: '密码长度不能少于6位' }
      ]
    }
  },

  onLoad(options) {
    if (options.username && options.password) {
      this.formData.username = decodeURIComponent(options.username)
      this.formData.password = decodeURIComponent(options.password)
      this.formData.remember = false
    } else {
      const rememberedUsername = uni.getStorageSync('remember_username')
      if (rememberedUsername) {
        this.formData.username = rememberedUsername
        this.formData.remember = true
      }
    }
  },

  onShow() {
    uni.$once('registerSuccess', (data) => {
      if (data.username && data.password) {
        this.formData.username = data.username
        this.formData.password = data.password
        this.formData.remember = false
      }
    })
  },

  methods: {
    handleSubmit() {
      this.$refs.form.validate().then(({ valid }) => {
        if (valid) {
          this.onLoginSubmit()
        }
      })
    },

    async onLoginSubmit() {
      this.isLoading = true

      try {
        const res = await authApi.login({
          username: this.formData.username.trim(),
          password: this.formData.password
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
                avatar: profileRes.data.avatar || '',
                signature: profileRes.data.signature || '',
                role: profileRes.data.role || 'user'
              })
            }
          } catch (profileError) {
            console.error('获取个人信息失败:', profileError)
            uni.setStorageSync(getStorageKey('user_info'), {
              username: this.formData.username,
              role: 'user'
            })
          }

          uni.showToast({
            title: '登录成功',
            icon: 'success'
          })

          if (this.formData.remember) {
            uni.setStorageSync('remember_username', this.formData.username)
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
        url: '/pages/register/index?from=login'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: $uni-bg-color-grey;
  box-sizing: border-box;
}

.auth-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48rpx;
  min-height: calc(100vh - env(safe-area-inset-bottom));
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 24rpx;
}

:deep(.auth-input) {
  background-color: $uni-bg-color-white;
  border-radius: 24rpx;
  padding: 24rpx 32rpx;
  
  .wd-input__inner {
    height: 48rpx;
    font-size: 30rpx;
  }
  
  .wd-input__placeholder {
    font-size: 30rpx;
    color: $uni-text-color-placeholder;
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24rpx 0 48rpx;
  padding: 0 16rpx;
}

:deep(.remember-checkbox) {
  .wd-checkbox__label {
    font-size: 26rpx;
    color: $uni-text-color-grey;
  }
}

.forgot-link {
  font-size: 26rpx;
  color: $uni-color-primary;
}

:deep(.auth-button) {
  height: 96rpx;
  font-size: 32rpx;
  font-weight: 500;
  border-radius: 48rpx;
}

.form-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 48rpx;
  gap: 8rpx;
}

.footer-text {
  font-size: 28rpx;
  color: $uni-text-color-grey;
}

.register-link {
  font-size: 28rpx;
  color: $uni-color-primary;
  font-weight: 500;
}

@media (max-width: 768px) {
  .auth-container {
    padding: 32rpx;
    align-items: flex-start;
    padding-top: 120rpx;
  }
}
</style>
