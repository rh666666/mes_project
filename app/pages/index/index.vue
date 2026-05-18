<template>
  <view class="page">
    <view class="content">
      <wd-card class="welcome-card">
        <view class="welcome-card__body">
          <text class="welcome-card__greeting">{{ greetingText }}</text>
          <text class="welcome-card__hint">请选择下方功能开始作业</text>
        </view>
      </wd-card>

      <view class="feature-section">
        <view class="section-header">
          <text class="section-title">生产作业</text>
        </view>
        <wd-card
          v-for="item in menuItems"
          :key="item.key"
          class="feature-card"
          @click="onMenuClick(item)"
        >
          <view class="feature-card__body">
            <view class="feature-card__main">
              <text class="feature-card__title">{{ item.text }}</text>
              <text class="feature-card__desc">{{ item.desc }}</text>
            </view>
            <wd-icon name="arrow-right" size="16" color="#969799" />
          </view>
        </wd-card>
      </view>
    </view>
  </view>
</template>

<script>
import { getStorageKey } from '@/config/index.js'
import { applyTabBarByRole } from '@/utils/tab-bar.js'

/**
 * 首页
 * @description 员工生产作业入口：抢单中心、我的工单、报工记录（每项独立卡片）
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
     * 问候语
     * @returns {string}
     */
    greetingText() {
      const name = this.userInfo.name || this.userInfo.username
      if (name) {
        return `你好，${name}`
      }
      return '你好'
    },

    /**
     * 功能入口菜单
     * @returns {Array<{key:string,text:string,desc:string,url:string}>}
     */
    menuItems() {
      return [
        {
          key: 'grabCenter',
          text: '抢单中心',
          desc: '查看并抢取待派工的工序工单',
          url: '/pages/work-order/grab-center/index'
        },
        {
          key: 'myOrders',
          text: '我的工单',
          desc: '查看已接单或进行中的工单',
          url: '/pages/work-order/my-orders/index'
        },
        {
          key: 'reportList',
          text: '报工记录',
          desc: '查看历史生产报工记录',
          url: '/pages/work-order/report-list/index'
        }
      ]
    }
  },

  onShow() {
    this.loadUserInfo()
    this.$nextTick(() => {
      applyTabBarByRole(this.userInfo)
    })
  },

  methods: {
    /**
     * 从本地存储加载用户信息
     * @returns {void}
     */
    loadUserInfo() {
      const userInfo = uni.getStorageSync(getStorageKey('user_info'))
      this.userInfo = userInfo || {}
    },

    /**
     * 菜单点击跳转
     * @param {{url?: string}} item - 菜单项
     * @returns {void}
     */
    onMenuClick(item) {
      if (!item || !item.url) {
        return
      }
      uni.navigateTo({
        url: item.url
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

.welcome-card {
  margin: 0 0 32rpx 0;
  width: 100%;
}

:deep(.welcome-card .wd-card) {
  margin: 0;
}

.welcome-card__body {
  padding: 32rpx 24rpx;
}

.welcome-card__greeting {
  display: block;
  font-size: 36rpx;
  font-weight: 600;
  color: $uni-text-color;
  margin-bottom: 12rpx;
}

.welcome-card__hint {
  display: block;
  font-size: 28rpx;
  color: $uni-text-color-grey;
}

.feature-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.section-header {
  padding: 0 8rpx;
}

.section-title {
  font-size: 26rpx;
  font-weight: 500;
  color: $uni-text-color-grey;
}

.feature-card {
  width: 100%;
  margin: 0;
}

:deep(.feature-card .wd-card) {
  margin: 0;
}

.feature-card__body {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 24rpx;
  gap: 24rpx;
}

.feature-card__main {
  flex: 1;
  min-width: 0;
}

.feature-card__title {
  display: block;
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
  margin-bottom: 8rpx;
}

.feature-card__desc {
  display: block;
  font-size: 26rpx;
  color: $uni-text-color-grey;
  line-height: 1.4;
}
</style>
