<template>
  <view class="bottom-nav-bar">
    <view 
      class="nav-item" 
      v-for="(item, index) in navList" 
      :key="index"
      :class="{ active: currentPath === item.path }"
      @click="onNavClick(item)"
    >
      <view class="nav-icon-wrapper">
        <text class="nav-icon">{{ item.icon }}</text>
      </view>
      <text class="nav-text">{{ item.name }}</text>
      <view class="nav-indicator" v-if="currentPath === item.path"></view>
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
    background-color: $uni-md-surface;
    border-top: 1rpx solid $uni-md-divider;
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
    position: relative;
    cursor: pointer;
    transition: all $uni-md-animation-fast ease;

    &:active {
      transform: scale(0.98);
    }

    &.active {
      .nav-icon {
        transform: translateY(-4rpx);
        color: $uni-md-color-primary;
        opacity: 1;
      }

      .nav-text {
        color: $uni-md-color-primary;
        font-weight: 500;
      }
    }
  }

  .nav-icon-wrapper {
    margin-bottom: 4rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .nav-icon {
    font-size: 40rpx;
    line-height: 1;
    opacity: 0.6;
    transition: all $uni-md-animation-normal ease;
    color: $uni-md-text-secondary;
  }

  .nav-text {
    font-size: 22rpx;
    color: $uni-md-text-secondary;
    transition: all $uni-md-animation-normal ease;
  }

  .nav-indicator {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 4rpx;
    height: 4rpx;
    border-radius: 50%;
    background-color: $uni-md-color-primary;
    box-shadow: 0 0 8rpx $uni-md-color-primary;
    animation: pulse $uni-md-animation-normal ease-in-out;
  }

  @keyframes pulse {
    0% {
      transform: translateX(-50%) scale(0.8);
      opacity: 0.8;
    }
    50% {
      transform: translateX(-50%) scale(1.2);
      opacity: 1;
    }
    100% {
      transform: translateX(-50%) scale(1);
      opacity: 1;
    }
  }
</style>