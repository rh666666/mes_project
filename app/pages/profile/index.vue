<template>
  <view class="page">
    <view class="content">
      <!-- 用户信息卡片 -->
      <view class="user-card" @click="onUserCardClick">
        <image
          v-if="userInfo.avatar"
          class="user-avatar-img"
          :src="getAvatarUrl(userInfo.avatar)"
          mode="aspectFill"
        />
        <view v-else class="user-avatar">
          <text class="avatar-text">{{ displayName.charAt(0).toUpperCase() }}</text>
        </view>
        <view class="user-info">
          <text class="user-name">{{ displayName }}</text>
          <text class="user-role">{{ displayRole }}</text>
        </view>
        <view class="user-arrow" v-if="!isLoggedIn">
          <text class="arrow-icon">></text>
        </view>
      </view>

      <!-- 功能菜单 -->
      <MenuList :menu-items="menuItems" @item-click="onMenuClick" />

      <!-- 退出登录菜单 -->
      <view v-if="isLoggedIn" class="logout-section">
        <MenuList :menu-items="logoutMenuItems" @item-click="onLogoutMenuClick" />
      </view>
    </view>

    <!-- 退出登录确认弹窗 -->
    <MaterialDialog
      :visible="logoutDialogVisible"
      title="提示"
      content="确定要退出登录吗？"
      confirm-text="确定"
      cancel-text="取消"
      @confirm="onLogoutConfirm"
      @cancel="onLogoutCancel"
    />
  </view>
</template>

<script>
  import MenuList from '@/components/MenuList.vue';
  import MaterialDialog from '@/components/MaterialDialog.vue';
  import authApi from '@/api/auth.js';
  import { getStorageKey, getApiBaseURL } from '@/config/index.js';

  export default {
    components: {
      MenuList,
      MaterialDialog
    },
    data() {
      return {
        isLoggedIn: false,
        userInfo: {},
        logoutDialogVisible: false
      };
    },
    computed: {
      menuItems() {
        const items = [
          { text: '设置', key: 'settings' },
          { text: '关于', key: 'about' }
        ];
        return items;
      },
      logoutMenuItems() {
        return [
          { text: '退出登录', key: 'logout', textClass: 'danger' }
        ];
      },
      displayName() {
        if (!this.isLoggedIn) return '未登录';
        return this.userInfo.name || '未设置昵称';
      },
      displayRole() {
        if (!this.isLoggedIn) return '请点击登录';
        return this.userInfo.signature || '已登录';
      }
    },
    onShow() {
      this.checkLoginStatus();
    },
    methods: {
      async checkLoginStatus() {
        const token = uni.getStorageSync(getStorageKey('access_token'));
        let userInfo = uni.getStorageSync(getStorageKey('user_info'));
        this.isLoggedIn = !!token;
        
        if (this.isLoggedIn && !userInfo) {
          // 有token但没有用户信息，尝试获取
          try {
            const res = await authApi.getProfile();
            if (res.code === 2000) {
              userInfo = {
                id: res.data.id,
                username: res.data.username,
                name: res.data.name,
                avatar: res.data.avatar,
                signature: res.data.signature
              };
              uni.setStorageSync(getStorageKey('user_info'), userInfo);
            }
          } catch (error) {
            console.error('获取个人信息失败:', error);
          }
        }
        
        this.userInfo = userInfo || {};
      },
      getAvatarUrl(avatar) {
        if (!avatar) return '';
        if (avatar.startsWith('http')) return avatar;
        return getApiBaseURL() + avatar;
      },
      onUserCardClick() {
        if (this.isLoggedIn) {
          uni.navigateTo({
            url: '/pages/profile/detail'
          });
        } else {
          this.goToLogin();
        }
      },
      goToLogin() {
        uni.navigateTo({
          url: '/pages/login/index'
        });
      },
      onMenuClick(item) {
        switch (item.key) {
          case 'settings':
            this.onSettings();
            break;
          case 'about':
            this.onAbout();
            break;
        }
      },
      onLogoutMenuClick(item) {
        if (item.key === 'logout') {
          this.logoutDialogVisible = true;
        }
      },
      onLogoutConfirm() {
        this.logoutDialogVisible = false;
        this.performLogout();
      },
      onLogoutCancel() {
        this.logoutDialogVisible = false;
      },
      async performLogout() {
        try {
          await authApi.logout();
        } catch (error) {
          console.error('注销请求失败:', error);
        }

        uni.removeStorageSync(getStorageKey('access_token'));
        uni.removeStorageSync(getStorageKey('refresh_token'));
        uni.removeStorageSync(getStorageKey('csrf_token'));
        uni.removeStorageSync(getStorageKey('user_info'));

        this.isLoggedIn = false;
        this.userInfo = {};

        uni.showToast({
          title: '已退出登录',
          icon: 'success'
        });
      },
      onSettings() {
        uni.showToast({
          title: '设置功能开发中',
          icon: 'none'
        });
      },
      onAbout() {
        uni.showToast({
          title: '关于功能开发中',
          icon: 'none'
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
    padding: $uni-md-space-md;
  }

  .user-card {
    display: flex;
    align-items: center;
    background-color: $uni-md-surface;
    border-radius: $uni-md-radius-large;
    padding: $uni-md-space-xl;
    margin-bottom: $uni-md-space-lg;
    box-shadow: $uni-md-shadow-sm;
  }

  .user-avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    background-color: $uni-md-color-primary;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: $uni-md-space-lg;
  }

  .user-avatar-img {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    margin-right: $uni-md-space-lg;
    background-color: $uni-md-surface;
  }

  .avatar-text {
    font-size: $uni-font-size-lg;
    color: white;
    font-weight: 500;
  }

  .user-info {
    flex: 1;
  }

  .user-name {
    display: block;
    font-size: $uni-font-size-lg;
    font-weight: 600;
    color: $uni-md-text-primary;
    margin-bottom: $uni-md-space-xs;
  }

  .user-role {
    display: block;
    font-size: $uni-font-size-base;
    color: $uni-md-text-secondary;
  }

  .user-arrow {
    padding: $uni-md-space-sm;
  }

  .arrow-icon {
    font-size: $uni-font-size-lg;
    color: $uni-md-text-tertiary;
  }

  .logout-section {
    margin-top: $uni-md-space-xl;

    :deep(.menu-list) {
      width: 100%;
    }
  }
</style>
