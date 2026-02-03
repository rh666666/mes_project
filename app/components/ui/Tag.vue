<template>
  <view
    class="tag"
    :class="[`variant-${variant}`, `size-${size}`]"
    :style="customStyle"
  >
    <text class="tag-text">{{ text }}</text>
  </view>
</template>

<script setup lang="ts">
/**
 * 标签组件
 * 用于展示状态、分类、角色等标签信息
 */

import { computed } from 'vue'

type TagVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info'
type TagSize = 'small' | 'medium' | 'large'

interface Props {
  /** 标签文本 */
  text: string
  /** 样式变体 */
  variant?: TagVariant
  /** 尺寸 */
  size?: TagSize
  /** 自定义背景色 */
  bgColor?: string
  /** 自定义文字颜色 */
  textColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'medium',
  bgColor: '',
  textColor: ''
})

/**
 * 自定义样式
 */
const customStyle = computed(() => {
  const style: Record<string, string> = {}
  if (props.bgColor) {
    style.backgroundColor = props.bgColor
  }
  if (props.textColor) {
    style.color = props.textColor
  }
  return style
})
</script>

<style lang="scss" scoped>
.tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: $uni-md-radius-small;
  font-weight: 500;

  // 尺寸变体
  &.size-small {
    padding: 2rpx 10rpx;
    font-size: 20rpx;
  }

  &.size-medium {
    padding: 4rpx 16rpx;
    font-size: $uni-font-size-sm;
  }

  &.size-large {
    padding: 6rpx 20rpx;
    font-size: $uni-font-size-base;
  }

  // 颜色变体
  &.variant-default {
    background-color: $uni-md-surface-variant;
    color: $uni-md-text-secondary;
  }

  &.variant-primary {
    background-color: rgba($uni-md-color-primary, 0.1);
    color: $uni-md-color-primary;
  }

  &.variant-success {
    background-color: rgba($uni-color-success, 0.1);
    color: $uni-color-success;
  }

  &.variant-warning {
    background-color: rgba($uni-color-warning, 0.1);
    color: $uni-color-warning;
  }

  &.variant-error {
    background-color: rgba($uni-color-error, 0.1);
    color: $uni-color-error;
  }

  &.variant-info {
    background-color: rgba($uni-md-text-tertiary, 0.1);
    color: $uni-md-text-tertiary;
  }
}

.tag-text {
  line-height: 1;
}
</style>
