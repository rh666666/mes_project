<template>
  <view class="page">
    <AuthContainer>
      <RegisterForm
        :loading="isLoading"
        @submit="onRegisterSubmit"
        @view-agreement="onViewAgreement"
        @view-privacy="onViewPrivacy"
        @login="goToLogin"
        ref="registerForm"
      />
    </AuthContainer>
  </view>
</template>

<script>
import AuthContainer from '@/components/auth/AuthContainer.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'
import authApi from '@/api/auth.js'

export default {
  components: {
    AuthContainer,
    RegisterForm
  },

  data() {
    return {
      isLoading: false
    }
  },

  methods: {
    async onRegisterSubmit(formData) {
      this.isLoading = true

      try {
        const res = await authApi.register({
          username: formData.username,
          password: formData.password
        })

        if (res.code === 2000) {
          uni.showToast({
            title: '注册成功',
            icon: 'success'
          })

          setTimeout(() => {
            const username = encodeURIComponent(formData.username)
            const password = encodeURIComponent(formData.password)
            uni.redirectTo({
              url: `/pages/login/index?username=${username}&password=${password}`
            })
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
