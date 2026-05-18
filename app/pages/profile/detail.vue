<template>
  <view class="page">
    <view class="content">
      <!-- 头像区域 -->
      <view class="avatar-section" @click="onChangeAvatar">
        <wd-avatar
          v-if="profile.avatar"
          :src="getAvatarUrl(profile.avatar)"
          size="80"
        />
        <wd-avatar v-else :text="profile.name ? profile.name.charAt(0).toUpperCase() : '用'" size="80" />
        <text class="avatar-tip">点击更换头像</text>
      </view>

      <!-- 信息表单 -->
      <wd-form ref="form" :model="formData">
        <wd-cell-group>
          <wd-input v-model="profile.username" label="用户名" disabled />
          <wd-input v-model="formData.name" label="昵称" placeholder="请输入昵称" clearable />
          <wd-input v-model="formData.email" label="邮箱" placeholder="请输入邮箱" clearable />
          <wd-input v-model="formData.phone" label="手机号" placeholder="请输入手机号" type="number" clearable />
        </wd-cell-group>

        <view class="signature-section">
          <text class="signature-label">个性签名</text>
          <wd-textarea
            v-model="formData.signature"
            placeholder="请输入个性签名"
            :maxlength="100"
            show-count
          />
        </view>
      </wd-form>

      <!-- 保存按钮 -->
      <view class="button-section">
        <wd-button type="primary" size="large" block :loading="isLoading" @click="onSave">
          {{ isLoading ? '保存中...' : '保存' }}
        </wd-button>
      </view>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'
import { getStorageKey, getApiBaseURL } from '@/config/index.js'

/**
 * 个人信息编辑页面
 * @description 编辑用户个人信息
 */
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
      showAppLoading({ title: '上传中...' })

      try {
        const res = await authApi.updateAvatar({ avatar: filePath })

        if (res.code === 2000) {
          this.profile.avatar = res.data.avatar || ''
          uni.showToast({
            title: '头像更新成功',
            icon: 'success'
          })

          const userInfo = uni.getStorageSync(getStorageKey('user_info')) || {}
          uni.setStorageSync(getStorageKey('user_info'), {
            ...userInfo,
            avatar: res.data.avatar || ''
          })
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
        hideAppLoading()
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

          const currentUserInfo = uni.getStorageSync(getStorageKey('user_info')) || {}
          uni.setStorageSync(getStorageKey('user_info'), {
            id: res.data.id,
            username: res.data.username,
            name: res.data.name,
            avatar: res.data.avatar,
            signature: res.data.signature,
            role: currentUserInfo.role || res.data.role || 'user'
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

<style lang="scss" scoped>
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: $uni-bg-color;
  box-sizing: border-box;
}

.content {
  flex: 1;
  padding: 24rpx;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 0;
  margin-bottom: 32rpx;
}

.avatar-tip {
  margin-top: 24rpx;
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.signature-section {
  margin: 24rpx 0;
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-radius: 16rpx;
}

.signature-label {
  display: block;
  font-size: 28rpx;
  color: $uni-text-color;
  margin-bottom: 16rpx;
}

.button-section {
  margin-top: 48rpx;
  padding: 0 24rpx;
}

:deep(.button-section .wd-button) {
  width: 100%;
}
</style>
