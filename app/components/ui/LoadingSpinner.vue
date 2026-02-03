<template>
  <view
    class="loading-spinner"
    :class="[`size-${size}`, `color-${color}`]"
    :style="customStyle"
  />
</template>

<script setup lang="ts">
/**
 * 加载动画组件
 * 提供统一的加载动画样式
 */

import { computed } from 'vue'

type SpinnerSize = 'small' | 'medium' | 'large'
type SpinnerColor = 'white' | 'primary' | 'grey'

interface Props {
  /** 尺寸大小 */
  size?: SpinnerSize
  /** 颜色主题 */
  color?: SpinnerColor
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  color: 'primary'
})

/**
 * 计算自定义样式
 * @returns 样式对象
 */
const customStyle = computed(() => {
  const sizeMap = {
    small: { width: '32rpx', height: '32rpx', borderWidth: '4rpx' },
    medium: { width: '48rpx', height: '48rpx', borderWidth: '6rpx' },
    large: { width: '64rpx', height: '64rpx', borderWidth: '8rpx' }
  }

  const sizeValue = sizeMap[props.size]
  return {
    width: sizeValue.width,
    height: sizeValue.height,
    borderWidth: sizeValue.borderWidth
  }
})
</script>

<style lang="scss" scoped>
.loading-spinner {
  border-style: solid;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  box-sizing: border-box;

  &.color-white {
    border-color: rgba(255, 255, 255, 0.3);
    border-top-color: white;
  }

  &.color-primary {
    border-color: rgba(25, 118, 210, 0.3);
    border-top-color: $uni-md-color-primary;
  }

  &.color-grey {
    border-color: rgba(199, 199, 204, 0.3);
    border-top-color: $uni-md-text-disabled;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
