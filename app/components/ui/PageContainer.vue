<template>
  <view class="page-container" :class="[{ 'has-padding': padding }]">
    <slot />
  </view>
</template>

<script setup lang="ts">
/**
 * 页面容器组件
 * 提供统一的页面布局和背景样式
 */

interface Props {
  /** 是否添加默认内边距 */
  padding?: boolean
}

withDefaults(defineProps<Props>(), {
  padding: true
})
</script>

<style lang="scss" scoped>
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: $uni-md-background;
  box-sizing: border-box;

  &.has-padding {
    padding: $uni-md-space-md;
  }
}
</style>
