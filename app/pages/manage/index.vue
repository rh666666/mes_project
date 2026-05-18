<template>
  <view class="page">
    <view class="content">
      <!-- 管理员快捷入口 -->
      <view v-if="isAdmin" class="admin-section">
        <view
          v-for="(group, groupIndex) in adminMenuGroups"
          :key="group.key"
          class="menu-group"
        >
          <view class="section-header">
            <text class="section-title module-title">{{ group.title }}</text>
          </view>
          <wd-cell-group border>
            <wd-cell
              v-for="(item, itemIndex) in group.items"
              :key="item.key"
              :title="item.text"
              :border="itemIndex !== group.items.length - 1"
              is-link
              @click="onMenuClick(item)"
            />
          </wd-cell-group>
        </view>
      </view>

      <view v-else class="empty-section">
        <wd-status-tip image="search" tip="暂无可用管理功能" />
      </view>
    </view>
  </view>
</template>

<script>
import { getStorageKey } from '@/config/index.js'
import { applyTabBarByRole } from '@/utils/tab-bar.js'

/**
 * 管理页
 * @description 管理员后台功能入口
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
        { text: '用户管理', key: 'userManagement', url: '/pages/admin/user/index' },
        { text: '部门管理', key: 'deptManagement', url: '/pages/admin/dept/index' },
        { text: '设备管理', key: 'deviceManagement', url: '/pages/admin/device/index' },
        { text: '技能管理', key: 'skillManagement', url: '/pages/admin/skill/index' },
        { text: '单位管理', key: 'unitManagement', url: '/pages/admin/unit/index' },
        { text: '物料管理', key: 'materialManagement', url: '/pages/admin/material/index' },
        { text: '工序管理', key: 'processManagement', url: '/pages/admin/process/index' },
        { text: '工艺路线管理', key: 'processRouteManagement', url: '/pages/admin/process-route/index' },
        { text: 'BOM 管理', key: 'bomManagement', url: '/pages/admin/bom/index' },
        {
          text: '生产任务单管理',
          key: 'productionOrderManagement',
          url: '/pages/admin/work-order/production-order/index'
        },
        {
          text: '工序派工单管理',
          key: 'dispatchOrderManagement',
          url: '/pages/admin/work-order/dispatch-order/index'
        },
        {
          text: '生产报工单管理',
          key: 'productionReportManagement',
          url: '/pages/admin/work-order/production-report/index'
        },
        {
          text: '质检任务单管理',
          key: 'qualityCheckOrderManagement',
          url: '/pages/admin/work-order/quality-check-order/index'
        }
      ]
    },

    /**
     * 管理员菜单分组
     * @returns {Array}
     */
    adminMenuGroups() {
      return [
        {
          key: 'organization',
          title: '组织与人员',
          items: this.adminMenuItems.filter((item) => ['userManagement', 'deptManagement'].includes(item.key))
        },
        {
          key: 'resource',
          title: '资源与能力',
          items: this.adminMenuItems.filter((item) =>
            ['deviceManagement', 'skillManagement', 'unitManagement', 'materialManagement'].includes(item.key)
          )
        },
        {
          key: 'process',
          title: '工艺流程',
          items: this.adminMenuItems.filter((item) =>
            ['processManagement', 'processRouteManagement', 'bomManagement'].includes(item.key)
          )
        },
        {
          key: 'workOrder',
          title: '工单管理',
          items: this.adminMenuItems.filter((item) =>
            [
              'productionOrderManagement',
              'dispatchOrderManagement',
              'productionReportManagement',
              'qualityCheckOrderManagement'
            ].includes(item.key)
          )
        }
      ]
    }
  },

  onShow() {
    this.loadUserInfo()
    applyTabBarByRole(this.userInfo)
    if (!this.isAdmin) {
      uni.showToast({ title: '无权限访问', icon: 'none' })
      uni.switchTab({ url: '/pages/index/index' })
    }
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
  padding: 32rpx;
}

.admin-section {
  margin-top: 8rpx;
}

.menu-group {
  margin-top: 20rpx;
  padding: 20rpx;
  border-radius: 16rpx;
  background-color: #ffffff;
}

.section-header {
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 26rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.module-title {
  font-weight: 400;
  color: $uni-text-color-grey;
}

.empty-section {
  margin-top: 40rpx;
  padding: 28rpx 20rpx;
  border-radius: 16rpx;
  background-color: #ffffff;
}
</style>
