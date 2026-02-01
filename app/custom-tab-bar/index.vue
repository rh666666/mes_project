<template>
  <view class="tab-bar">
    <view 
      class="tab-bar-item" 
      v-for="(item, index) in list" 
      :key="index"
      :class="{ active: selected === index }"
      @click="switchTab(index, item)"
    >
      <view class="tab-icon-wrapper">
        <text class="tab-icon">{{ item.icon }}</text>
      </view>
      <text class="tab-text">{{ item.text }}</text>
      <view class="tab-indicator" v-if="selected === index"></view>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
        selected: 0,
        list: [
          {
            pagePath: '/pages/index/index',
            text: '首页',
            icon: '首'
          },
          {
            pagePath: '/pages/production/index',
            text: '生产',
            icon: '产'
          },
          {
            pagePath: '/pages/equipment/index',
            text: '设备',
            icon: '设'
          },
          {
            pagePath: '/pages/profile/index',
            text: '我的',
            icon: '我'
          }
        ]
      };
    },
    methods: {
      switchTab(index, item) {
        if (this.selected === index) {
          return;
        }
        this.selected = index;
        uni.switchTab({
          url: item.pagePath
        });
      }
    }
  };
</script>

<style lang="scss">
  .tab-bar {
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

  .tab-bar-item {
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
      .tab-icon {
        transform: translateY(-4rpx);
        color: $uni-md-color-primary;
        opacity: 1;
      }

      .tab-text {
        color: $uni-md-color-primary;
        font-weight: 500;
      }
    }
  }

  .tab-icon-wrapper {
    margin-bottom: 4rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .tab-icon {
    font-size: 40rpx;
    line-height: 1;
    opacity: 0.6;
    transition: all $uni-md-animation-normal ease;
    color: $uni-md-text-secondary;
  }

  .tab-text {
    font-size: 22rpx;
    color: $uni-md-text-secondary;
    transition: all $uni-md-animation-normal ease;
  }

  .tab-indicator {
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
