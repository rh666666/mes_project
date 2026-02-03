<template>
  <button
    :class="['submit-button', { 'is-loading': loading, 'is-disabled': disabled }]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <LoadingSpinner v-if="loading" size="small" color="white" />
    <text v-else class="button-text">{{ text }}</text>
  </button>
</template>

<script setup lang="ts">
/**
 * 提交按钮组件
 * 提供统一的提交按钮样式，支持加载状态
 */

import LoadingSpinner from './LoadingSpinner.vue'

interface Props {
  /** 按钮文本 */
  text: string
  /** 是否处于加载状态 */
  loading?: boolean
  /** 是否禁用 */
  disabled?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false
})

const emit = defineEmits<Emits>()

/**
 * 处理点击事件
 * @param event 点击事件
 */
const handleClick = (event: MouseEvent): void => {
  emit('click', event)
}
</script>

<style lang="scss" scoped>
.submit-button {
  width: 100%;
  height: 96rpx;
  background-color: $uni-md-color-primary;
  border-radius: $uni-md-radius-medium;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  box-shadow: $uni-md-shadow-sm;
  transition: all $uni-md-animation-normal ease;

  &:active:not(:disabled) {
    transform: scale(0.98);
    box-shadow: $uni-md-shadow-sm;
  }

  &.is-disabled {
    background-color: $uni-md-text-disabled;
    cursor: not-allowed;
  }

  &.is-loading {
    cursor: not-allowed;
  }
}

.button-text {
  color: white;
  font-size: $uni-font-size-lg;
  font-weight: 500;
}
</style>
