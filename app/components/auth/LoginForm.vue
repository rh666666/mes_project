<template>
  <view class="login-form-container">
    <view class="form-body">
      <view class="form-item" :class="{ 'has-error': errors.username }">
        <text class="form-label">账号</text>
        <input
          class="form-input"
          type="text"
          v-model="formData.username"
          placeholder="请输入账号"
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
          placeholder="请输入密码"
          @blur="validateField('password')"
        />
        <view class="password-toggle" @click="togglePassword">
          <text class="toggle-icon">{{ showPassword ? '隐藏' : '显示' }}</text>
        </view>
        <text v-if="errors.password" class="error-text">{{ errors.password }}</text>
      </view>

      <view class="form-options">
        <label class="checkbox-wrapper" @click="toggleRemember">
          <view class="checkbox" :class="{ checked: formData.remember }">
            <text v-if="formData.remember" class="check-icon">✓</text>
          </view>
          <text class="checkbox-text">记住我</text>
        </label>
        <text class="forgot-link" @click="onForgotPassword">忘记密码？</text>
      </view>

      <button
        class="submit-btn"
        :class="{ loading: isLoading }"
        :disabled="isLoading || !isFormValid"
        @click="handleSubmit"
      >
        <text v-if="!isLoading">登录</text>
        <view v-else class="loading-wrapper">
          <view class="loading-spinner"></view>
          <text>登录中...</text>
        </view>
      </button>

      <view class="form-footer">
        <text class="footer-text">还没有账号？</text>
        <text class="register-link" @click="onRegister">立即注册</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'LoginForm',

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
        remember: false
      },
      errors: {
        username: '',
        password: ''
      },
      showPassword: false,
      isLoading: false
    }
  },

  computed: {
    isFormValid() {
      return this.formData.username.trim() && this.formData.password.trim()
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

      if (!value || !value.trim()) {
        const fieldNames = {
          username: '账号',
          password: '密码'
        }
        this.errors[field] = `请输入${fieldNames[field]}`
        return false
      }

      if (field === 'password' && value.length < 6) {
        this.errors[field] = '密码长度不能少于6位'
        return false
      }

      return true
    },

    validateForm() {
      const usernameValid = this.validateField('username')
      const passwordValid = this.validateField('password')
      return usernameValid && passwordValid
    },

    togglePassword() {
      this.showPassword = !this.showPassword
    },

    toggleRemember() {
      this.formData.remember = !this.formData.remember
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
        password: this.formData.password,
        remember: this.formData.remember
      })
    },

    onForgotPassword() {
      this.$emit('forgot-password')
    },

    onRegister() {
      this.$emit('register')
    },

    resetForm() {
      this.formData = {
        username: '',
        password: '',
        remember: false
      }
      this.errors = {
        username: '',
        password: ''
      }
      this.showPassword = false
    }
  }
}
</script>

<style lang="scss">
.login-form-container {
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $uni-md-space-xl;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
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

.checkbox-text {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.forgot-link {
  font-size: $uni-font-size-sm;
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

.register-link {
  font-size: $uni-font-size-base;
  color: $uni-md-color-primary;
  font-weight: 500;
  cursor: pointer;

  &:active {
    opacity: 0.7;
  }
}
</style>
