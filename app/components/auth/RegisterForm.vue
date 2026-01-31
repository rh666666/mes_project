<template>
  <view class="register-form-container">
    <view class="form-body">
      <view class="form-item" :class="{ 'has-error': errors.username }">
        <text class="form-label">账号</text>
        <input
          class="form-input"
          type="text"
          v-model="formData.username"
          placeholder="请输入账号（2-20位字符）"
          @blur="validateField('username')"
        />
        <text v-if="errors.username" class="error-text">{{ errors.username }}</text>
      </view>

      <view class="form-item" :class="{ 'has-error': errors.password }">
        <text class="form-label">密码</text>
        <input
          class="form-input"
          :type="showPassword ? 'text' : 'password'"
          v-model="formData.password"
          placeholder="请输入密码（6-20位）"
          @blur="validateField('password')"
        />
        <view class="password-toggle" @click="togglePassword">
          <text class="toggle-icon">{{ showPassword ? '隐藏' : '显示' }}</text>
        </view>
        <text v-if="errors.password" class="error-text">{{ errors.password }}</text>
      </view>

      <view class="form-item" :class="{ 'has-error': errors.confirmPassword }">
        <text class="form-label">确认密码</text>
        <input
          class="form-input"
          :type="showConfirmPassword ? 'text' : 'password'"
          v-model="formData.confirmPassword"
          placeholder="请再次输入密码"
          @blur="validateField('confirmPassword')"
        />
        <view class="password-toggle" @click="toggleConfirmPassword">
          <text class="toggle-icon">{{ showConfirmPassword ? '隐藏' : '显示' }}</text>
        </view>
        <text v-if="errors.confirmPassword" class="error-text">{{ errors.confirmPassword }}</text>
      </view>

      <view class="form-item agreement-item" :class="{ 'has-error': errors.agreement }">
        <label class="agreement-wrapper" @click="toggleAgreement">
          <view class="checkbox" :class="{ checked: formData.agreement }">
            <text v-if="formData.agreement" class="check-icon">✓</text>
          </view>
          <view class="agreement-text">
            <text>我已阅读并同意</text>
            <text class="agreement-link" @click.stop="onViewAgreement">《用户协议》</text>
            <text>和</text>
            <text class="agreement-link" @click.stop="onViewPrivacy">《隐私政策》</text>
          </view>
        </label>
        <text v-if="errors.agreement" class="error-text">{{ errors.agreement }}</text>
      </view>

      <button
        class="submit-btn"
        :class="{ loading: isLoading }"
        :disabled="isLoading || !isFormValid"
        @click="handleSubmit"
      >
        <text v-if="!isLoading">注册</text>
        <view v-else class="loading-wrapper">
          <view class="loading-spinner"></view>
          <text>注册中...</text>
        </view>
      </button>

      <view class="form-footer">
        <text class="footer-text">已有账号？</text>
        <text class="login-link" @click="onLogin">立即登录</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'RegisterForm',

  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      formData: {
        username: '',
        password: '',
        confirmPassword: '',
        agreement: false
      },
      errors: {
        username: '',
        password: '',
        confirmPassword: '',
        agreement: ''
      },
      showPassword: false,
      showConfirmPassword: false,
      isLoading: false
    }
  },

  computed: {
    isFormValid() {
      return (
        this.formData.username.trim() &&
        this.formData.password.trim() &&
        this.formData.confirmPassword.trim() &&
        this.formData.agreement
      )
    }
  },

  watch: {
    loading: {
      immediate: true,
      handler(val) {
        this.isLoading = val
      }
    }
  },

  methods: {
    validateField(field) {
      const value = this.formData[field]
      this.errors[field] = ''

      switch (field) {
        case 'username':
          if (!value || !value.trim()) {
            this.errors[field] = '请输入账号'
            return false
          }
          if (value.length < 2 || value.length > 20) {
            this.errors[field] = '账号长度应为2-20位字符'
            return false
          }
          break

        case 'password':
          if (!value || !value.trim()) {
            this.errors[field] = '请输入密码'
            return false
          }
          if (value.length < 6 || value.length > 20) {
            this.errors[field] = '密码长度应为6-20位'
            return false
          }
          if (this.formData.confirmPassword && value !== this.formData.confirmPassword) {
            this.errors.confirmPassword = '两次输入的密码不一致'
          }
          break

        case 'confirmPassword':
          if (!value || !value.trim()) {
            this.errors[field] = '请确认密码'
            return false
          }
          if (value !== this.formData.password) {
            this.errors[field] = '两次输入的密码不一致'
            return false
          }
          break

        case 'agreement':
          if (!value) {
            this.errors[field] = '请阅读并同意用户协议和隐私政策'
            return false
          }
          break
      }

      return true
    },

    validateForm() {
      const fields = ['username', 'password', 'confirmPassword', 'agreement']
      let isValid = true

      fields.forEach(field => {
        if (!this.validateField(field)) {
          isValid = false
        }
      })

      return isValid
    },

    togglePassword() {
      this.showPassword = !this.showPassword
    },

    toggleConfirmPassword() {
      this.showConfirmPassword = !this.showConfirmPassword
    },

    toggleAgreement() {
      this.formData.agreement = !this.formData.agreement
      if (this.formData.agreement) {
        this.errors.agreement = ''
      }
    },

    handleSubmit() {
      if (!this.validateForm()) {
        uni.showToast({
          title: '请检查输入信息',
          icon: 'none'
        })
        return
      }

      this.$emit('submit', {
        username: this.formData.username.trim(),
        password: this.formData.password
      })
    },

    onViewAgreement() {
      this.$emit('view-agreement')
    },

    onViewPrivacy() {
      this.$emit('view-privacy')
    },

    onLogin() {
      this.$emit('login')
    },

    resetForm() {
      this.formData = {
        username: '',
        password: '',
        confirmPassword: '',
        agreement: false
      }
      this.errors = {
        username: '',
        password: '',
        confirmPassword: '',
        agreement: ''
      }
      this.showPassword = false
      this.showConfirmPassword = false
    }
  }
}
</script>

<style lang="scss">
.register-form-container {
  width: 100%;
}

.form-body {
  width: 100%;
}

.form-item {
  margin-bottom: $uni-md-space-lg;
  position: relative;

  &.has-error {
    .form-input {
      border-color: $uni-color-error;
    }
  }

  &.agreement-item {
    margin-bottom: $uni-md-space-xl;
  }
}

.form-label {
  display: block;
  font-size: $uni-font-size-base;
  font-weight: 500;
  color: $uni-md-text-primary;
  margin-bottom: $uni-md-space-sm;
}

.form-input {
  width: 100%;
  height: 96rpx;
  padding: 0 $uni-md-space-md;
  background-color: $uni-md-surface;
  border: 1px solid $uni-md-border;
  border-radius: $uni-md-radius-medium;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  box-sizing: border-box;
  transition: all $uni-md-animation-fast ease;

  &:focus {
    border-color: $uni-md-color-primary;
    box-shadow: 0 0 0 2rpx rgba($uni-md-color-primary, 0.1);
  }

  &::placeholder {
    color: $uni-md-text-tertiary;
  }
}

.password-toggle {
  position: absolute;
  right: $uni-md-space-md;
  top: 80rpx;
  padding: $uni-md-space-xs;
}

.toggle-icon {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.error-text {
  display: block;
  font-size: $uni-font-size-sm;
  color: $uni-color-error;
  margin-top: $uni-md-space-xs;
}

.agreement-wrapper {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid $uni-md-border;
  border-radius: $uni-md-radius-small;
  margin-right: $uni-md-space-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $uni-md-animation-fast ease;
  flex-shrink: 0;
  margin-top: 4rpx;

  &.checked {
    background-color: $uni-md-color-primary;
    border-color: $uni-md-color-primary;
  }
}

.check-icon {
  font-size: 20rpx;
  color: white;
  font-weight: bold;
}

.agreement-text {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
  line-height: 1.6;
  flex: 1;
}

.agreement-link {
  color: $uni-md-color-primary;
  cursor: pointer;

  &:active {
    opacity: 0.7;
  }
}

.submit-btn {
  width: 100%;
  height: 96rpx;
  background-color: $uni-md-color-primary;
  color: white;
  border: none;
  border-radius: $uni-md-radius-medium;
  font-size: $uni-font-size-lg;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $uni-md-shadow-sm;
  transition: all $uni-md-animation-fast ease;

  &:active {
    transform: scale(0.98);
    box-shadow: $uni-md-shadow-sm;
  }

  &[disabled] {
    background-color: $uni-md-text-disabled;
    box-shadow: none;
  }

  &::after {
    border: none;
  }
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $uni-md-space-sm;
}

.loading-spinner {
  width: 32rpx;
  height: 32rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
  border-top: 4rpx solid white;
  border-radius: 50%;
  animation: spin $uni-md-animation-normal linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.form-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: $uni-md-space-xl;
  gap: $uni-md-space-xs;
}

.footer-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
}

.login-link {
  font-size: $uni-font-size-base;
  color: $uni-md-color-primary;
  font-weight: 500;
  cursor: pointer;

  &:active {
    opacity: 0.7;
  }
}
</style>
