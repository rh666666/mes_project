<template>
  <view class="register-form-container">
    <view class="form-body">
      <FormItem
        label="账号"
        :has-error="!!errors.username"
        :error-message="errors.username"
      >
        <FormInput
          v-model="formData.username"
          type="text"
          placeholder="请输入账号（2-20位字符）"
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
          placeholder="请输入密码（6-20位）"
          :has-error="!!errors.password"
          @blur="validateField('password')"
        />
      </FormItem>

      <FormItem
        label="确认密码"
        :has-error="!!errors.confirmPassword"
        :error-message="errors.confirmPassword"
      >
        <PasswordInput
          v-model="formData.confirmPassword"
          placeholder="请再次输入密码"
          :has-error="!!errors.confirmPassword"
          @blur="validateField('confirmPassword')"
        />
      </FormItem>

      <view class="form-item agreement-item" :class="{ 'has-error': errors.agreement }">
        <view class="agreement-wrapper">
          <Checkbox v-model="formData.agreement" @change="onAgreementChange">
            <view class="agreement-text">
              <text>我已阅读并同意</text>
              <text class="agreement-link" @click.stop="onViewAgreement">《用户协议》</text>
              <text>和</text>
              <text class="agreement-link" @click.stop="onViewPrivacy">《隐私政策》</text>
            </view>
          </Checkbox>
        </view>
        <text v-if="errors.agreement" class="error-text">{{ errors.agreement }}</text>
      </view>

      <SubmitButton
        text="注册"
        :loading="isLoading"
        :disabled="!isFormValid"
        @click="handleSubmit"
      />

      <view class="form-footer">
        <text class="footer-text">已有账号？</text>
        <text class="login-link" @click="onLogin">立即登录</text>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 注册表单组件
 * 使用基础UI组件构建的注册表单
 */

import FormItem from '@/components/ui/FormItem.vue'
import FormInput from '@/components/ui/FormInput.vue'
import PasswordInput from '@/components/ui/PasswordInput.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import SubmitButton from '@/components/ui/SubmitButton.vue'

export default {
  name: 'RegisterForm',

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
        confirmPassword: '',
        agreement: false
      },
      errors: {
        username: '',
        password: '',
        confirmPassword: '',
        agreement: ''
      },
      isLoading: false
    }
  },

  computed: {
    isFormValid() {
      return (
        (this.formData.username || '').trim() &&
        (this.formData.password || '').trim() &&
        (this.formData.confirmPassword || '').trim() &&
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

    onAgreementChange(value) {
      if (value) {
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

.agreement-item {
  margin-bottom: $uni-md-space-xl;

  &.has-error {
    :deep(.checkbox) {
      border-color: $uni-color-error;
    }
  }
}

.agreement-wrapper {
  display: flex;
  align-items: flex-start;
}

.agreement-text {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
  line-height: 1.6;
  flex: 1;
  margin-left: $uni-md-space-sm;
}

.agreement-link {
  color: $uni-md-color-primary;
  cursor: pointer;

  &:active {
    opacity: 0.7;
  }
}

.error-text {
  display: block;
  font-size: $uni-font-size-sm;
  color: $uni-color-error;
  margin-top: $uni-md-space-xs;
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
