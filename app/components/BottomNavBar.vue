<template>
  <view class="bottom-nav-bar">
    <view 
      class="nav-item" 
      v-for="(item, index) in navList" 
      :key="index"
      @click="onNavClick(item)"
    >
      <view class="nav-icon-wrapper">
        <text class="nav-icon" :class="{ active: currentPath === item.path }">{{ item.icon }}</text>
      </view>
      <text class="nav-text" :class="{ active: currentPath === item.path }">{{ item.name }}</text>
    </view>
  </view>
</template>

<script>
  export default {
    name: 'BottomNavBar',
    props: {
      currentPath: {
        type: String,
        default: '/pages/index/index'
      }
    },
    data() {
      return {
        navList: [
          {
            name: '首页',
            path: '/pages/index/index',
            icon: '首'
          },
          {
            name: '生产',
            path: '/pages/production/index',
            icon: '产'
          },
          {
            name: '设备',
            path: '/pages/equipment/index',
            icon: '设'
          },
          {
            name: '我的',
            path: '/pages/profile/index',
            icon: '我'
          }
        ]
      };
    },
    methods: {
      onNavClick(item) {
        if (this.currentPath === item.path) {
          return;
        }
        this.$emit('nav-change', item);
        // 使用 reLaunch 切换页面，避免页面堆叠
        uni.reLaunch({
          url: item.path,
          fail: (err) => {
            console.log('页面跳转失败:', err);
            uni.showToast({
              title: `${item.name}功能开发中`,
              icon: 'none'
            });
          }
        });
      }
    }
  };
</script>

<style lang="scss" scoped>
  .bottom-nav-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: space-around;
    height: 100rpx;
    background-color: $uni-bg-color;
    border-top: 1rpx solid $uni-border-color;
    box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
    z-index: 999;
    padding-bottom: env(safe-area-inset-bottom);
  }

  .nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8rpx 0;
  }

  .nav-icon-wrapper {
    margin-bottom: 4rpx;
  }

  .nav-icon {
    font-size: 40rpx;
    line-height: 1;
    opacity: 0.6;
    transition: all 0.3s;
    color: $uni-text-color-grey;
  }

  .nav-icon.active {
    opacity: 1;
    color: $uni-color-primary;
  }

  .nav-text {
    font-size: 22rpx;
    color: $uni-text-color-grey;
    transition: color 0.3s;
  }

  .nav-text.active {
    color: $uni-color-primary;
    font-weight: 500;
  }
</style>