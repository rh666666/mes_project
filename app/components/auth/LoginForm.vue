<template>
  <view class="login-form-container">
    <view class="form-body">
      <FormItem
        label="账号"
        :has-error="!!errors.username"
        :error-message="errors.username"
      >
        <FormInput
          v-model="formData.username"
          type="text"
          placeholder="请输入账号"
          :has-error="!!errors.username"
          @blur="validateField('username')"
        />
      </FormItem>

      <FormItem
        label="密码"
        :has-error="!!errors.password"
        :error-message="errors.password"
      >
        <PasswordInput
          v-model="formData.password"
          placeholder="请输入密码"
          :has-error="!!errors.password"
          @blur="validateField('password')"
        />
      </FormItem>

      <view class="form-options">
        <Checkbox v-model="formData.remember" label="记住我" />
        <text class="forgot-link" @click="onForgotPassword">忘记密码？</text>
      </view>

      <SubmitButton
        text="登录"
        :loading="isLoading"
        :disabled="!isFormValid"
        @click="handleSubmit"
      />

      <view class="form-footer">
        <text class="footer-text">还没有账号？</text>
        <text class="register-link" @click="onRegister">立即注册</text>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 登录表单组件
 * 使用基础UI组件构建的登录表单
 */

import FormItem from '@/components/ui/FormItem.vue'
import FormInput from '@/components/ui/FormInput.vue'
import PasswordInput from '@/components/ui/PasswordInput.vue'
import Checkbox from '@/components/ui/md3/Checkbox.vue'
import SubmitButton from '@/components/ui/SubmitButton.vue'

export default {
  name: 'LoginForm',

  components: {
    FormItem,
    FormInput,
    PasswordInput,
    Checkbox,
    SubmitButton
  },

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
      isLoading: false
    }
  },

  computed: {
    isFormValid() {
      return (this.formData.username || '').trim() && (this.formData.password || '').trim()
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $uni-md-space-xl;
}

.forgot-link {
  font-size: $uni-font-size-sm;
  color: $uni-md-color-primary;
  cursor: pointer;

  &:active {
    opacity: 0.7;
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
