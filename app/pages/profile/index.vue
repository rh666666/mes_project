<template>
  <view class="page">
    <view class="content">
      <!-- 用户信息卡片 -->
      <Card
        class="profile-user-card"
        variant="elevated"
        :clickable="true"
        @click="onUserCardClick"
      >
        <template #header>
          <view class="profile-user-card__header">
            <image
              v-if="userInfo.avatar"
              class="profile-user-card__avatar"
              :src="getAvatarUrl(userInfo.avatar)"
              mode="aspectFill"
            />
            <view v-else class="profile-user-card__avatar profile-user-card__avatar--placeholder">
              <text class="profile-user-card__avatar-text">{{ displayName.charAt(0).toUpperCase() }}</text>
            </view>
            <view class="profile-user-card__info">
              <text class="profile-user-card__name">{{ displayName }}</text>
              <text class="profile-user-card__role">{{ displayRole }}</text>
            </view>
            <view v-if="!isLoggedIn" class="profile-user-card__arrow">
              <MdIcon type="chevron_right" :size="24" :color="iconColor" />
            </view>
          </view>
        </template>
      </Card>

      <!-- 功能菜单 -->
      <List class="menu-list-wrapper">
        <ListItem
          v-for="(item, index) in menuItems"
          :key="index"
          :clickable="true"
          :has-divider="index < menuItems.length - 1"
          @click="onMenuClick(item)"
        >
          <template #headline>
            <text class="menu-text">{{ item.text }}</text>
          </template>
          <template #end>
            <text class="menu-arrow">></text>
          </template>
        </ListItem>
      </List>

      <!-- 退出登录菜单 -->
      <view v-if="isLoggedIn" class="logout-section">
        <List class="menu-list-wrapper">
          <ListItem
            v-for="(item, index) in logoutMenuItems"
            :key="index"
            :clickable="true"
            :has-divider="index < logoutMenuItems.length - 1"
            @click="onLogoutMenuClick(item)"
          >
            <template #headline>
              <text class="menu-text" :class="item.textClass">{{ item.text }}</text>
            </template>
            <template #end>
              <text class="menu-arrow">></text>
            </template>
          </ListItem>
        </List>
      </view>
    </view>

    <!-- 退出登录确认弹窗 -->
    <Dialog
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
  import List from '@/components/ui/md3/List.vue';
  import ListItem from '@/components/ui/md3/ListItem.vue';
  import Dialog from '@/components/ui/md3/Dialog.vue';
  import Card from '@/components/ui/md3/Card.vue';
  import MdIcon from '@/components/ui/MdIcon.vue';
  import authApi from '@/api/auth.js';
  import { getStorageKey, getApiBaseURL } from '@/config/index.js';

  export default {
    components: {
      List,
      ListItem,
      Dialog,
      Card,
      MdIcon
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
      },
      iconColor() {
        return '#6E6E73';
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
                avatar: res.data.avatar || '',
                signature: res.data.signature || ''
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
        uni.showLoading({ title: '注销中...' });

        try {
          const res = await authApi.logout();

          if (res.code === 2000) {
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
          } else {
            uni.showToast({
              title: res.msg || '注销失败',
              icon: 'none'
            });
          }
        } catch (error) {
          console.error('注销请求失败:', error);
          uni.showToast({
            title: error.msg || '注销失败，请稍后重试',
            icon: 'none'
          });
        } finally {
          uni.hideLoading();
        }
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

  .profile-user-card {
    margin-bottom: $uni-md-space-lg;

    :deep(.md3-card__header) {
      padding: $uni-md-space-xl;
    }
  }

  .profile-user-card__header {
    display: flex;
    align-items: center;
    gap: $uni-md-space-lg;
  }

  .profile-user-card__avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    background-color: $uni-md-surface;
  }

  .profile-user-card__avatar--placeholder {
    background-color: $uni-md-color-primary;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .profile-user-card__avatar-text {
    font-size: $uni-font-size-lg;
    color: $uni-md-surface;
    font-weight: 500;
  }

  .profile-user-card__info {
    flex: 1;
  }

  .profile-user-card__name {
    display: block;
    font-size: $uni-font-size-lg;
    font-weight: 600;
    color: $uni-md-text-primary;
    margin-bottom: $uni-md-space-xs;
  }

  .profile-user-card__role {
    display: block;
    font-size: $uni-font-size-base;
    color: $uni-md-text-secondary;
  }

  .profile-user-card__arrow {
    padding: $uni-md-space-sm;
  }

  .logout-section {
    margin-top: $uni-md-space-xl;
  }

  .menu-list-wrapper {
    margin-bottom: $uni-md-space-lg;
  }

  .menu-text {
    font-size: $uni-font-size-base;
    color: $uni-md-text-primary;

    &.danger {
      color: $uni-color-error;
    }
  }

  .menu-arrow {
    font-size: $uni-font-size-base;
    color: $uni-md-text-tertiary;
  }
</style>
