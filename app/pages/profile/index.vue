<template>
  <view class="page">
    <view class="content">
      <!-- 用户信息卡片 -->
      <wd-card class="profile-user-card" @click="onUserCardClick">
        <view class="profile-user-card__header">
          <wd-avatar
            v-if="userInfo.avatar"
            :src="getAvatarUrl(userInfo.avatar)"
            size="medium"
          />
          <wd-avatar v-else :text="displayName.charAt(0).toUpperCase()" size="medium" />
          <view class="profile-user-card__info">
            <text class="profile-user-card__name">{{ displayName }}</text>
            <text class="profile-user-card__role">{{ displayRole }}</text>
          </view>
          <wd-icon v-if="!isLoggedIn" name="chevron-right" size="24" color="#969799" />
        </view>
      </wd-card>

      <!-- 功能菜单 -->
      <wd-cell-group>
        <wd-cell
          v-for="(item, index) in menuItems"
          :key="index"
          :title="item.text"
          is-link
          @click="onMenuClick(item)"
        />
      </wd-cell-group>

      <!-- 退出登录菜单 -->
      <view v-if="isLoggedIn" class="logout-section">
        <wd-cell-group>
          <wd-cell
            v-for="(item, index) in logoutMenuItems"
            :key="index"
            is-link
            custom-class="logout-cell"
            @click="onLogoutMenuClick(item)"
          >
            <template #title>
              <text class="logout-title">{{ item.text }}</text>
            </template>
          </wd-cell>
        </wd-cell-group>
      </view>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth.js'
import { getStorageKey, getApiBaseURL } from '@/config/index.js'

/**
 * 个人中心页面
 * @description 用户个人中心，展示用户信息和功能菜单
 */
export default {
  data() {
    return {
      isLoggedIn: false,
      userInfo: {}
    }
  },

  computed: {
    menuItems() {
      return [
        { text: '设置', key: 'settings' },
        { text: '关于', key: 'about' }
      ]
    },

    logoutMenuItems() {
      return [
        { text: '退出登录', key: 'logout' }
      ]
    },

    displayName() {
      if (!this.isLoggedIn) return '未登录'
      return this.userInfo.name || '未设置昵称'
    },

    displayRole() {
      if (!this.isLoggedIn) return '请点击登录'
      return this.userInfo.signature || '已登录'
    }
  },

  onShow() {
    this.checkLoginStatus()
  },

  methods: {
    async checkLoginStatus() {
      const token = uni.getStorageSync(getStorageKey('access_token'))
      let userInfo = uni.getStorageSync(getStorageKey('user_info'))
      this.isLoggedIn = !!token

      if (this.isLoggedIn && !userInfo) {
        try {
          const res = await authApi.getProfile()
          if (res.code === 2000) {
            userInfo = {
              id: res.data.id,
              username: res.data.username,
              name: res.data.name,
              avatar: res.data.avatar || '',
              signature: res.data.signature || ''
            }
            uni.setStorageSync(getStorageKey('user_info'), userInfo)
          }
        } catch (error) {
          console.error('获取个人信息失败:', error)
        }
      }

      this.userInfo = userInfo || {}
    },

    getAvatarUrl(avatar) {
      if (!avatar) return ''
      if (avatar.startsWith('http')) return avatar
      return getApiBaseURL() + avatar
    },

    onUserCardClick() {
      if (this.isLoggedIn) {
        uni.navigateTo({
          url: '/pages/profile/detail'
        })
      } else {
        this.goToLogin()
      }
    },

    goToLogin() {
      uni.navigateTo({
        url: '/pages/login/index'
      })
    },

    onMenuClick(item) {
      switch (item.key) {
        case 'settings':
          this.onSettings()
          break
        case 'about':
          this.onAbout()
          break
      }
    },

    onLogoutMenuClick(item) {
      if (item.key === 'logout') {
        this.showLogoutConfirm()
      }
    },

    showLogoutConfirm() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        confirmText: '确定',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.performLogout()
          }
        }
      })
    },

    async performLogout() {
      uni.showLoading({ title: '注销中...' })

      try {
        const res = await authApi.logout()

        if (res.code === 2000) {
          uni.removeStorageSync(getStorageKey('access_token'))
          uni.removeStorageSync(getStorageKey('refresh_token'))
          uni.removeStorageSync(getStorageKey('csrf_token'))
          uni.removeStorageSync(getStorageKey('user_info'))

          this.isLoggedIn = false
          this.userInfo = {}

          uni.showToast({
            title: '已退出登录',
            icon: 'success'
          })
        } else {
          uni.showToast({
            title: res.msg || '注销失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('注销请求失败:', error)
        uni.showToast({
          title: error.msg || '注销失败，请稍后重试',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },

    onSettings() {
      uni.showToast({
        title: '设置功能开发中',
        icon: 'none'
      })
    },

    onAbout() {
      uni.showToast({
        title: '关于功能开发中',
        icon: 'none'
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
  background-color: $uni-bg-color;
  box-sizing: border-box;
}

.content {
  flex: 1;
  padding: 24rpx;
}

.profile-user-card {
  margin: 0 0 32rpx 0;
  width: 100%;
}

:deep(.profile-user-card .wd-card) {
  margin: 0;
}

.profile-user-card__header {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx;
}

.profile-user-card__info {
  flex: 1;
}

.profile-user-card__name {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: $uni-text-color;
  margin-bottom: 8rpx;
}

.profile-user-card__role {
  display: block;
  font-size: 28rpx;
  color: $uni-text-color-grey;
}

.logout-section {
  margin-top: 48rpx;
}

.logout-title {
  color: #ee0a24;
  font-size: 30rpx;
}
</style>
