<template>
  <view class="page">
    <view class="placeholder-content">
      <text class="placeholder-desc">页面开发中...</text>
    </view>
    <BottomNavBar :current-path="currentPath" @nav-change="onNavChange"></BottomNavBar>
  </view>
</template>

<script>
  import BottomNavBar from '@/components/BottomNavBar.vue';

  export default {
    components: {
      BottomNavBar
    },
    data() {
      return {
        currentPath: '/pages/equipment/index'
      };
    },
    onLoad() {},
    methods: {
      onNavChange(item) {
        console.log('导航切换到:', item);
      }
    }
  };
</script>

<style lang="scss">
  .page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: $uni-bg-color-grey;
    padding-bottom: calc(100rpx + env(safe-area-inset-bottom));
    box-sizing: border-box;
  }

  .placeholder-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40rpx;
  }

  .placeholder-desc {
    font-size: 28rpx;
    color: $uni-text-color-grey;
  }
</style>