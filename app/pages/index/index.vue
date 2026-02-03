<template>
  <view class="page">
    <view class="content">
      <!-- 管理员快捷入口 -->
      <view v-if="isAdmin" class="admin-section">
        <view class="section-header">
          <text class="section-title">管理员功能</text>
        </view>
        <MenuList :menu-items="adminMenuItems" @item-click="onMenuClick" />
      </view>
    </view>
  </view>
</template>

<script>
import MenuList from '@/components/MenuList.vue';
import { getStorageKey } from '@/config/index.js';

/**
 * 首页
 * @description 系统首页
 */
export default {
  components: {
    MenuList
  },

  data() {
    return {
      /** @type {Object} 用户信息 */
      userInfo: {}
    };
  },

  computed: {
    /**
     * 判断当前用户是否为管理员
     * @returns {boolean}
     */
    isAdmin() {
      return this.userInfo && this.userInfo.role === 'admin';
    },

    /**
     * 管理员菜单项
     * @returns {Array}
     */
    adminMenuItems() {
      return [
        { text: '用户管理', key: 'userManagement' }
      ];
    }
  },

  onShow() {
    this.loadUserInfo();
  },

  methods: {
    /**
     * 加载用户信息
     */
    loadUserInfo() {
      const userInfo = uni.getStorageSync(getStorageKey('user_info'));
      this.userInfo = userInfo || {};
    },

    /**
     * 菜单点击事件
     * @param {Object} item - 菜单项
     */
    onMenuClick(item) {
      if (item.key === 'userManagement') {
        this.onUserManagement();
      }
    },

    /**
     * 跳转到用户管理页面
     */
    onUserManagement() {
      uni.navigateTo({
        url: '/pages/admin/user-management'
      });
    }
  }
};
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
  padding: $uni-md-space-lg;
}

.admin-section {
  margin-top: $uni-md-space-lg;
}

.section-header {
  margin-bottom: $uni-md-space-md;
}

.section-title {
  font-size: $uni-font-size-lg;
  font-weight: 600;
  color: $uni-md-text-primary;
}
</style>
