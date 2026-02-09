<template>
  <view class="page">
    <view class="content">
      <!-- 管理员快捷入口 -->
      <view v-if="isAdmin" class="admin-section">
        <view class="section-header">
          <text class="section-title">管理员功能</text>
        </view>
        <wd-cell-group>
          <wd-cell
            v-for="(item, index) in adminMenuItems"
            :key="index"
            :title="item.text"
            is-link
            @click="onMenuClick(item)"
          />
        </wd-cell-group>
      </view>
    </view>
  </view>
</template>

<script>
import { getStorageKey } from '@/config/index.js'

/**
 * 首页
 * @description 系统首页
 */
export default {
  data() {
    return {
      /** @type {Object} 用户信息 */
      userInfo: {}
    }
  },

  computed: {
    /**
     * 判断当前用户是否为管理员
     * @returns {boolean}
     */
    isAdmin() {
      return this.userInfo && this.userInfo.role === 'admin'
    },

    /**
     * 管理员菜单项
     * @returns {Array}
     */
    adminMenuItems() {
      return [
        { text: '用户管理', key: 'userManagement' },
        { text: '部门管理', key: 'deptManagement' },
        { text: '设备管理', key: 'deviceManagement' }
      ]
    }
  },

  onShow() {
    this.loadUserInfo()
  },

  methods: {
    /**
     * 加载用户信息
     */
    loadUserInfo() {
      const userInfo = uni.getStorageSync(getStorageKey('user_info'))
      this.userInfo = userInfo || {}
    },

    /**
     * 菜单点击事件
     * @param {Object} item - 菜单项
     */
    onMenuClick(item) {
      if (item.key === 'userManagement') {
        this.onUserManagement()
      } else if (item.key === 'deptManagement') {
        this.onDeptManagement()
      } else if (item.key === 'deviceManagement') {
        this.onDeviceManagement()
      }
    },

    /**
     * 跳转到用户管理页面
     */
    onUserManagement() {
      uni.navigateTo({
        url: '/pages/admin/user/index'
      })
    },

    /**
     * 跳转到部门管理页面
     */
    onDeptManagement() {
      uni.navigateTo({
        url: '/pages/admin/dept/index'
      })
    },

    /**
     * 跳转到设备管理页面
     */
    onDeviceManagement() {
      uni.navigateTo({
        url: '/pages/admin/device/index'
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
  padding: 32rpx;
}

.admin-section {
  margin-top: 32rpx;
}

.section-header {
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: $uni-text-color;
}
</style>
