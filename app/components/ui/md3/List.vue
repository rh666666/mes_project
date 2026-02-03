<template>
  <view class="md3-list" role="list">
    <slot />
  </view>
</template>

<script>
/**
 * Material Design 3 List 组件
 * @component
 * @description 列表容器，用于包裹 ListItem 组件
 */
export default {
  name: 'List'
}
</script>

<style lang="scss">
.md3-list {
  display: flex;
  flex-direction: column;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-medium;
  overflow: hidden;
}
</style>
