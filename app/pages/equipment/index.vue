<template>
  <view class="page">
    <view class="placeholder-content">
      <text class="placeholder-desc">页面开发中...</text>
    </view>
  </view>
</template>

<script>
  export default {
    data() {
      return {
      };
    },
    onLoad() {},
    methods: {
    }
  };
</script>

<style lang="scss">
  .page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: $uni-bg-color-grey;
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
