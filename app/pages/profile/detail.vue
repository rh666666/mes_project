<template>
  <view class="page">
    <view class="content">
      <!-- 头像区域 -->
      <view class="avatar-section" @click="onChangeAvatar">
        <image
          v-if="profile.avatar"
          class="avatar-image"
          :src="getAvatarUrl(profile.avatar)"
          mode="aspectFill"
        />
        <view v-else class="avatar-placeholder">
          <text class="avatar-text">{{ profile.name ? profile.name.charAt(0).toUpperCase() : '用' }}</text>
        </view>
        <text class="avatar-tip">点击更换头像</text>
      </view>

      <!-- 信息表单 -->
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">用户名</text>
          <text class="form-value readonly">{{ profile.username }}</text>
        </view>

        <view class="form-item">
          <text class="form-label">昵称</text>
          <input
            class="form-input"
            v-model="formData.name"
            placeholder="请输入昵称"
          />
        </view>

        <view class="form-item">
          <text class="form-label">邮箱</text>
          <input
            class="form-input"
            v-model="formData.email"
            placeholder="请输入邮箱"
            type="email"
          />
        </view>

        <view class="form-item">
          <text class="form-label">手机号</text>
          <input
            class="form-input"
            v-model="formData.phone"
            placeholder="请输入手机号"
            type="number"
            maxlength="11"
          />
        </view>

        <view class="form-item signature-item">
          <text class="form-label">个性签名</text>
          <textarea
            class="form-textarea"
            v-model="formData.signature"
            placeholder="请输入个性签名"
            maxlength="100"
            auto-height
          />
        </view>
      </view>

      <!-- 保存按钮 -->
      <button
        class="save-btn"
        :class="{ loading: isLoading }"
        :disabled="isLoading"
        @click="onSave"
      >
        <text v-if="!isLoading">保存</text>
        <view v-else class="loading-wrapper">
          <view class="loading-spinner"></view>
          <text>保存中...</text>
        </view>
      </button>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth.js'
import { getStorageKey, getApiBaseURL } from '@/config/index.js'

export default {
  data() {
    return {
      profile: {
        id: null,
        username: '',
        name: '',
        email: '',
        phone: '',
        avatar: null,
        signature: ''
      },
      formData: {
        name: '',
        email: '',
        phone: '',
        signature: ''
      },
      isLoading: false,
      avatarFile: null
    }
  },

  onLoad() {
    this.loadProfile()
  },

  onShow() {
    // 从本地存储加载最新的用户信息
    const userInfo = uni.getStorageSync(getStorageKey('user_info'))
    if (userInfo) {
      this.profile.username = userInfo.username || this.profile.username
      this.profile.name = userInfo.name || this.profile.name
      this.profile.avatar = userInfo.avatar || this.profile.avatar
      this.profile.signature = userInfo.signature || this.profile.signature
      
      this.formData.name = userInfo.name || this.formData.name
      this.formData.signature = userInfo.signature || this.formData.signature
    }
  },



  methods: {
    async loadProfile() {
      try {
        const res = await authApi.getProfile()
        if (res.code === 2000) {
          this.profile = res.data
          this.formData.name = res.data.name || ''
          this.formData.email = res.data.email || ''
          this.formData.phone = res.data.phone || ''
          this.formData.signature = res.data.signature || ''
        }
      } catch (error) {
        console.error('获取个人信息失败:', error)
        uni.showToast({
          title: '获取信息失败',
          icon: 'none'
        })
      }
    },

    getAvatarUrl(avatar) {
      if (!avatar) return ''
      if (avatar.startsWith('http')) return avatar
      return getApiBaseURL() + avatar
    },

    onChangeAvatar() {
      uni.showActionSheet({
        itemList: ['从相册选择', '拍照'],
        success: (res) => {
          const sourceType = res.tapIndex === 0 ? ['album'] : ['camera']
          uni.chooseImage({
            count: 1,
            sourceType: sourceType,
            success: (chooseRes) => {
              const tempFilePath = chooseRes.tempFilePaths[0]
              this.updateAvatar(tempFilePath)
            }
          })
        }
      })
    },

    async updateAvatar(filePath) {
      uni.showLoading({ title: '上传中...' })
      
      try {
        const res = await authApi.updateAvatar({ avatar: filePath })
        
        if (res.code === 2000) {
          this.profile.avatar = res.data.avatar || ''
          uni.showToast({
            title: '头像更新成功',
            icon: 'success'
          })

          // 更新本地存储
          const userInfo = uni.getStorageSync(getStorageKey('user_info')) || {}
          userInfo.avatar = res.data.avatar || ''
          uni.setStorageSync(getStorageKey('user_info'), userInfo)
        } else {
          uni.showToast({
            title: res.msg || '头像更新失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('更新头像失败:', error)
        uni.showToast({
          title: error.msg || '头像更新失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },

    async onSave() {
      this.isLoading = true

      try {
        const res = await authApi.updateUserInfo({
          name: this.formData.name,
          email: this.formData.email,
          phone: this.formData.phone,
          signature: this.formData.signature
        })

        if (res.code === 2000) {
          uni.showToast({
            title: '保存成功',
            icon: 'success'
          })

          this.profile = res.data

          // 根据API响应更新本地存储
          uni.setStorageSync(getStorageKey('user_info'), {
            id: res.data.id,
            username: res.data.username,
            name: res.data.name,
            avatar: res.data.avatar,
            signature: res.data.signature
          })
        } else {
          uni.showToast({
            title: res.msg || '保存失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('保存个人信息失败:', error)
        uni.showToast({
          title: error.msg || '保存失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
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

.content {
  flex: 1;
  padding: $uni-md-space-md;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $uni-md-space-xl 0;
  margin-bottom: $uni-md-space-lg;
}

.avatar-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background-color: $uni-md-surface;
}

.avatar-placeholder {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background-color: $uni-md-color-primary;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 64rpx;
  color: white;
  font-weight: 500;
}

.avatar-tip {
  margin-top: $uni-md-space-md;
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.form-section {
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-large;
  box-shadow: $uni-md-shadow-sm;
  overflow: hidden;
  margin-bottom: $uni-md-space-xl;
}

.form-item {
  display: flex;
  align-items: center;
  padding: $uni-md-space-md $uni-md-space-lg;
  border-bottom: 1px solid $uni-md-divider;

  &:last-child {
    border-bottom: none;
  }

  &.signature-item {
    align-items: flex-start;
    padding-top: $uni-md-space-lg;
    padding-bottom: $uni-md-space-lg;
  }
}

.form-label {
  width: 140rpx;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  font-weight: 500;
}

.form-value {
  flex: 1;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;

  &.readonly {
    color: $uni-md-text-secondary;
  }
}

.form-input {
  flex: 1;
  height: 72rpx;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;

  &::placeholder {
    color: $uni-md-text-tertiary;
  }
}

.form-textarea {
  flex: 1;
  min-height: 80rpx;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  line-height: 1.5;

  &::placeholder {
    color: $uni-md-text-tertiary;
  }
}

.save-btn {
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
</style>
