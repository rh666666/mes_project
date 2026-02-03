<template>
  <view
    class="md3-divider"
    :class="{
      'is-inset': inset,
      'is-inset-start': insetStart,
      'is-inset-end': insetEnd
    }"
    :role="role"
  />
</template>

<script>
/**
 * Material Design 3 Divider 组件
 * @component
 * @description 列表分割线组件，支持全宽和缩进样式
 */
export default {
  name: 'Divider',

  props: {
    /** @type {boolean} 是否两侧缩进 */
    inset: {
      type: Boolean,
      default: false
    },
    /** @type {boolean} 是否起始侧缩进 */
    insetStart: {
      type: Boolean,
      default: false
    },
    /** @type {boolean} 是否结束侧缩进 */
    insetEnd: {
      type: Boolean,
      default: false
    },
    /** @type {string} 无障碍角色， decorative 为装饰性不播报 */
    role: {
      type: String,
      default: 'separator'
    }
  }
}
</script>

<style lang="scss">
.md3-divider {
  height: 1px;
  background-color: $uni-md-divider;

  // 默认全宽
  margin: 0;

  // 两侧缩进
  &.is-inset {
    margin: 0 $uni-md-space-lg;
  }

  // 起始侧缩进
  &.is-inset-start {
    margin-left: $uni-md-space-lg;
  }

  // 结束侧缩进
  &.is-inset-end {
    margin-right: $uni-md-space-lg;
  }
}
</style>
