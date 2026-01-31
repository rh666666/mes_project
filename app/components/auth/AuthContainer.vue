<template>
  <view class="auth-container">
    <view class="auth-card">
      <slot></slot>
    </view>
  </view>
</template>

<script>
export default {
  name: 'AuthContainer'
}
</script>

<style lang="scss">
.auth-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $uni-md-space-md;
  min-height: calc(100vh - 200rpx - env(safe-area-inset-bottom));
}

.auth-card {
  width: 100%;
  max-width: 480px;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-large;
  box-shadow: $uni-md-shadow-md;
  padding: $uni-md-space-2xl;
}

@media (max-width: 768px) {
  .auth-container {
    padding: $uni-md-space-sm;
    align-items: flex-start;
    padding-top: 60rpx;
  }

  .auth-card {
    padding: $uni-md-space-xl;
    border-radius: $uni-md-radius-medium;
  }
}
</style>
