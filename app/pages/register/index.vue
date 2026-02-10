<template>
  <view class="page">
    <view class="auth-container">
      <wd-form ref="form" :model="formData">
        <view class="input-group">
          <wd-input
            v-model="formData.username"
            placeholder="请输入账号（2-20位字符）"
            :rules="usernameRules"
            clearable
            custom-class="auth-input"
          />

          <wd-input
            v-model="formData.password"
            placeholder="请输入密码（6-20位）"
            type="password"
            show-password
            :rules="passwordRules"
            clearable
            custom-class="auth-input"
          />

          <wd-input
            v-model="formData.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            show-password
            :rules="confirmPasswordRules"
            clearable
            custom-class="auth-input"
          />
        </view>

        <view class="agreement-item">
          <wd-checkbox v-model="formData.agreement" custom-class="agreement-checkbox">
            <text class="agreement-text">
              我已阅读并同意
              <text class="agreement-link" @click.stop="onViewAgreement">《用户协议》</text>
              和
              <text class="agreement-link" @click.stop="onViewPrivacy">《隐私政策》</text>
            </text>
          </wd-checkbox>
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
          注册
        </wd-button>

        <view class="form-footer">
          <text class="footer-text">已有账号？</text>
          <text class="login-link" @click="goToLogin">立即登录</text>
        </view>
      </wd-form>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth.js'

/**
 * 注册页面
 * @description 用户注册页面
 */
export default {
  data() {
    return {
      formData: {
        username: '',
        password: '',
        confirmPassword: '',
        agreement: false
      },
      isLoading: false,
      from: '',
      usernameRules: [
        { required: true, message: '请输入账号' },
        { min: 2, max: 20, message: '账号长度应为2-20位字符' }
      ],
      passwordRules: [
        { required: true, message: '请输入密码' },
        { min: 6, max: 20, message: '密码长度应为6-20位' }
      ]
    }
  },

  computed: {
    confirmPasswordRules() {
      return [
        { required: true, message: '请确认密码' },
        {
          validator: (value) => {
            if (value !== this.formData.password) {
              return '两次输入的密码不一致'
            }
            return true
          }
        }
      ]
    }
  },

  onLoad(options) {
    if (options.from) {
      this.from = options.from
    }
  },

  methods: {
    handleSubmit() {
      if (!this.formData.agreement) {
        uni.showToast({
          title: '请阅读并同意用户协议和隐私政策',
          icon: 'none'
        })
        return
      }

      this.$refs.form.validate().then(({ valid }) => {
        if (valid) {
          this.onRegisterSubmit()
        }
      })
    },

    async onRegisterSubmit() {
      this.isLoading = true

      try {
        const res = await authApi.register({
          username: this.formData.username.trim(),
          password: this.formData.password
        })

        if (res.code === 2000) {
          uni.showToast({
            title: '注册成功',
            icon: 'success'
          })

          setTimeout(() => {
            if (this.from === 'login') {
              uni.$emit('registerSuccess', {
                username: this.formData.username,
                password: this.formData.password
              })
              uni.navigateBack()
            } else {
              const username = encodeURIComponent(this.formData.username)
              const password = encodeURIComponent(this.formData.password)
              uni.redirectTo({
                url: `/pages/login/index?username=${username}&password=${password}`
              })
            }
          }, 1500)
        } else {
          uni.showToast({
            title: res.msg || '注册失败',
            icon: 'none'
          })
        }
      } catch (error) {
        uni.showToast({
          title: error.msg || '网络错误，请稍后重试',
          icon: 'none'
        })
        console.error('注册错误:', error)
      } finally {
        this.isLoading = false
      }
    },

    onViewAgreement() {
      uni.showModal({
        title: '用户协议',
        content: '这里是用户协议内容...',
        showCancel: false
      })
    },

    onViewPrivacy() {
      uni.showModal({
        title: '隐私政策',
        content: '这里是隐私政策内容...',
        showCancel: false
      })
    },

    goToLogin() {
      if (this.from === 'login') {
        uni.navigateBack()
      } else {
        uni.navigateBack({
          fail: () => {
            uni.redirectTo({
              url: '/pages/login/index'
            })
          }
        })
      }
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

  :deep(.wd-form) {
    width: 100%;
    max-width: 640rpx;
  }
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

.agreement-item {
  margin: 24rpx 0 48rpx;
  padding: 0 16rpx;
}

:deep(.agreement-checkbox) {
  .wd-checkbox__label {
    font-size: 24rpx;
    color: $uni-text-color-grey;
    line-height: 1.6;
  }
}

.agreement-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
  line-height: 1.6;
}

.agreement-link {
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

.login-link {
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
